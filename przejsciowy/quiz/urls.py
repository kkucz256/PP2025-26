from django.urls import path
from . import views

app_name = 'quiz'

urlpatterns = [
    path('', views.main_menu_view, name='main_menu'),
    path('start-quiz/', views.start_quiz_view, name='start_quiz'),
    path('my-notes/', views.my_notes_view, name='my_notes'),
    path('my-notes/upload/', views.upload_pdf_view, name='upload_pdf_view'),
    path('my-quizzes/', views.my_quizzes_view, name='my_quizzes'),
    path('multiplayer/', views.multiplayer_view, name='multiplayer'),
    path('statistics/', views.statistics_view, name='statistics'),
]