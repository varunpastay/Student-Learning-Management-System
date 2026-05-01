from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('',             views.home,               name='home'),
    path('student/',     views.student_dashboard,  name='student_dashboard'),
    path('teacher/',     views.teacher_dashboard,  name='teacher_dashboard'),
    path('admin/',       views.admin_dashboard,    name='admin_dashboard'),
    path('leaderboard/', views.leaderboard,        name='leaderboard'),
]
