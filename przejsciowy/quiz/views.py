from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from .models import Users
from django.contrib.auth.hashers import make_password, check_password

def main_menu_view(request):
    """Renders the main menu page."""
    if 'user_id' not in request.session:
        return redirect('quiz:login')
    logged_in_username = request.session.get('username')
    first_name = logged_in_username.split(' ')[0] if logged_in_username else 'Użytkowniku'
    context = {
        'username': logged_in_username,
        'first_name': first_name,
        'user_mail': request.session.get('mail', 'brak@adresu.pl')  # Jeśli mail jest zapisywany w sesji
    }

    return render(request, 'quiz/main_menu.html', context)

def start_quiz_view(request):
    """Renders the start quiz page."""
    return render(request, 'quiz/start_quiz.html')

def my_notes_view(request):
    """Renders the my notes page."""
    return render(request, 'quiz/my_notes.html')

def my_quizzes_view(request):
    """Renders the my quizzes page."""
    return render(request, 'quiz/my_quizzes.html')

def multiplayer_view(request):
    """Renders the multiplayer page."""
    return render(request, 'quiz/multiplayer.html')

def statistics_view(request):
    """Renders the statistics page."""
    return render(request, 'quiz/statistics.html')

def upload_pdf_view(request):
    """Handles PDF upload and text extraction."""
    # This view will now just render the page, 
    # the form submission logic can be handled by another view or kept here
    # but for now we just render the page to make it accessible
    return render(request, 'quiz/upload_pdf.html')


def login_view(request):
    if 'user_id' in request.session:
        return redirect('quiz:main_menu')

    error_message = None

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user_instance = Users.objects.get(username=username)

            # Użycie check_password() do porównania podanego hasła z hashem w bazie
            if check_password(password, user_instance.password):  # <-- KLUCZOWA ZMIANA

                request.session['user_id'] = user_instance.id
                request.session['username'] = user_instance.username
                request.session['role'] = user_instance.role
                request.session['mail'] = user_instance.mail  # Dodano dla wyświetlania w base.html

                return redirect('quiz:main_menu')
            else:
                error_message = "Nieprawidłowa nazwa użytkownika lub hasło."

        except Users.DoesNotExist:
            error_message = "Nieprawidłowa nazwa użytkownika lub hasło."
        except Exception as e:
            print(f"Błąd logowania: {e}")
            error_message = "Wystąpił nieoczekiwany błąd serwera."

    return render(request, 'quiz/login.html', {'error_message': error_message})


from django.shortcuts import redirect


def logout_view(request):
    keys_to_clear = ['user_id', 'username', 'role', 'mail']

    for key in keys_to_clear:
        request.session.pop(key, None)

    return redirect('quiz:login')


def register_view(request):
    if 'user_id' in request.session:
        return redirect('quiz:main_menu')

    error_message = None

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('mail')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        role = 'user'

        if password != password_confirm:
            error_message = "Hasła nie są identyczne."
        elif Users.objects.filter(username=username).exists():
            error_message = "Użytkownik o tej nazwie już istnieje."
        elif Users.objects.filter(mail=email).exists():
            error_message = "Ten adres e-mail jest już zajęty."
        else:
            try:
                hashed_password = make_password(password)

                new_user = Users.objects.create(
                    username=username,
                    password=hashed_password,  # <-- ZAPIS SHASZOWANEGO HASŁA
                    mail=email,
                    role=role
                )
                new_user.save()

                request.session['user_id'] = new_user.id
                request.session['username'] = new_user.username
                request.session['role'] = new_user.role
                request.session['mail'] = new_user.mail  # <-- ZAPIS MAIL DO SESJI

                return redirect('quiz:main_menu')

            except Exception as e:
                print(f"Błąd rejestracji w bazie: {e}")
                error_message = "Wystąpił błąd podczas zapisywania danych."

    return render(request, 'quiz/register.html', {'error_message': error_message})