"""courses/urls.py"""
from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('',                    views.course_list,   name='list'),
    path('create/',             views.course_create, name='create'),
    path('<slug:slug>/',        views.course_detail, name='detail'),
    path('<slug:slug>/edit/',   views.course_edit,   name='edit'),
    path('<slug:slug>/delete/', views.course_delete, name='delete'),
    path('<slug:slug>/enroll/', views.enroll_course, name='enroll'),
    path('<slug:slug>/unenroll/', views.unenroll_course, name='unenroll'),
    path('<slug:slug>/material/add/', views.add_material, name='add_material'),
]
