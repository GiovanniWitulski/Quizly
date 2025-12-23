from django.urls import path
from .views import CreateQuizView, QuizListView, QuizDetailView

urlpatterns = [
    path('createQuiz/', CreateQuizView.as_view(), name='create_quiz'),
    path('quizzes/', QuizListView.as_view(), name='quiz_list'),
    path('quizzes/<int:pk>/', QuizDetailView.as_view(), name='quiz_detail'),
]