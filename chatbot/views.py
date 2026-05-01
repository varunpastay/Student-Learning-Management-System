"""chatbot/views.py — AI chatbot for students using simple rule-based + keyword responses."""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json, re
from courses.models import Course, Enrollment
from assignments.models import Assignment, Submission
from django.utils import timezone


def get_bot_response(user, message):
    msg = message.lower().strip()

    # Greetings
    if any(w in msg for w in ['hello','hi','hey','good morning','good evening','howdy']):
        return f"👋 Hello {user.first_name}! I'm your SLMS assistant. How can I help you today?\n\nYou can ask me about your courses, assignments, deadlines, or grades!"

    # Enrolled courses
    if any(w in msg for w in ['my course','enrolled','what course','which course','my class']):
        enrollments = Enrollment.objects.filter(student=user, is_active=True).select_related('course')
        if enrollments.exists():
            course_list = '\n'.join([f"• {e.course.title} — {e.course.teacher.get_full_name()}" for e in enrollments])
            return f"📚 You are enrolled in **{enrollments.count()} course(s)**:\n\n{course_list}"
        return "You are not enrolled in any courses yet. Visit the Courses page to browse and enroll!"

    # Assignments / deadlines
    if any(w in msg for w in ['assignment','deadline','due','homework','task','pending']):
        enrolled_courses = Enrollment.objects.filter(student=user, is_active=True).values_list('course_id', flat=True)
        pending = Assignment.objects.filter(
            course_id__in=enrolled_courses, deadline__gte=timezone.now()
        ).exclude(submissions__student=user).order_by('deadline')[:5]
        if pending.exists():
            a_list = '\n'.join([f"• {a.title} ({a.course.title}) — Due: {a.deadline.strftime('%b %d, %Y')}" for a in pending])
            return f"📝 You have **{pending.count()} pending assignment(s)**:\n\n{a_list}"
        return "✅ Great news! You have no pending assignments right now."

    # Grades / marks
    if any(w in msg for w in ['grade','mark','score','result','how did i do','my result']):
        submissions = Submission.objects.filter(student=user, status='graded').select_related('assignment').order_by('-graded_at')[:5]
        if submissions.exists():
            g_list = '\n'.join([f"• {s.assignment.title}: {s.marks_obtained}/{s.assignment.total_marks} ({s.percentage}%)" for s in submissions])
            return f"⭐ Your recent grades:\n\n{g_list}"
        return "No graded submissions yet. Keep working on those assignments! 💪"

    # Progress
    if any(w in msg for w in ['progress','how am i doing','my progress','completion']):
        enrollments = Enrollment.objects.filter(student=user, is_active=True).select_related('course')
        if enrollments.exists():
            p_list = '\n'.join([f"• {e.course.title}: {e.progress}% complete" for e in enrollments])
            return f"📊 Your course progress:\n\n{p_list}"
        return "Enroll in courses first to track your progress!"

    # Teacher info
    if any(w in msg for w in ['teacher','instructor','professor','who teach']):
        enrollments = Enrollment.objects.filter(student=user, is_active=True).select_related('course__teacher')
        if enrollments.exists():
            t_list = '\n'.join([f"• {e.course.title} → {e.course.teacher.get_full_name()}" for e in enrollments])
            return f"👩‍🏫 Your teachers:\n\n{t_list}\n\nYou can chat with them via the Messages section!"
        return "You are not enrolled in any courses yet."

    # Help
    if any(w in msg for w in ['help','what can you do','commands','features','options']):
        return ("🤖 I can help you with:\n\n"
                "• **My courses** — list your enrolled courses\n"
                "• **Assignments** — show pending assignments & deadlines\n"
                "• **Grades** — check your recent grades\n"
                "• **Progress** — see course completion\n"
                "• **Teachers** — find your instructors\n"
                "• **Tips** — study tips and advice\n\n"
                "Just ask me anything! 😊")

    # Study tips
    if any(w in msg for w in ['tip','advice','study','how to learn','suggestion','help me study']):
        tips = [
            "📖 Break your study sessions into 25-minute focused blocks (Pomodoro technique)!",
            "🎯 Set a specific goal for each study session before you start.",
            "💡 Teach what you learn to someone else — it's the best way to retain knowledge!",
            "⏰ Review your notes within 24 hours of a lecture to improve retention by 80%.",
            "🏃 Take short breaks and exercise — physical activity boosts memory!",
        ]
        import random
        return random.choice(tips)

    # Motivation
    if any(w in msg for w in ['motivat','encourage','i give up','hard','difficult','struggling','fail']):
        return ("💪 Don't give up! Every expert was once a beginner.\n\n"
                "\"The secret of getting ahead is getting started.\" — Mark Twain\n\n"
                "You've got this! Check your assignments, reach out to your teacher, and take it one step at a time. 🌟")

    # Default
    return ("🤔 I'm not sure I understand that. Here are some things I can help with:\n\n"
            "• Type **my courses** to see your enrollments\n"
            "• Type **assignments** to check deadlines\n"
            "• Type **grades** to see your marks\n"
            "• Type **help** to see all options")


@login_required
def chatbot_view(request):
    return render(request, 'chatbot/chatbot.html')


@login_required
def chatbot_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', '').strip()
            if not message:
                return JsonResponse({'reply': 'Please type a message.'})
            reply = get_bot_response(request.user, message)
            return JsonResponse({'reply': reply})
        except Exception as e:
            return JsonResponse({'reply': 'Sorry, something went wrong. Please try again.'})
    return JsonResponse({'error': 'Method not allowed'}, status=405)
