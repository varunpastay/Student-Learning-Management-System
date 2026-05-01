from django.contrib import admin
from .models import TeacherFeedback

@admin.register(TeacherFeedback)
class TeacherFeedbackAdmin(admin.ModelAdmin):
    list_display = ['student','teacher','course','rating','created_at']
    list_filter  = ['rating']
