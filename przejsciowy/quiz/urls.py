from django.urls import path
from . import views

app_name = 'quiz'

urlpatterns = [
    path('', views.main_menu_view, name='main_menu'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('settings/', views.settings_view, name='settings'),
    path('start-quiz/', views.start_quiz_view, name='start_quiz'),
    path('my-notes/', views.my_notes_view, name='my_notes'),
    path('my-notes/upload/', views.upload_pdf_view, name='upload_pdf_view'),
    path('my-quizzes/', views.my_quizzes_view, name='my_quizzes'),
    path('quiz-attempt/<int:attempt_id>/', views.quiz_attempt_view, name='quiz_attempt'),
    path('quiz-results/<int:attempt_id>/', views.quiz_results_view, name='quiz_results'),
    path('quiz-review/<int:attempt_id>/', views.quiz_review_view, name='quiz_review'),
    path('multiplayer/', views.multiplayer_view, name='multiplayer'),
    path('statistics/', views.statistics_view, name='statistics'),
    path('review-questions/', views.review_questions_view, name='review_questions_view'),
]