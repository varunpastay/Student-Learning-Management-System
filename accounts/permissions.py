"""accounts/permissions.py — Role-based access control."""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from rest_framework.permissions import BasePermission


# ─── Django View Decorators ────────────────────────────────────────────────────

def student_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not request.user.is_student:
            messages.error(request, 'This page is for students only.')
            return redirect('dashboard:home')
        return view_func(request, *args, **kwargs)
    return wrapper


def teacher_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not request.user.is_teacher and not request.user.is_admin_user:
            messages.error(request, 'This page is for teachers only.')
            return redirect('dashboard:home')
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not request.user.is_admin_user:
            messages.error(request, 'Admin access required.')
            return redirect('dashboard:home')
        return view_func(request, *args, **kwargs)
    return wrapper


# ─── DRF Permission Classes ────────────────────────────────────────────────────

class IsTeacherOrAdmin(BasePermission):
    message = 'Only teachers or admins can perform this action.'

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            (request.user.is_teacher or request.user.is_admin_user)
        )


class IsStudentOnly(BasePermission):
    message = 'Only students can perform this action.'

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_student


class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_admin_user:
            return True
        if hasattr(obj, 'student'):
            return obj.student == request.user
        if hasattr(obj, 'teacher'):
            return obj.teacher == request.user
        return obj == request.user
