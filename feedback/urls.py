from django.urls import path
from . import views
app_name = 'feedback'
urlpatterns = [
    path('course/<slug:course_slug>/', views.give_feedback,        name='give'),
    path('my-feedback/',              views.teacher_feedback_view, name='teacher_view'),
]
