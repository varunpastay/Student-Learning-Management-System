"""courses/signals.py — Auto-notifications on enrollment + progress tracking."""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Enrollment


def update_enrollment_progress(student, course):
    """Recalculate student progress = submitted assignments / total assignments."""
    from assignments.models import Assignment, Submission
    total = Assignment.objects.filter(course=course).count()
    if total == 0:
        return
    submitted = Submission.objects.filter(
        student=student,
        assignment__course=course,
        status__in=['submitted', 'late', 'graded']
    ).count()
    progress = round((submitted / total) * 100, 2)
    Enrollment.objects.filter(
        student=student, course=course, is_active=True
    ).update(progress=progress)


@receiver(post_save, sender=Enrollment)
def notify_enrollment(sender, instance, created, **kwargs):
    if created:
        import threading
        from notifications.utils import create_notification
        from notifications.email_utils import (
            email_enrollment_confirmation,
            email_new_student_enrolled
        )
        try:
            create_notification(
                user=instance.student,
                title=f'Enrolled in {instance.course.title}',
                message=f'Successfully enrolled in "{instance.course.title}".',
                notification_type='course'
            )
            create_notification(
                user=instance.course.teacher,
                title=f'New Student Enrolled',
                message=f'{instance.student.get_full_name()} enrolled in "{instance.course.title}".',
                notification_type='course'
            )
        except Exception:
            pass

        def send_emails():
            try:
                email_enrollment_confirmation(instance)
                email_new_student_enrolled(instance)
            except Exception:
                pass
        threading.Thread(target=send_emails, daemon=True).start()


@receiver(post_save, sender='assignments.Submission')
def progress_on_submission(sender, instance, created, **kwargs):
    """Update progress when student submits an assignment."""
    if created:
        update_enrollment_progress(instance.student, instance.assignment.course)


@receiver(post_save, sender='assignments.Submission')
def progress_on_grade(sender, instance, created, **kwargs):
    """Update progress when assignment is graded."""
    if not created and instance.status == 'graded':
        update_enrollment_progress(instance.student, instance.assignment.course)