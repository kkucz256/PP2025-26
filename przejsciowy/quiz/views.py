from django.shortcuts import render
from django.views.generic import TemplateView

def main_menu_view(request):
    """Renders the main menu page."""
    return render(request, 'quiz/main_menu.html')

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