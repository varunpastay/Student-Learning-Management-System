"""accounts/admin.py"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, StudentProfile, TeacherProfile


class StudentProfileInline(admin.StackedInline):
    model = StudentProfile
    extra = 0
    can_delete = False


class TeacherProfileInline(admin.StackedInline):
    model = TeacherProfile
    extra = 0
    can_delete = False


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display  = ['username', 'get_full_name', 'email', 'role', 'is_active', 'date_joined']
    list_filter   = ['role', 'is_active', 'is_staff']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    fieldsets     = BaseUserAdmin.fieldsets + (
        ('LMS Info', {'fields': ('role', 'avatar', 'bio', 'phone')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('LMS Info', {'fields': ('role', 'first_name', 'last_name', 'email')}),
    )

    def get_inlines(self, request, obj=None):
        if obj:
            if obj.role == User.Role.STUDENT:
                return [StudentProfileInline]
            elif obj.role == User.Role.TEACHER:
                return [TeacherProfileInline]
        return []


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display  = ['user', 'student_id', 'department', 'year_of_study', 'cgpa']
    search_fields = ['user__username', 'student_id', 'department']


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display  = ['user', 'employee_id', 'department', 'specialization']
    search_fields = ['user__username', 'employee_id', 'department']
