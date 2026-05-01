"""
notifications/email_utils.py
Real-time email notifications sent to actual Gmail addresses.
Uses Django's SMTP email backend with Gmail.
"""
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def send_real_email(to_email, subject, html_content):
    """Core function — sends actual HTML email via Gmail SMTP."""
    try:
        plain = strip_tags(html_content)
        msg = EmailMultiAlternatives(
            subject=f'[SLMS] {subject}',
            body=plain,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)
        logger.info(f'✅ Email sent to {to_email}: {subject}')
        return True
    except Exception as e:
        logger.error(f'❌ Email failed to {to_email}: {e}')
        return False


def _base_email(title, body_html, action_url=None, action_text=None):
    """Build a styled HTML email."""
    btn = ''
    if action_url and action_text:
        btn = f'<a href="{action_url}" style="display:inline-block;background:#4f46e5;color:#fff;padding:12px 28px;border-radius:8px;text-decoration:none;font-weight:600;font-size:14px;margin:20px 0">{action_text}</a>'
    return f"""
<!DOCTYPE html><html><head><meta charset="UTF-8">
<style>
  body{{margin:0;padding:0;background:#f1f5f9;font-family:'Segoe UI',Arial,sans-serif}}
  .wrap{{max-width:600px;margin:30px auto;background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,.08)}}
  .header{{background:linear-gradient(135deg,#4f46e5,#7c3aed);padding:32px;text-align:center}}
  .header h1{{color:#fff;margin:0;font-size:26px;font-weight:700}}
  .header p{{color:rgba(255,255,255,.8);margin:6px 0 0;font-size:13px}}
  .body{{padding:32px}}
  .body h2{{font-size:22px;color:#1e293b;margin:0 0 12px}}
  .body p{{color:#475569;line-height:1.7;font-size:14px;margin:8px 0}}
  .info{{background:#f8fafc;border-radius:10px;padding:16px 20px;margin:16px 0;border-left:4px solid #4f46e5}}
  .info p{{margin:5px 0;font-size:13px;color:#334155}}
  .footer{{background:#f8fafc;padding:20px 32px;text-align:center;font-size:12px;color:#94a3b8;border-top:1px solid #e2e8f0}}
  .badge{{display:inline-block;background:#ede9fe;color:#4f46e5;padding:3px 10px;border-radius:20px;font-size:12px;font-weight:600}}
</style>
</head><body>
<div class="wrap">
  <div class="header">
    <h1>📚 SLMS</h1>
    <p>Student Learning Management System</p>
  </div>
  <div class="body">
    {title}
    {body_html}
    {btn}
  </div>
  <div class="footer">
    © SLMS — You received this because you are a registered user.<br>
    <a href="https://student-learning-management-system.onrender.com" style="color:#4f46e5">Visit SLMS</a>
  </div>
</div>
</body></html>"""


BASE_URL = "https://student-learning-management-system.onrender.com"


# ── Specific notification functions ────────────────────────────────────────

def email_new_assignment(assignment, students):
    """Notify students when a new assignment is posted."""
    for student in students:
        html = _base_email(
            f'<h2>📝 New Assignment Posted!</h2>',
            f'''<p>Hi <strong>{student.first_name}</strong>,</p>
            <p>A new assignment has been posted in <strong>{assignment.course.title}</strong>.</p>
            <div class="info">
              <p><strong>Assignment:</strong> {assignment.title}</p>
              <p><strong>Course:</strong> {assignment.course.title}</p>
              <p><strong>Instructor:</strong> {assignment.created_by.get_full_name()}</p>
              <p><strong>Due Date:</strong> {assignment.deadline.strftime("%B %d, %Y at %H:%M")}</p>
              <p><strong>Total Marks:</strong> {assignment.total_marks}</p>
            </div>
            <p>{assignment.description[:300]}</p>''',
            f'{BASE_URL}/assignments/{assignment.pk}/',
            '📝 View Assignment'
        )
        send_real_email(student.email, f'New Assignment: {assignment.title}', html)


def email_grade_received(submission):
    """Notify student when their assignment is graded."""
    student = submission.student
    grade_color = '#059669' if float(submission.percentage or 0) >= 60 else '#dc2626'
    html = _base_email(
        f'<h2>⭐ Your Assignment Has Been Graded!</h2>',
        f'''<p>Hi <strong>{student.first_name}</strong>,</p>
        <p>Your submission for <strong>{submission.assignment.title}</strong> has been graded.</p>
        <div class="info">
          <p><strong>Assignment:</strong> {submission.assignment.title}</p>
          <p><strong>Course:</strong> {submission.assignment.course.title}</p>
          <p><strong>Marks:</strong> <span style="color:{grade_color};font-weight:700;font-size:16px">{submission.marks_obtained} / {submission.assignment.total_marks}</span></p>
          <p><strong>Percentage:</strong> <span style="color:{grade_color};font-weight:700">{submission.percentage}%</span></p>
          {"<p><strong>Feedback:</strong> " + str(submission.feedback) + "</p>" if submission.feedback else ""}
        </div>''',
        f'{BASE_URL}/assignments/{submission.assignment.pk}/',
        '📊 View Full Results'
    )
    send_real_email(student.email, f'Assignment Graded: {submission.assignment.title}', html)


def email_enrollment_confirmation(enrollment):
    """Confirm enrollment to student."""
    student = enrollment.student
    html = _base_email(
        f'<h2>🎓 Enrollment Confirmed!</h2>',
        f'''<p>Hi <strong>{student.first_name}</strong>,</p>
        <p>You have successfully enrolled in a new course. Welcome!</p>
        <div class="info">
          <p><strong>Course:</strong> {enrollment.course.title}</p>
          <p><strong>Instructor:</strong> {enrollment.course.teacher.get_full_name()}</p>
          <p><strong>Level:</strong> {enrollment.course.get_level_display()}</p>
          <p><strong>Start Date:</strong> {enrollment.course.start_date or "Ongoing"}</p>
        </div>
        <p>Log in to your dashboard to access course materials and upcoming assignments.</p>''',
        f'{BASE_URL}/courses/{enrollment.course.slug}/',
        '📚 Go to Course'
    )
    send_real_email(student.email, f'Enrolled in {enrollment.course.title}', html)


def email_new_student_enrolled(enrollment):
    """Notify teacher when a new student enrolls."""
    teacher = enrollment.course.teacher
    student = enrollment.student
    html = _base_email(
        f'<h2>👋 New Student Enrolled!</h2>',
        f'''<p>Hi <strong>{teacher.first_name}</strong>,</p>
        <p>A new student has enrolled in your course.</p>
        <div class="info">
          <p><strong>Student:</strong> {student.get_full_name()}</p>
          <p><strong>Email:</strong> {student.email}</p>
          <p><strong>Course:</strong> {enrollment.course.title}</p>
          <p><strong>Total Enrolled:</strong> {enrollment.course.enrolled_count} / {enrollment.course.max_students}</p>
        </div>''',
        f'{BASE_URL}/courses/{enrollment.course.slug}/',
        '👥 View Course'
    )
    send_real_email(teacher.email, f'New Student: {student.get_full_name()}', html)


def email_new_submission(submission):
    """Notify teacher when a student submits an assignment."""
    teacher = submission.assignment.created_by
    student = submission.student
    html = _base_email(
        f'<h2>📥 New Assignment Submission!</h2>',
        f'''<p>Hi <strong>{teacher.first_name}</strong>,</p>
        <p><strong>{student.get_full_name()}</strong> has submitted an assignment that needs grading.</p>
        <div class="info">
          <p><strong>Student:</strong> {student.get_full_name()} ({student.email})</p>
          <p><strong>Assignment:</strong> {submission.assignment.title}</p>
          <p><strong>Course:</strong> {submission.assignment.course.title}</p>
          <p><strong>Submitted At:</strong> {submission.submitted_at.strftime("%B %d, %Y at %H:%M")}</p>
          <p><strong>Status:</strong> {"⚠️ Late Submission" if submission.status == "late" else "✅ On Time"}</p>
        </div>''',
        f'{BASE_URL}/assignments/{submission.assignment.pk}/',
        '✏️ Grade Submission'
    )
    send_real_email(teacher.email, f'New Submission: {submission.assignment.title}', html)


def email_new_quiz(quiz, students):
    """Notify students when a new quiz is posted."""
    for student in students:
        html = _base_email(
            f'<h2>🎯 New Quiz Available!</h2>',
            f'''<p>Hi <strong>{student.first_name}</strong>,</p>
            <p>A new quiz has been posted in <strong>{quiz.course.title}</strong>.</p>
            <div class="info">
              <p><strong>Quiz:</strong> {quiz.title}</p>
              <p><strong>Course:</strong> {quiz.course.title}</p>
              <p><strong>Questions:</strong> {quiz.questions.count()}</p>
              <p><strong>Time Limit:</strong> {"No limit" if not quiz.time_limit else f"{quiz.time_limit} minutes"}</p>
              <p><strong>Pass Score:</strong> {quiz.pass_score}%</p>
            </div>''',
            f'{BASE_URL}/quiz/{quiz.pk}/take/',
            '🎯 Take Quiz Now'
        )
        send_real_email(student.email, f'New Quiz: {quiz.title}', html)


def email_quiz_result(attempt):
    """Notify student of their quiz result."""
    student = attempt.student
    color = '#059669' if attempt.passed else '#dc2626'
    icon = '🎉' if attempt.passed else '📚'
    html = _base_email(
        f'<h2>{icon} Quiz Result: {attempt.quiz.title}</h2>',
        f'''<p>Hi <strong>{student.first_name}</strong>,</p>
        <p>Your quiz has been auto-graded. Here are your results:</p>
        <div class="info">
          <p><strong>Quiz:</strong> {attempt.quiz.title}</p>
          <p><strong>Score:</strong> <span style="color:{color};font-weight:700;font-size:18px">{attempt.score}/{attempt.total}</span></p>
          <p><strong>Percentage:</strong> <span style="color:{color};font-weight:700">{attempt.percentage}%</span></p>
          <p><strong>Grade:</strong> <span style="color:{color};font-weight:700">{attempt.grade_letter}</span></p>
          <p><strong>Result:</strong> <span style="color:{color};font-weight:700">{"✅ PASSED" if attempt.passed else "❌ Not Passed"}</span></p>
        </div>
        <p>{"Great job! Keep up the excellent work! 🌟" if attempt.passed else "Don't worry! Review the material and try again. 💪"}</p>''',
        f'{BASE_URL}/quiz/{attempt.quiz.pk}/result/',
        '📊 View Detailed Results'
    )
    send_real_email(student.email, f'Quiz Result: {attempt.quiz.title}', html)


def email_certificate_issued(cert):
    """Notify student when their certificate is issued."""
    student = cert.student
    html = _base_email(
        f'<h2>🎓 Certificate Issued!</h2>',
        f'''<p>Hi <strong>{student.first_name}</strong>,</p>
        <p>Congratulations! Your course completion certificate has been issued.</p>
        <div class="info">
          <p><strong>Course:</strong> {cert.course.title}</p>
          <p><strong>Instructor:</strong> {cert.course.teacher.get_full_name()}</p>
          <p><strong>Grade:</strong> {cert.grade}</p>
          <p><strong>Certificate ID:</strong> {cert.cert_id}</p>
          <p><strong>Issued:</strong> {cert.issued_at.strftime("%B %d, %Y")}</p>
        </div>
        <p>You can download your PDF certificate and share the verification link with employers!</p>''',
        f'{BASE_URL}/certificates/download/{cert.cert_id}/',
        '🏆 Download Certificate'
    )
    send_real_email(student.email, f'Certificate: {cert.course.title}', html)


def email_new_chat_message(message, recipient):
    """Notify user of a new chat message."""
    sender = message.sender
    html = _base_email(
        f'<h2>💬 New Message from {sender.get_full_name()}</h2>',
        f'''<p>Hi <strong>{recipient.first_name}</strong>,</p>
        <p>You have a new message in your SLMS inbox.</p>
        <div class="info">
          <p><strong>From:</strong> {sender.get_full_name()}</p>
          <p><strong>Course:</strong> {message.room.course.title}</p>
          <p><strong>Message:</strong> "{message.message[:200]}"</p>
        </div>
        <p>Log in to reply.</p>''',
        f'{BASE_URL}/chat/room/{message.room.pk}/',
        '💬 Reply Now'
    )
    send_real_email(recipient.email, f'New message from {sender.get_full_name()}', html)


def email_new_feedback(feedback):
    """Notify teacher of new student feedback."""
    teacher = feedback.teacher
    stars = '★' * feedback.rating + '☆' * (5 - feedback.rating)
    html = _base_email(
        f'<h2>⭐ New Student Feedback!</h2>',
        f'''<p>Hi <strong>{teacher.first_name}</strong>,</p>
        <p>A student has left feedback for your course.</p>
        <div class="info">
          <p><strong>Student:</strong> {feedback.student.get_full_name()}</p>
          <p><strong>Course:</strong> {feedback.course.title}</p>
          <p><strong>Rating:</strong> <span style="color:#f59e0b;font-size:18px">{stars}</span> ({feedback.rating}/5)</p>
          {"<p><strong>Comment:</strong> " + feedback.comment + "</p>" if feedback.comment else ""}
        </div>''',
        f'{BASE_URL}/feedback/my-feedback/',
        '⭐ View All Feedback'
    )
    send_real_email(teacher.email, f'New {feedback.rating}★ Feedback: {feedback.course.title}', html)


def email_welcome(user):
    """Send welcome email on registration."""
    role = user.role.capitalize()
    html = _base_email(
        f'<h2>🎉 Welcome to SLMS, {user.first_name}!</h2>',
        f'''<p>Hi <strong>{user.first_name}</strong>,</p>
        <p>Your <strong>{role}</strong> account has been created successfully on SLMS!</p>
        <div class="info">
          <p><strong>Username:</strong> {user.username}</p>
          <p><strong>Email:</strong> {user.email}</p>
          <p><strong>Role:</strong> {role}</p>
        </div>
        {"<p>Browse available courses and enroll to start learning today!</p>" if user.is_student else "<p>Create your first course and start teaching today!</p>"}''',
        f'{BASE_URL}/dashboard/',
        '🚀 Go to Dashboard'
    )
    send_real_email(user.email, f'Welcome to SLMS, {user.first_name}!', html)


def email_forum_reply(reply):
    """Notify post author when someone replies."""
    post = reply.post
    if post.author == reply.author:
        return  # Don't notify yourself
    html = _base_email(
        f'<h2>💬 New Reply on Your Post</h2>',
        f'''<p>Hi <strong>{post.author.first_name}</strong>,</p>
        <p><strong>{reply.author.get_full_name()}</strong> replied to your discussion post.</p>
        <div class="info">
          <p><strong>Post:</strong> {post.title}</p>
          <p><strong>Course:</strong> {post.course.title}</p>
          <p><strong>Reply:</strong> "{reply.body[:200]}"</p>
        </div>''',
        f'{BASE_URL}/forum/post/{post.pk}/',
        '💬 View Discussion'
    )
    send_real_email(post.author.email, f'New reply: {post.title}', html)
