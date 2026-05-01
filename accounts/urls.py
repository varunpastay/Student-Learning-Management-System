from django.urls import path
from . import views
app_name = 'accounts'
urlpatterns = [
    path('register/student/', views.register_student,  name='register_student'),
    path('register/teacher/', views.register_teacher,  name='register_teacher'),
    path('login/',            views.user_login,         name='login'),
    path('logout/',           views.user_logout,        name='logout'),
    path('profile/',          views.profile,            name='profile'),
    path('password/',         views.change_password,    name='change_password'),
]
