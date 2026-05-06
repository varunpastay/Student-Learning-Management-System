"""
courses/models.py
Course management: Category → Course → Enrollment
"""
from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.utils import timezone


class Category(models.Model):
    name        = models.CharField(max_length=100, unique=True)
    slug        = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    icon        = models.CharField(max_length=50, default='book')
    created_at  = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']


class Course(models.Model):
    class Level(models.TextChoices):
        BEGINNER     = 'beginner',     'Beginner'
        INTERMEDIATE = 'intermediate', 'Intermediate'
        ADVANCED     = 'advanced',     'Advanced'

    class Status(models.TextChoices):
        DRAFT     = 'draft',     'Draft'
        PUBLISHED = 'published', 'Published'
        ARCHIVED  = 'archived',  'Archived'

    title       = models.CharField(max_length=200)
    slug        = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    teacher     = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='courses_taught', limit_choices_to={'role': 'teacher'}
    )
    category    = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='courses')
    thumbnail   = models.ImageField(upload_to='course_thumbnails/', blank=True, null=True)
    level       = models.CharField(max_length=15, choices=Level.choices, default=Level.BEGINNER)
    status      = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
    max_students = models.PositiveIntegerField(default=50)
    start_date  = models.DateField(null=True, blank=True)
    end_date    = models.DateField(null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)
    youtube_url = models.URLField(blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Course.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def enrolled_count(self):
        return self.enrollments.filter(is_active=True).count()

    @property
    def is_full(self):
        return self.enrolled_count >= self.max_students

    @property
    def is_active(self):
        today = timezone.now().date()
        if self.start_date and self.end_date:
            return self.start_date <= today <= self.end_date
        return self.status == self.Status.PUBLISHED

    def __str__(self):
        return f"{self.title} ({self.teacher.get_full_name()})"

    class Meta:
        ordering = ['-created_at']


class Enrollment(models.Model):
    student    = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='enrollments', limit_choices_to={'role': 'student'}
    )
    course     = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    is_active  = models.BooleanField(default=True)
    progress   = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    completed  = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.student.get_full_name()} → {self.course.title}"

    class Meta:
        unique_together = ('student', 'course')
        ordering = ['-enrolled_at']


class CourseMaterial(models.Model):
    class MaterialType(models.TextChoices):
        PDF   = 'pdf',   'PDF'
        VIDEO = 'video', 'Video Link'
        LINK  = 'link',  'External Link'
        OTHER = 'other', 'Other'

    course        = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='materials')
    title         = models.CharField(max_length=200)
    material_type = models.CharField(max_length=10, choices=MaterialType.choices, default=MaterialType.PDF)
    file          = models.FileField(upload_to='course_materials/', blank=True, null=True)
    url           = models.URLField(blank=True)
    description   = models.TextField(blank=True)
    order         = models.PositiveIntegerField(default=0)
    uploaded_at   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course.title} | {self.title}"

    class Meta:
        ordering = ['order', 'uploaded_at']