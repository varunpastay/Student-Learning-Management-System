"""accounts/views.py"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse

from .forms import (StudentRegistrationForm, TeacherRegistrationForm,
                    LoginForm, UserProfileForm, StudentProfileForm, TeacherProfileForm)
from .models import User


def register_student(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            from notifications.email_utils import email_welcome
            email_welcome(user)
            messages.success(request, f'Welcome, {user.get_full_name()}! A confirmation email has been sent to {user.email}.')
            return redirect('dashboard:student_dashboard')
    else:
        form = StudentRegistrationForm()
    return render(request, 'accounts/register_student.html', {'form': form})


def register_teacher(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    if request.method == 'POST':
        form = TeacherRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            from notifications.email_utils import email_welcome
            email_welcome(user)
            messages.success(request, f'Welcome, {user.get_full_name()}! A confirmation email has been sent to {user.email}.')
            return redirect('dashboard:teacher_dashboard')
    else:
        form = TeacherRegistrationForm()
    return render(request, 'accounts/register_teacher.html', {'form': form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next', 'dashboard:home')
            messages.success(request, f'Welcome back, {user.get_full_name()}!')
            return redirect(next_url)
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def user_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('accounts:login')


@login_required
def profile(request):
    user = request.user
    user_form = UserProfileForm(instance=user)
    profile_form = None

    if user.is_student:
        profile_obj, _ = user.student_profile.__class__.objects.get_or_create(user=user)
        profile_form = StudentProfileForm(instance=profile_obj)
    elif user.is_teacher:
        profile_obj, _ = user.teacher_profile.__class__.objects.get_or_create(user=user)
        profile_form = TeacherProfileForm(instance=profile_obj)

    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, request.FILES, instance=user)
        if user.is_student:
            profile_form = StudentProfileForm(request.POST, instance=profile_obj)
        elif user.is_teacher:
            profile_form = TeacherProfileForm(request.POST, instance=profile_obj)

        forms_valid = user_form.is_valid() and (profile_form is None or profile_form.is_valid())
        if forms_valid:
            user_form.save()
            if profile_form:
                profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')

    return render(request, 'accounts/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })


def error_403(request, exception=None):
    return render(request, 'errors/403.html', status=403)


def error_404(request, exception=None):
    return render(request, 'errors/404.html', status=404)


from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully!')
            return redirect('accounts:profile')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {'form': form})
