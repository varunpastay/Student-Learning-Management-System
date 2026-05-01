"""certificates/views.py — PDF certificate with grade based on overall performance."""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone
from .models import Certificate
from courses.models import Course, Enrollment
from assignments.models import Submission
from quiz.models import QuizAttempt
import io

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    REPORTLAB = True
except ImportError:
    REPORTLAB = False


def calculate_overall_grade(student, course):
    """
    Calculate grade based on ALL performance metrics:
    - Assignment average (50%)
    - Quiz average (30%)
    - Course progress (20%)
    Returns: grade letter, percentage, breakdown dict
    """
    # 1. Assignment performance
    submissions = Submission.objects.filter(
        student=student,
        assignment__course=course,
        status='graded'
    )
    if submissions.exists():
        assign_avg = sum(float(s.percentage or 0) for s in submissions) / submissions.count()
        assign_count = submissions.count()
    else:
        assign_avg = 0
        assign_count = 0

    # 2. Quiz performance
    attempts = QuizAttempt.objects.filter(
        student=student,
        quiz__course=course,
        completed_at__isnull=False
    )
    if attempts.exists():
        quiz_avg = sum(float(a.percentage or 0) for a in attempts) / attempts.count()
        quiz_count = attempts.count()
    else:
        quiz_avg = 0
        quiz_count = 0

    # 3. Course progress
    enrollment = Enrollment.objects.filter(student=student, course=course, is_active=True).first()
    progress = float(enrollment.progress or 0) if enrollment else 0

    # Weighted overall score
    if assign_count > 0 and quiz_count > 0:
        overall = (assign_avg * 0.50) + (quiz_avg * 0.30) + (progress * 0.20)
    elif assign_count > 0:
        overall = (assign_avg * 0.70) + (progress * 0.30)
    elif quiz_count > 0:
        overall = (quiz_avg * 0.70) + (progress * 0.30)
    else:
        overall = progress

    overall = round(overall, 1)

    # Grade letter
    if overall >= 90:   grade = 'A+'
    elif overall >= 85: grade = 'A'
    elif overall >= 80: grade = 'A-'
    elif overall >= 75: grade = 'B+'
    elif overall >= 70: grade = 'B'
    elif overall >= 65: grade = 'B-'
    elif overall >= 60: grade = 'C+'
    elif overall >= 55: grade = 'C'
    elif overall >= 50: grade = 'D'
    else:               grade = 'F'

    breakdown = {
        'assignment_avg': round(assign_avg, 1),
        'assignment_count': assign_count,
        'quiz_avg': round(quiz_avg, 1),
        'quiz_count': quiz_count,
        'progress': round(progress, 1),
        'overall': overall,
    }
    return grade, overall, breakdown


def generate_certificate_pdf(cert, breakdown=None):
    buffer = io.BytesIO()
    w, h = landscape(A4)
    c = canvas.Canvas(buffer, pagesize=landscape(A4))

    # Background
    c.setFillColor(colors.HexColor('#f5f3ff'))
    c.rect(0, 0, w, h, fill=1, stroke=0)

    # Outer border
    c.setStrokeColor(colors.HexColor('#4f46e5'))
    c.setLineWidth(8)
    c.rect(20, 20, w-40, h-40, fill=0, stroke=1)
    c.setLineWidth(2)
    c.setStrokeColor(colors.HexColor('#7c3aed'))
    c.rect(30, 30, w-60, h-60, fill=0, stroke=1)

    # Header
    c.setFillColor(colors.HexColor('#4f46e5'))
    c.setFont("Helvetica-Bold", 36)
    c.drawCentredString(w/2, h-90, "SLMS")
    c.setFont("Helvetica", 14)
    c.setFillColor(colors.HexColor('#7c3aed'))
    c.drawCentredString(w/2, h-115, "Student Learning Management System")

    # Title
    c.setFillColor(colors.HexColor('#1e293b'))
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(w/2, h-165, "Certificate of Completion")

    # Divider
    c.setStrokeColor(colors.HexColor('#4f46e5'))
    c.setLineWidth(1.5)
    c.line(w*0.2, h-182, w*0.8, h-182)

    # Body
    c.setFont("Helvetica", 14)
    c.setFillColor(colors.HexColor('#475569'))
    c.drawCentredString(w/2, h-210, "This is to certify that")

    c.setFont("Helvetica-Bold", 26)
    c.setFillColor(colors.HexColor('#4f46e5'))
    c.drawCentredString(w/2, h-248, cert.student.get_full_name())

    c.setFont("Helvetica", 14)
    c.setFillColor(colors.HexColor('#475569'))
    c.drawCentredString(w/2, h-275, "has successfully completed the course")

    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(colors.HexColor('#1e293b'))
    c.drawCentredString(w/2, h-308, f'"{cert.course.title}"')

    c.setFont("Helvetica", 12)
    c.setFillColor(colors.HexColor('#64748b'))
    c.drawCentredString(w/2, h-332, f"Taught by {cert.course.teacher.get_full_name()}")

    # Grade display
    if cert.grade:
        grade_color = '#059669' if cert.grade not in ['D','F'] else '#dc2626'
        c.setFillColor(colors.HexColor(grade_color))
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(w/2, h-362, f"Overall Grade: {cert.grade}")

    # Performance breakdown (small)
    if breakdown:
        c.setFont("Helvetica", 10)
        c.setFillColor(colors.HexColor('#94a3b8'))
        parts = []
        if breakdown['assignment_count'] > 0:
            parts.append(f"Assignments: {breakdown['assignment_avg']}%")
        if breakdown['quiz_count'] > 0:
            parts.append(f"Quizzes: {breakdown['quiz_avg']}%")
        parts.append(f"Progress: {breakdown['progress']}%")
        parts.append(f"Overall: {breakdown['overall']}%")
        c.drawCentredString(w/2, h-385, "  |  ".join(parts))

    # Footer
    c.setFont("Helvetica", 11)
    c.setFillColor(colors.HexColor('#94a3b8'))
    c.drawCentredString(w/2, 80, f"Issued on {cert.issued_at.strftime('%B %d, %Y')}")
    c.drawCentredString(w/2, 60, f"Certificate ID: {cert.cert_id}")
    c.drawCentredString(w/2, 40, "Verify at: student-learning-management-system.onrender.com/certificates/verify/")

    # Seal
    c.setFillColor(colors.HexColor('#4f46e5'))
    c.circle(w-100, 100, 50, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(w-100, 106, "SLMS")
    c.drawCentredString(w-100, 94, "CERTIFIED")

    c.save()
    buffer.seek(0)
    return buffer


@login_required
def issue_certificate(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    get_object_or_404(Enrollment, student=request.user, course=course, is_active=True)

    # Calculate grade based on overall performance
    grade, overall_pct, breakdown = calculate_overall_grade(request.user, course)

    cert, created = Certificate.objects.get_or_create(
        student=request.user,
        course=course,
        defaults={'grade': grade}
    )

    # Always update grade with latest performance
    if not created:
        cert.grade = grade
        cert.save()

    if created:
        try:
            from notifications.email_utils import email_certificate_issued
            email_certificate_issued(cert)
        except Exception:
            pass

    return redirect('certificates:download', cert_id=cert.cert_id)


@login_required
def download_certificate(request, cert_id):
    cert = get_object_or_404(Certificate, cert_id=cert_id, student=request.user)
    if not REPORTLAB:
        return HttpResponse("PDF library not available.", status=500)

    # Recalculate breakdown for PDF
    _, _, breakdown = calculate_overall_grade(cert.student, cert.course)
    buffer = generate_certificate_pdf(cert, breakdown)

    response = HttpResponse(buffer, content_type='application/pdf')
    safe_title = cert.course.title.replace(' ', '_').replace('/', '_')
    response['Content-Disposition'] = f'attachment; filename="SLMS_Certificate_{safe_title}.pdf"'
    return response


def verify_certificate(request, cert_id):
    """Public verification — no login required."""
    try:
        from uuid import UUID
        cert = Certificate.objects.select_related(
            'student', 'course', 'course__teacher'
        ).get(cert_id=UUID(str(cert_id)))
        _, _, breakdown = calculate_overall_grade(cert.student, cert.course)
        return render(request, 'certificates/verify.html', {
            'cert': cert, 'valid': True, 'breakdown': breakdown
        })
    except Exception:
        return render(request, 'certificates/verify.html', {'valid': False})


@login_required
def my_certificates(request):
    certs = Certificate.objects.filter(
        student=request.user
    ).select_related('course', 'course__teacher').order_by('-issued_at')

    # Add breakdown for each cert
    certs_data = []
    for cert in certs:
        _, overall, breakdown = calculate_overall_grade(cert.student, cert.course)
        # Update grade if changed
        new_grade = cert.grade
        if cert.grade != new_grade:
            cert.grade = new_grade
            cert.save()
        certs_data.append({'cert': cert, 'breakdown': breakdown})

    return render(request, 'certificates/my_certificates.html', {
        'certs_data': certs_data
    })
