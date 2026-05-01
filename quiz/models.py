"""quiz/models.py — Full MCQ quiz system with auto-grading."""
from django.db import models
from django.conf import settings


class Quiz(models.Model):
    course       = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='quizzes')
    created_by   = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_quizzes')
    title        = models.CharField(max_length=200)
    description  = models.TextField(blank=True)
    time_limit   = models.PositiveIntegerField(default=30, help_text='Time limit in minutes (0 = no limit)')
    pass_score   = models.PositiveIntegerField(default=60, help_text='Minimum percentage to pass')
    is_active    = models.BooleanField(default=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    def __str__(self): return f"{self.title} ({self.course.title})"

    @property
    def total_marks(self): return self.questions.count()

    class Meta: ordering = ['-created_at']


class Question(models.Model):
    quiz    = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text    = models.TextField()
    order   = models.PositiveIntegerField(default=0)
    marks   = models.PositiveIntegerField(default=1)
    explanation = models.TextField(blank=True, help_text='Explanation shown after answering')

    def __str__(self): return self.text[:60]

    class Meta: ordering = ['order']


class Choice(models.Model):
    question   = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text       = models.CharField(max_length=300)
    is_correct = models.BooleanField(default=False)

    def __str__(self): return self.text[:50]


class QuizAttempt(models.Model):
    quiz       = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    student    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quiz_attempts')
    score      = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total      = models.PositiveIntegerField(default=0)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    passed     = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta: unique_together = ('quiz', 'student')

    @property
    def grade_letter(self):
        p = float(self.percentage)
        if p >= 90: return 'A'
        if p >= 80: return 'B'
        if p >= 70: return 'C'
        if p >= 60: return 'D'
        return 'F'


class StudentAnswer(models.Model):
    attempt  = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice   = models.ForeignKey(Choice, on_delete=models.SET_NULL, null=True, blank=True)
    is_correct = models.BooleanField(default=False)
