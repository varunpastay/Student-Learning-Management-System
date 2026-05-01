from django.contrib import admin
from .models import Quiz, Question, Choice, QuizAttempt, StudentAnswer

class ChoiceInline(admin.TabularInline):
    model = Choice; extra = 4

class QuestionInline(admin.TabularInline):
    model = Question; extra = 2

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title','course','created_by','is_active','created_at']
    inlines = [QuestionInline]

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text','quiz','marks']
    inlines = [ChoiceInline]

@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ['student','quiz','score','percentage','passed','started_at']
