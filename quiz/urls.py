from django.urls import path
from . import views
app_name = 'quiz'
urlpatterns = [
    path('',                         views.quiz_list,    name='list'),
    path('create/',                  views.quiz_create,  name='create'),
    path('<int:quiz_id>/',            views.quiz_detail,  name='detail'),
    path('<int:quiz_id>/take/',       views.take_quiz,    name='take'),
    path('<int:quiz_id>/result/',     views.quiz_result,  name='result'),
    path('<int:quiz_id>/question/',   views.add_question, name='add_question'),
]
