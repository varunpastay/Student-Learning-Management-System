from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg
from .models import TeacherFeedback
from .forms import FeedbackForm
from courses.models import Course, Enrollment
from accounts.models import User


@login_required
def give_feedback(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    if not request.user.is_student:
        messages.error(request, 'Only students can give feedback.')
        return redirect('courses:detail', slug=course_slug)
    if not Enrollment.objects.filter(student=request.user, course=course, is_active=True).exists():
        messages.error(request, 'You must be enrolled to give feedback.')
        return redirect('courses:detail', slug=course_slug)

    existing = TeacherFeedback.objects.filter(student=request.user, course=course).first()

    if request.method == 'POST':
        form = FeedbackForm(request.POST, instance=existing)
        if form.is_valid():
            fb = form.save(commit=False)
            fb.student = request.user
            fb.teacher = course.teacher
            fb.course  = course
            fb.save()
            from notifications.email_utils import email_new_feedback
            email_new_feedback(fb)
            messages.success(request, '✅ Feedback submitted! Teacher has been notified.')
            return redirect('courses:detail', slug=course_slug)
    else:
        form = FeedbackForm(instance=existing)

    # Course average rating
    avg = TeacherFeedback.objects.filter(course=course).aggregate(Avg('rating'))['rating__avg']
    all_feedback = TeacherFeedback.objects.filter(course=course).select_related('student')

    return render(request, 'feedback/give_feedback.html', {
        'form': form, 'course': course, 'existing': existing,
        'avg_rating': round(avg, 1) if avg else None,
        'all_feedback': all_feedback,
    })


@login_required
def teacher_feedback_view(request):
    """Teacher views all their feedback."""
    if not request.user.is_teacher:
        return redirect('dashboard:home')
    feedback = TeacherFeedback.objects.filter(teacher=request.user).select_related('student','course')
    avg = feedback.aggregate(Avg('rating'))['rating__avg']
    return render(request, 'feedback/teacher_feedback.html', {
        'feedback': feedback,
        'avg_rating': round(avg, 1) if avg else None,
    })
