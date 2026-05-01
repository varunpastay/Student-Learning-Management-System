"""courses/views.py"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q

from .models import Course, Category, Enrollment, CourseMaterial
from .forms import CourseForm, CourseMaterialForm
from accounts.permissions import teacher_required, student_required


def course_list(request):
    """Public course listing with search & filter."""
    courses = Course.objects.filter(status='published').select_related('teacher', 'category')

    # Search
    query = request.GET.get('q', '')
    if query:
        courses = courses.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(teacher__first_name__icontains=query)
        )

    # Category filter
    category_slug = request.GET.get('category', '')
    if category_slug:
        courses = courses.filter(category__slug=category_slug)

    # Level filter
    level = request.GET.get('level', '')
    if level:
        courses = courses.filter(level=level)

    # Pagination
    paginator = Paginator(courses, 9)
    page      = request.GET.get('page', 1)
    courses   = paginator.get_page(page)

    categories = Category.objects.all()
    user_enrolled_courses = []
    if request.user.is_authenticated and request.user.is_student:
        user_enrolled_courses = list(Course.objects.filter(enrollments__student=request.user, enrollments__is_active=True))
    return render(request, 'courses/course_list.html', {
        'courses': courses, 'categories': categories,
        'query': query, 'selected_category': category_slug,
        'selected_level': level, 'level_choices': Course.Level.choices,
        'user_enrolled_courses': user_enrolled_courses,
    })


def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug, status='published')
    is_enrolled = False
    if request.user.is_authenticated and request.user.is_student:
        is_enrolled = Enrollment.objects.filter(student=request.user, course=course, is_active=True).exists()

    materials = course.materials.all() if (is_enrolled or (request.user.is_authenticated and request.user.is_teacher)) else course.materials.none()
    enrollment_progress = None
    if is_enrolled:
        try:
            enrollment_progress = Enrollment.objects.get(student=request.user, course=course, is_active=True).progress
        except: pass
    return render(request, 'courses/course_detail.html', {
        'course': course, 'is_enrolled': is_enrolled, 'materials': materials,
        'enrollment_progress': enrollment_progress,
    })


@student_required
def enroll_course(request, slug):
    course = get_object_or_404(Course, slug=slug, status='published')

    if course.is_full:
        messages.error(request, 'This course is full.')
        return redirect('courses:detail', slug=slug)

    enrollment, created = Enrollment.objects.get_or_create(
        student=request.user, course=course,
        defaults={'is_active': True}
    )
    if created:
        messages.success(request, f'You have enrolled in {course.title}!')
        # Signal will fire notification
    else:
        messages.info(request, 'You are already enrolled in this course.')
    return redirect('courses:detail', slug=slug)


@student_required
def unenroll_course(request, slug):
    course = get_object_or_404(Course, slug=slug)
    Enrollment.objects.filter(student=request.user, course=course).update(is_active=False)
    messages.success(request, f'You have unenrolled from {course.title}.')
    return redirect('courses:list')


@teacher_required
def course_create(request):
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = request.user
            course.save()
            messages.success(request, f'Course "{course.title}" created successfully!')
            return redirect('courses:detail', slug=course.slug)
    else:
        form = CourseForm()
    return render(request, 'courses/course_form.html', {'form': form, 'action': 'Create'})


@teacher_required
def course_edit(request, slug):
    course = get_object_or_404(Course, slug=slug, teacher=request.user)
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course updated successfully!')
            return redirect('courses:detail', slug=course.slug)
    else:
        form = CourseForm(instance=course)
    return render(request, 'courses/course_form.html', {'form': form, 'action': 'Edit', 'course': course})


@teacher_required
def course_delete(request, slug):
    course = get_object_or_404(Course, slug=slug, teacher=request.user)
    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Course deleted.')
        return redirect('dashboard:teacher_dashboard')
    return render(request, 'courses/course_confirm_delete.html', {'course': course})


@teacher_required
def add_material(request, slug):
    course = get_object_or_404(Course, slug=slug, teacher=request.user)
    if request.method == 'POST':
        form = CourseMaterialForm(request.POST, request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            material.course = course
            material.save()
            messages.success(request, 'Material added.')
            return redirect('courses:detail', slug=slug)
    else:
        form = CourseMaterialForm()
    return render(request, 'courses/add_material.html', {'form': form, 'course': course})
