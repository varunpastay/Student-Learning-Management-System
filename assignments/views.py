"""assignments/views.py — Full CRUD + submit + grade + real email notifications."""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q

from .models import Assignment, Submission
from .forms import AssignmentForm, SubmissionForm, GradeSubmissionForm
from accounts.permissions import teacher_required, student_required
from notifications.utils import create_notification
from notifications.email_utils import (
    email_new_assignment, email_grade_received,
    email_new_submission
)
from courses.models import Enrollment


@login_required
def assignment_list(request):
    user = request.user
    status_filter = request.GET.get('status', '')
    if user.is_teacher:
        qs = Assignment.objects.filter(created_by=user).select_related('course').annotate(
            sub_count=Count('submissions'))
    else:
        enrolled = Enrollment.objects.filter(student=user, is_active=True).values_list('course_id', flat=True)
        qs = Assignment.objects.filter(course_id__in=enrolled).select_related('course')

    all_count    = qs.count()
    open_count   = sum(1 for a in qs if not a.is_past_deadline)
    closed_count = sum(1 for a in qs if a.is_past_deadline)
    pending_grade_count = 0
    if user.is_teacher:
        pending_grade_count = Submission.objects.filter(
            assignment__created_by=user, status__in=['submitted','late']).count()

    if status_filter == 'open':
        qs = [a for a in qs if not a.is_past_deadline]
    elif status_filter == 'closed':
        qs = [a for a in qs if a.is_past_deadline]
    elif status_filter == 'pending_grade' and user.is_teacher:
        ids = Submission.objects.filter(assignment__created_by=user,
              status__in=['submitted','late']).values_list('assignment_id', flat=True)
        qs = Assignment.objects.filter(id__in=ids).select_related('course')

    return render(request, 'assignments/assignment_list.html', {
        'assignments': qs, 'status_filter': status_filter,
        'all_count': all_count, 'open_count': open_count,
        'closed_count': closed_count, 'pending_grade_count': pending_grade_count,
    })


@login_required
def assignment_detail(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    user = request.user
    user_submission = None
    all_submissions = None
    if user.is_student:
        user_submission = Submission.objects.filter(assignment=assignment, student=user).first()
    elif user.is_teacher:
        all_submissions = Submission.objects.filter(
            assignment=assignment).select_related('student').order_by('-submitted_at')
    graded_count = assignment.submissions.filter(status='graded').count() if user.is_teacher else None
    return render(request, 'assignments/assignment_detail.html', {
        'assignment': assignment, 'user_submission': user_submission,
        'all_submissions': all_submissions, 'graded_count': graded_count,
        'now': timezone.now(),
    })


@teacher_required
def assignment_create(request):
    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES, teacher=request.user)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.created_by = request.user
            assignment.save()
            # Get enrolled students
            enrollments = Enrollment.objects.filter(
                course=assignment.course, is_active=True).select_related('student')
            enrolled_students = [e.student for e in enrollments]
            # In-app notification
            for student in enrolled_students:
                create_notification(
                    user=student,
                    title=f'New Assignment: {assignment.title}',
                    message=f'Posted in {assignment.course.title}. Due: {assignment.deadline.strftime("%b %d, %Y %H:%M")}',
                    notification_type='assignment'
                )
            # Real email notification
            email_new_assignment(assignment, enrolled_students)
            messages.success(request, f'✅ Assignment "{assignment.title}" created! Email notifications sent to {len(enrolled_students)} students.')
            return redirect('assignments:detail', pk=assignment.pk)
    else:
        form = AssignmentForm(teacher=request.user)
    return render(request, 'assignments/assignment_form.html', {'form': form, 'action': 'Create'})


@teacher_required
def assignment_edit(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk, created_by=request.user)
    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES, instance=assignment, teacher=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Assignment updated!')
            return redirect('assignments:detail', pk=assignment.pk)
    else:
        form = AssignmentForm(instance=assignment, teacher=request.user)
    return render(request, 'assignments/assignment_form.html',
                  {'form': form, 'action': 'Edit', 'assignment': assignment})


@teacher_required
def assignment_delete(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk, created_by=request.user)
    if request.method == 'POST':
        title = assignment.title
        assignment.delete()
        messages.success(request, f'Assignment "{title}" deleted.')
        return redirect('assignments:list')
    return render(request, 'assignments/assignment_confirm_delete.html', {'assignment': assignment})


@student_required
def submit_assignment(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    if not Enrollment.objects.filter(student=request.user, course=assignment.course, is_active=True).exists():
        messages.error(request, 'You are not enrolled in this course.')
        return redirect('courses:list')
    if Submission.objects.filter(assignment=assignment, student=request.user).exists():
        messages.info(request, 'You have already submitted this assignment.')
        return redirect('assignments:detail', pk=pk)
    if assignment.is_past_deadline and not assignment.allow_late:
        messages.error(request, 'Deadline passed and late submissions are not allowed.')
        return redirect('assignments:detail', pk=pk)

    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            sub = form.save(commit=False)
            sub.assignment = assignment
            sub.student    = request.user
            sub.status     = Submission.Status.LATE if assignment.is_past_deadline else Submission.Status.SUBMITTED
            sub.save()
            # In-app notification to teacher
            create_notification(
                user=assignment.created_by,
                title=f'New Submission: {assignment.title}',
                message=f'{request.user.get_full_name()} submitted "{assignment.title}".',
                notification_type='assignment'
            )
            # Real email to teacher
            email_new_submission(sub)
            messages.success(request, '✅ Assignment submitted! Your teacher has been notified by email.')
            return redirect('assignments:detail', pk=pk)
    else:
        form = SubmissionForm()
    return render(request, 'assignments/submit_assignment.html',
                  {'form': form, 'assignment': assignment})


@teacher_required
def grade_submission(request, pk):
    submission = get_object_or_404(Submission, pk=pk, assignment__created_by=request.user)
    if request.method == 'POST':
        form = GradeSubmissionForm(request.POST, instance=submission)
        if form.is_valid():
            sub = form.save(commit=False)
            sub.status    = Submission.Status.GRADED
            sub.graded_by = request.user
            sub.graded_at = timezone.now()
            sub.save()
            # In-app notification
            create_notification(
                user=submission.student,
                title='Assignment Graded',
                message=f'"{submission.assignment.title}" — {sub.marks_obtained}/{submission.assignment.total_marks} marks.',
                notification_type='grade'
            )
            # Real email to student
            email_grade_received(sub)
            messages.success(request, f'✅ Graded! Email sent to {submission.student.get_full_name()}.')
            return redirect('assignments:detail', pk=submission.assignment.pk)
    else:
        form = GradeSubmissionForm(instance=submission)
    return render(request, 'assignments/grade_submission.html',
                  {'form': form, 'submission': submission})
