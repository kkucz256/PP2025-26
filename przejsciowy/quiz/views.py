from django.db.models import Avg, Q, F, ExpressionWrapper, DurationField
from django.utils import timezone
from datetime import timedelta
import os
import re
import pdfplumber
from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from .models import Users, Quiz, QuizAttempt, Question, Answers, QuizUser
from .services import QuestionGenerator
import json

def main_menu_view(request):
    if 'user_id' not in request.session:
        return redirect('quiz:login')
    logged_in_username = request.session.get('username')
    first_name = logged_in_username.split(' ')[0] if logged_in_username else 'Użytkowniku'
    
    user_id = request.session.get('user_id')
    
    # Pobierz statystyki
    completed_attempts = QuizAttempt.objects.filter(
        user_id=user_id,
        end_date__isnull=False
    )
    
    total_quizzes = Quiz.objects.filter(quiz_users__user_id=user_id).count()
    completed_quizzes = completed_attempts.values('quiz').distinct().count()
    
    # Średni wynik
    if completed_attempts.exists():
        total_correct = sum(a.correct or 0 for a in completed_attempts)
        total_questions = sum(
            a.quiz.questions.count() for a in completed_attempts
        )
        avg_percentage = round(
            (total_correct / total_questions * 100) if total_questions > 0 else 0, 1
        )
    else:
        avg_percentage = 0
    
    # Liczba dni nauki
    if completed_attempts.exists():
        learning_days = completed_attempts.values(
            'start_date__date'
        ).distinct().count()
    else:
        learning_days = 0
    
    context = {
        'username': logged_in_username,
        'first_name': first_name,
        'user_mail': request.session.get('mail', 'brak@adresu.pl'),
        'total_quizzes': total_quizzes,
        'completed_quizzes': completed_quizzes,
        'completed_attempts': completed_attempts.count(),
        'avg_percentage': avg_percentage,
        'learning_days': learning_days,
        'recent_attempts': completed_attempts.order_by('-start_date')[:5]
    }
    return render(request, 'quiz/main_menu.html', context)

def start_quiz_view(request):
    return render(request, 'quiz/start_quiz.html')

def my_notes_view(request):
    return render(request, 'quiz/my_notes.html')

def my_quizzes_view(request):
    return render(request, 'quiz/my_quizzes.html')

def quiz_attempt_view(request, attempt_id):
    """Wyświetl quiz do rozwiązania"""
    if 'user_id' not in request.session:
        return redirect('quiz:login')
    
    try:
        attempt = QuizAttempt.objects.get(id=attempt_id)
    except QuizAttempt.DoesNotExist:
        return redirect('quiz:my_quizzes')
    
    # Sprawdzenie czy użytkownik jest właścicielem attempt'u
    if attempt.user_id != request.session.get('user_id'):
        return redirect('quiz:my_quizzes')
    
    quiz = attempt.quiz
    questions = quiz.questions.all().order_by('position')
    
    context = {
        'attempt_id': attempt_id,
        'quiz': quiz,
        'questions': questions,
        'total_questions': questions.count(),
    }
    
    return render(request, 'quiz/quiz_attempt.html', context)

def quiz_results_view(request, attempt_id):
    """Wyświetl wyniki quizu"""
    if 'user_id' not in request.session:
        return redirect('quiz:login')
    
    try:
        attempt = QuizAttempt.objects.get(id=attempt_id)
    except QuizAttempt.DoesNotExist:
        return redirect('quiz:my_quizzes')
    
    # Sprawdzenie czy użytkownik jest właścicielem attempt'u
    if attempt.user_id != request.session.get('user_id'):
        return redirect('quiz:my_quizzes')
    
    quiz = attempt.quiz
    total_questions = attempt.quiz.questions.count()
    correct_answers = attempt.correct or 0
    incorrect_answers = attempt.incorrect or 0
    
    # Wylicz procent
    if total_questions > 0:
        percentage = round((correct_answers / total_questions) * 100, 2)
    else:
        percentage = 0
    
    context = {
        'attempt': attempt,
        'quiz': quiz,
        'correct_answers': correct_answers,
        'is_submitted': attempt.end_date is not None,
        'incorrect_answers': incorrect_answers,
        'total_questions': total_questions,
        'percentage': percentage,
    }
    
    return render(request, 'quiz/quiz_results.html', context)

def quiz_review_view(request, attempt_id):
    """Wyświetl podsumowanie quizu z poprawnymi odpowiedziami"""
    if 'user_id' not in request.session:
        return redirect('quiz:login')
    
    try:
        attempt = QuizAttempt.objects.get(id=attempt_id)
    except QuizAttempt.DoesNotExist:
        return redirect('quiz:my_quizzes')
    
    # Sprawdzenie czy użytkownik jest właścicielem attempt'u
    if attempt.user_id != request.session.get('user_id'):
        return redirect('quiz:my_quizzes')
    
    quiz = attempt.quiz
    questions = quiz.questions.all().order_by('position')
    
    context = {
        'attempt': attempt,
        'quiz': quiz,
        'questions': questions,
        'total_questions': questions.count(),
    }
    
    return render(request, 'quiz/quiz_review.html', context)

def multiplayer_view(request):
    return render(request, 'quiz/multiplayer.html')

def statistics_view(request):
    """Wyświetl statystyki quizów"""
    if 'user_id' not in request.session:
        return redirect('quiz:login')
    
    user_id = request.session.get('user_id')
    
    # Pobierz wszystkie quizy użytkownika
    user_quizzes = Quiz.objects.filter(quiz_users__user_id=user_id).distinct()
    
    quizzes_stats = []
    
    for quiz in user_quizzes:
        # Tylko podejścia z datą zakończenia
        completed_attempts = quiz.attempts.filter(end_date__isnull=False)
        
        if completed_attempts.count() == 0:
            continue
        
        # Statystyki dla wszystkich użytkowników
        all_stats = completed_attempts.aggregate(
            avg_score=Avg('correct'),
            avg_incorrect=Avg('incorrect'),
            count=Avg('id')  # Dummy do zliczenia
        )
        
        # Oblicz średni wynik w procentach
        total_questions = quiz.questions.count()
        avg_correct = all_stats['avg_score'] or 0
        
        if total_questions > 0:
            avg_percentage_all = round((avg_correct / total_questions) * 100, 2)
        else:
            avg_percentage_all = 0
        
        # Średni czas ukończenia
        avg_duration_all = 0
        durations = []
        for attempt in completed_attempts:
            if attempt.end_date and attempt.start_date:
                duration = (attempt.end_date - attempt.start_date).total_seconds() / 60
                durations.append(duration)
        if durations:
            avg_duration_all = round(sum(durations) / len(durations), 1)
        
        # Statystyki dla zalogowanego użytkownika
        user_attempts = completed_attempts.filter(user_id=user_id)
        
        user_avg_score = 0
        user_avg_percentage = 0
        user_avg_duration = 0
        user_best_duration = None
        user_attempts_count = user_attempts.count()
        
        if user_attempts_count > 0:
            user_stats = user_attempts.aggregate(
                avg_score=Avg('correct'),
            )
            user_avg_score = user_stats['avg_score'] or 0
            
            if total_questions > 0:
                user_avg_percentage = round((user_avg_score / total_questions) * 100, 2)
            
            # Średni czas dla użytkownika
            user_durations = []
            for attempt in user_attempts:
                if attempt.end_date and attempt.start_date:
                    duration = (attempt.end_date - attempt.start_date).total_seconds() / 60
                    user_durations.append(duration)
            
            if user_durations:
                user_avg_duration = round(sum(user_durations) / len(user_durations), 1)
                user_best_duration = round(min(user_durations), 1)
        
        quizzes_stats.append({
            'id': quiz.id,
            'name': quiz.content,
            'total_questions': total_questions,
            'user_attempts': user_attempts_count,
            'all_attempts': completed_attempts.count(),
            'user_avg_score': round(user_avg_score, 1),
            'user_avg_percentage': user_avg_percentage,
            'user_avg_duration': user_avg_duration,
            'user_best_duration': user_best_duration,
            'all_avg_percentage': avg_percentage_all,
            'all_avg_duration': avg_duration_all,
        })
    
    context = {
        'quizzes_stats': quizzes_stats,
    }
    
    return render(request, 'quiz/statistics.html', context)

def upload_pdf_view(request):
    context = {}
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'extract':
            if 'pdf_file' not in request.FILES:
                context['error'] = "Nie wybrano pliku."
                return render(request, "quiz/upload_pdf.html", context)

            uploaded_file = request.FILES['pdf_file']
            if not uploaded_file.name.endswith('.pdf'):
                context['error'] = "To nie jest plik PDF."
                return render(request, "quiz/upload_pdf.html", context)

            try:
                fs = FileSystemStorage()
                old_filename = request.session.get('last_uploaded_pdf')
                if old_filename:
                    old_file_path = os.path.join(settings.MEDIA_ROOT, old_filename)
                    if os.path.exists(old_file_path):
                        os.remove(old_file_path)

                filename = fs.save(uploaded_file.name, uploaded_file)
                file_url = fs.url(filename)
                request.session['last_uploaded_pdf'] = filename
                
                context['file_url'] = file_url
                context['filename'] = filename

                extracted_text = ""
                with pdfplumber.open(uploaded_file) as pdf:
                    for page in pdf.pages:
                        text = page.extract_text(x_tolerance=1, y_tolerance=3)
                        if text:
                            extracted_text += text.replace('\r', '').replace('-\n', '').replace('\n', ' ') + " "
                
                context['extracted_text'] = re.sub(r'\s+', ' ', extracted_text).strip()
                if not context['extracted_text']:
                    context['error'] = "Nie udało się odczytać tekstu."
            except Exception as e:
                context['error'] = f"Błąd: {str(e)}"

        elif action == 'generate':
            final_text = request.POST.get('final_text')
            filename_to_delete = request.POST.get('filename_to_delete')
            count = request.POST.get('question_count', 25)
            model_type = request.POST.get('model_choice', 'azure')
            # Można zmienić model_type na 'deepseek' aby użyć lokalnego modelu DeepSeek-r1

            if not final_text:
                context['error'] = "Pole tekstowe jest puste."
            else:
                questions = QuestionGenerator.generate(final_text, count, model_type)
                if questions:
                    request.session['temp_questions'] = questions
                    if filename_to_delete:
                        path = os.path.join(settings.MEDIA_ROOT, filename_to_delete)
                        if os.path.exists(path): os.remove(path)
                    return redirect('quiz:review_questions_view')
                context['error'] = "AI zawiodło przy generowaniu pytań."

    return render(request, "quiz/upload_pdf.html", context)

def review_questions_view(request):
    questions = request.session.get('temp_questions', [])
    
    # DEBUG
    print("\n" + "="*60)
    print("DEBUG review_questions_view:")
    print(f"  - temp_questions w sesji: {questions is not None}")
    print(f"  - Liczba pytań: {len(questions) if questions else 0}")
    if questions:
        print(f"  - Pierwsze pytanie: {questions[0] if questions else 'BRAK'}")
    print("="*60 + "\n")
    
    if request.method == 'POST':
        quiz_name = request.POST.get('quiz_name')
        parsed_data = {}
        
        for key in request.POST:
            if key.endswith('_text'):
                prefix = key.replace('_text', '')
                
                parsed_data[prefix] = {
                    'text': request.POST.get(key),
                    'correct': request.POST.get(f'{prefix}_correct'),
                    'options': [
                        request.POST.get(f'{prefix}_opt_0'),
                        request.POST.get(f'{prefix}_opt_1'),
                        request.POST.get(f'{prefix}_opt_2'),
                        request.POST.get(f'{prefix}_opt_3'),
                    ]
                }
        
        # Zapisz quiz do bazy
        if quiz_name and parsed_data:
            try:
                # Sprawdź czy quiz z taką nazwą już istnieje
                slug = quiz_name.lower().replace(' ', '-').replace('ł', 'l').replace('ą', 'a').replace('ć', 'c').replace('ę', 'e').replace('ń', 'n').replace('ó', 'o').replace('ś', 's').replace('ź', 'z').replace('ż', 'z')
                slug = re.sub(r'[^a-z0-9\-]', '', slug)
                
                # Upewnij się że slug jest unikalny
                counter = 1
                original_slug = slug
                while Quiz.objects.filter(slug=slug).exists():
                    slug = f"{original_slug}-{counter}"
                    counter += 1
                
                # Utwórz quiz
                quiz = Quiz.objects.create(content=quiz_name, slug=slug)
                
                # Utwórz użytkownika do quizu jeśli zalogowany
                user_id = request.session.get('user_id')
                if user_id:
                    try:
                        user = Users.objects.get(id=user_id)
                        QuizUser.objects.create(quiz=quiz, user=user)
                    except Users.DoesNotExist:
                        pass
                
                # Dodaj pytania
                position = 1
                for prefix in sorted(parsed_data.keys(), key=lambda x: int(x.replace('q', '')) if x.startswith('q') else 0):
                    q_data = parsed_data[prefix]
                    question_text = q_data['text']
                    correct_idx = int(q_data['correct']) if q_data['correct'] else 0
                    options = [opt for opt in q_data['options'] if opt]  # Usuń puste opcje
                    
                    # Utwórz pytanie
                    question = Question.objects.create(
                        quiz=quiz,
                        content=question_text,
                        position=position
                    )
                    position += 1
                    
                    # Utwórz odpowiedzi
                    for opt_idx, option_text in enumerate(options):
                        is_correct = (opt_idx == int(correct_idx))
                        Answers.objects.create(
                            question=question,
                            content=option_text,
                            is_correct=is_correct
                        )
                
                # Wyczyść sesję
                request.session.pop('temp_questions', None)
                
                print("\n" + "="*50)
                print(f"DEBUG: QUIZ ZAPISANY: {quiz_name} (ID: {quiz.id})")
                print(f"LICZBA PYTAŃ: {len(parsed_data)}")
                print("="*50 + "\n")
                
            except Exception as e:
                print(f"BŁĄD PRZY ZAPISYWANIU QUIZU: {str(e)}")
                import traceback
                traceback.print_exc()
        
        return redirect('quiz:my_quizzes')

    # Przekaż pytania jako JSON do template'u
    questions_json = json.dumps(questions)
    return render(request, 'quiz/review_questions.html', {
        'questions': questions,
        'questions_json': questions_json
    })

def login_view(request):
    if 'user_id' in request.session:
        return redirect('quiz:main_menu')
    error_message = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = Users.objects.get(username=username)
            if check_password(password, user.password):
                request.session['user_id'] = user.id
                request.session['username'] = user.username
                request.session['role'] = user.role
                request.session['mail'] = user.mail
                return redirect('quiz:main_menu')
            error_message = "Błędne dane logowania."
        except Users.DoesNotExist:
            error_message = "Błędne dane logowania."
    return render(request, 'quiz/login.html', {'error_message': error_message})

def register_view(request):
    if 'user_id' in request.session:
        return redirect('quiz:main_menu')
    error_message = None
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('mail')
        password = request.POST.get('password')
        if password != request.POST.get('password_confirm'):
            error_message = "Hasła nie są identyczne."
        elif Users.objects.filter(username=username).exists():
            error_message = "Nazwa zajęta."
        else:
            user = Users.objects.create(username=username, password=make_password(password), mail=email, role='user')
            request.session['user_id'] = user.id
            request.session['username'] = user.username
            return redirect('quiz:main_menu')
    return render(request, 'quiz/register.html', {'error_message': error_message})

def logout_view(request):
    request.session.flush()
    return redirect('quiz:login')

def settings_view(request):
    if 'user_id' not in request.session:
        return redirect('quiz:login')
    
    user_id = request.session.get('user_id')
    user = Users.objects.get(id=user_id)
    error_message = None
    success_message = None
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        # Zmiana nazwy użytkownika
        if action == 'change_username':
            new_username = request.POST.get('new_username', '').strip()
            
            if not new_username:
                error_message = 'Nazwa użytkownika nie może być pusta'
            elif len(new_username) < 3:
                error_message = 'Nazwa użytkownika musi mieć co najmniej 3 znaki'
            elif Users.objects.filter(username=new_username).exclude(id=user_id).exists():
                error_message = 'Użytkownik z taką nazwą już istnieje'
            else:
                user.username = new_username
                user.save()
                request.session['username'] = new_username
                success_message = 'Nazwa użytkownika zmieniona pomyślnie'
        
        # Zmiana adresu email
        elif action == 'change_email':
            new_email = request.POST.get('new_email', '').strip()
            
            if not new_email or '@' not in new_email:
                error_message = 'Podaj prawidłowy adres email'
            elif Users.objects.filter(mail=new_email).exclude(id=user_id).exists():
                error_message = 'Email już jest zarejestrowany'
            else:
                user.mail = new_email
                user.save()
                request.session['mail'] = new_email
                success_message = 'Adres email zmieniony pomyślnie'
        
        # Zmiana hasła
        elif action == 'change_password':
            old_password = request.POST.get('old_password', '')
            new_password = request.POST.get('new_password', '')
            confirm_password = request.POST.get('confirm_password', '')
            
            if not check_password(old_password, user.password):
                error_message = 'Obecne hasło jest nieprawidłowe'
            elif len(new_password) < 6:
                error_message = 'Nowe hasło musi mieć co najmniej 6 znaków'
            elif new_password != confirm_password:
                error_message = 'Hasła nie zgadzają się'
            else:
                user.password = make_password(new_password)
                user.save()
                success_message = 'Hasło zmienione pomyślnie'
    
    context = {
        'user': user,
        'error_message': error_message,
        'success_message': success_message,
    }
    return render(request, 'quiz/settings.html', context)