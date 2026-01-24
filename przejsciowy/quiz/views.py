import os
import re
import pdfplumber
from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from .models import Users
from .services import QuestionGenerator
import json

def main_menu_view(request):
    if 'user_id' not in request.session:
        return redirect('quiz:login')
    logged_in_username = request.session.get('username')
    first_name = logged_in_username.split(' ')[0] if logged_in_username else 'Użytkowniku'
    context = {
        'username': logged_in_username,
        'first_name': first_name,
        'user_mail': request.session.get('mail', 'brak@adresu.pl')
    }
    return render(request, 'quiz/main_menu.html', context)

def start_quiz_view(request):
    return render(request, 'quiz/start_quiz.html')

def my_notes_view(request):
    return render(request, 'quiz/my_notes.html')

def my_quizzes_view(request):
    return render(request, 'quiz/my_quizzes.html')

def multiplayer_view(request):
    return render(request, 'quiz/multiplayer.html')

def statistics_view(request):
    return render(request, 'quiz/statistics.html')

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
        #TODO - zapisywanie pytań do bazy - na razie jest tylko print z tego co jest
        print("\n" + "="*50)
        print(f"DEBUG: OTRZYMANO QUIZ: {quiz_name}")
        print(f"LICZBA PYTAŃ: {len(parsed_data)}")
        print("STRUKTURA DANYCH:")
        print(json.dumps(parsed_data, indent=4, ensure_ascii=False))
        print("="*50 + "\n")
        
        return redirect('/my-quizzes/')

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