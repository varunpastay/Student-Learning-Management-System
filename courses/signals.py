"""courses/signals.py — Auto-notifications + real emails on enrollment."""
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Enrollment


@receiver(post_save, sender=Enrollment)
def notify_enrollment(sender, instance, created, **kwargs):
    if created:
        from notifications.utils import create_notification
        from notifications.email_utils import email_enrollment_confirmation, email_new_student_enrolled
        # In-app: student
        create_notification(
            user=instance.student,
            title=f'Enrolled in {instance.course.title}',
            message=f'Successfully enrolled in "{instance.course.title}" by {instance.course.teacher.get_full_name()}.',
            notification_type='course'
        )
        # In-app: teacher
        create_notification(
            user=instance.course.teacher,
            title=f'New Student Enrolled',
            message=f'{instance.student.get_full_name()} enrolled in "{instance.course.title}".',
            notification_type='course'
        )
        # Real email: student
        email_enrollment_confirmation(instance)
        # Real email: teacher
        email_new_student_enrolled(instance)
