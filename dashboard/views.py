"""dashboard/views.py — Role-aware dashboards with full data."""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count, Q

from courses.models import Course, Enrollment
from assignments.models import Assignment, Submission
from notifications.models import Notification


@login_required
def home(request):
    if request.user.is_student:   return redirect('dashboard:student_dashboard')
    elif request.user.is_teacher: return redirect('dashboard:teacher_dashboard')
    else:                         return redirect('dashboard:admin_dashboard')


@login_required
def student_dashboard(request):
    user = request.user
    enrollments = Enrollment.objects.filter(student=user, is_active=True).select_related('course','course__teacher','course__category')
    enrolled_courses = [e.course for e in enrollments]

    pending_assignments = Assignment.objects.filter(
        course__in=enrolled_courses, deadline__gte=timezone.now()
    ).exclude(submissions__student=user).select_related('course').order_by('deadline')[:6]

    overdue_assignments = Assignment.objects.filter(
        course__in=enrolled_courses, deadline__lt=timezone.now()
    ).exclude(submissions__student=user)

    recent_submissions = Submission.objects.filter(student=user).select_related('assignment','assignment__course').order_by('-submitted_at')[:5]
    notifications = Notification.objects.filter(user=user).order_by('-created_at')[:6]

    return render(request, 'dashboard/student_dashboard.html', {
        'enrollments': enrollments,
        'enrolled_count': enrollments.count(),
        'pending_assignments': pending_assignments,
        'pending_count': pending_assignments.count(),
        'overdue_count': overdue_assignments.count(),
        'recent_submissions': recent_submissions,
        'submitted_count': Submission.objects.filter(student=user).count(),
        'notifications': notifications,
    })


@login_required
def teacher_dashboard(request):
    user = request.user
    my_courses = Course.objects.filter(teacher=user).annotate(
        student_count=Count('enrollments', filter=Q(enrollments__is_active=True)),
        assignment_count=Count('assignments'),
    )
    my_assignments = Assignment.objects.filter(created_by=user).annotate(
        submission_count=Count('submissions'),
        graded_count=Count('submissions', filter=Q(submissions__status='graded')),
    ).select_related('course').order_by('-created_at')[:8]

    recent_submissions = Submission.objects.filter(
        assignment__created_by=user
    ).select_related('student','assignment','assignment__course').order_by('-submitted_at')[:10]

    pending_grading = Submission.objects.filter(assignment__created_by=user, status__in=['submitted','late']).count()
    total_students  = Enrollment.objects.filter(course__teacher=user, is_active=True).values('student').distinct().count()

    # Chart data
    course_names  = [c.title[:20] for c in my_courses]
    course_counts = [c.student_count for c in my_courses]

    import json
    return render(request, 'dashboard/teacher_dashboard.html', {
        'my_courses': my_courses,
        'course_count': my_courses.count(),
        'my_assignments': my_assignments,
        'recent_submissions': recent_submissions,
        'pending_grading': pending_grading,
        'total_students': total_students,
        'course_names_json': json.dumps(course_names),
        'course_counts_json': json.dumps(course_counts),
        'late_count': Submission.objects.filter(assignment__created_by=user, status='late').count(),
        'graded_count': Submission.objects.filter(assignment__created_by=user, status='graded').count(),
    })


@login_required
def admin_dashboard(request):
    if not request.user.is_admin_user:
        return redirect('dashboard:home')
    from accounts.models import User
    import json

    total_s = User.objects.filter(role='student').count()
    total_t = User.objects.filter(role='teacher').count()
    total_c = Course.objects.count()
    total_a = Assignment.objects.count()
    total_sub = Submission.objects.count()
    graded   = Submission.objects.filter(status='graded').count()

    recent_users   = User.objects.order_by('-date_joined')[:6]
    recent_courses = Course.objects.order_by('-created_at').select_related('teacher')[:6]

    course_enrollments = list(Course.objects.annotate(ec=Count('enrollments', filter=Q(enrollments__is_active=True))).values_list('title','ec')[:5])
    return render(request, 'dashboard/admin_dashboard.html', {
        'total_students': total_s, 'total_teachers': total_t,
        'total_courses': total_c, 'total_assignments': total_a,
        'total_submissions': total_sub, 'graded_submissions': graded,
        'published_courses': Course.objects.filter(status='published').count(),
        'recent_users': recent_users, 'recent_courses': recent_courses,
        'course_labels': json.dumps([c[0][:18] for c in course_enrollments]),
        'course_data':   json.dumps([c[1] for c in course_enrollments]),
        'stat_cards': [
            ('Students', total_s, 'people-fill', '#4f46e5'),
            ('Teachers', total_t, 'person-workspace', '#7c3aed'),
            ('Courses',  total_c, 'book-fill', '#059669'),
            ('Assignments', total_a, 'file-earmark-text', '#d97706'),
            ('Submissions', total_sub, 'inbox-fill', '#0891b2'),
            ('Graded', graded, 'check-circle-fill', '#059669'),
        ],
    })


@login_required
def leaderboard(request):
    from .leaderboard import get_leaderboard
    board = get_leaderboard(20)
    # Find current user rank
    all_board = get_leaderboard(1000)
    user_rank = next((i+1 for i,x in enumerate(all_board) if x['student']==request.user), None)
    return render(request, 'dashboard/leaderboard.html', {
        'board': board, 'user_rank': user_rank,
    })
