"""assignments/admin.py"""
from django.contrib import admin
from .models import Assignment, Submission


class SubmissionInline(admin.TabularInline):
    model = Submission
    extra = 0
    readonly_fields = ['student', 'submitted_at', 'status']


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display  = ['title', 'course', 'created_by', 'deadline', 'total_marks', 'allow_late']
    list_filter   = ['allow_late', 'course__category']
    search_fields = ['title', 'course__title', 'created_by__username']
    inlines       = [SubmissionInline]


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display  = ['student', 'assignment', 'status', 'marks_obtained', 'submitted_at', 'graded_by']
    list_filter   = ['status']
    search_fields = ['student__username', 'assignment__title']
    readonly_fields = ['submitted_at', 'graded_at']
