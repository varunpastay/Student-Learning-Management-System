"""courses/admin.py"""
from django.contrib import admin
from .models import Category, Course, Enrollment, CourseMaterial


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


class CourseMaterialInline(admin.TabularInline):
    model = CourseMaterial
    extra = 1


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display   = ['title', 'teacher', 'category', 'level', 'status', 'enrolled_count', 'created_at']
    list_filter    = ['status', 'level', 'category']
    search_fields  = ['title', 'teacher__username']
    prepopulated_fields = {'slug': ('title',)}
    inlines        = [CourseMaterialInline]


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display  = ['student', 'course', 'enrolled_at', 'is_active', 'progress', 'completed']
    list_filter   = ['is_active', 'completed']
    search_fields = ['student__username', 'course__title']
