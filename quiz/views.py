"""quiz/views.py"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from .models import Quiz, Question, Choice, QuizAttempt, StudentAnswer
from .forms import QuizForm, QuestionForm, ChoiceFormSet
from courses.models import Enrollment


@login_required
def quiz_list(request):
    user = request.user
    if user.is_teacher:
        quizzes = Quiz.objects.filter(created_by=user).select_related('course')
    else:
        enrolled = Enrollment.objects.filter(student=user,is_active=True).values_list('course_id',flat=True)
        quizzes  = Quiz.objects.filter(course_id__in=enrolled,is_active=True).select_related('course')
    return render(request, 'quiz/quiz_list.html', {'quizzes': quizzes})


@login_required
def quiz_create(request):
    if not request.user.is_teacher:
        return redirect('quiz:list')
    if request.method == 'POST':
        form = QuizForm(request.POST, teacher=request.user)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.created_by = request.user
            quiz.save()
            messages.success(request, f'Quiz "{quiz.title}" created! Now add questions.')
            return redirect('quiz:add_question', quiz_id=quiz.id)
    else:
        form = QuizForm(teacher=request.user)
    return render(request, 'quiz/quiz_form.html', {'form': form, 'action': 'Create'})


@login_required
def add_question(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, created_by=request.user)
    if request.method == 'POST':
        qform = QuestionForm(request.POST)
        if qform.is_valid():
            question = qform.save(commit=False)
            question.quiz = quiz
            question.save()
            cformset = ChoiceFormSet(request.POST, instance=question)
            if cformset.is_valid():
                cformset.save()
                messages.success(request, 'Question added!')
                if 'add_more' in request.POST:
                    return redirect('quiz:add_question', quiz_id=quiz_id)
                return redirect('quiz:detail', quiz_id=quiz_id)
    else:
        qform = QuestionForm()
        cformset = ChoiceFormSet()
    return render(request, 'quiz/add_question.html', {'quiz': quiz, 'qform': qform, 'cformset': cformset})


@login_required
def quiz_detail(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    user = request.user
    attempt = QuizAttempt.objects.filter(quiz=quiz, student=user).first() if user.is_student else None
    questions = quiz.questions.prefetch_related('choices').all()
    all_attempts = QuizAttempt.objects.filter(quiz=quiz).select_related('student').order_by('-percentage') if user.is_teacher else None
    return render(request, 'quiz/quiz_detail.html', {
        'quiz': quiz, 'attempt': attempt, 'questions': questions, 'all_attempts': all_attempts,
    })


@login_required
def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, is_active=True)
    user = request.user
    if not user.is_student:
        return redirect('quiz:detail', quiz_id=quiz_id)
    if not Enrollment.objects.filter(student=user, course=quiz.course, is_active=True).exists():
        messages.error(request, 'Enroll in the course first.')
        return redirect('courses:detail', slug=quiz.course.slug)
    if QuizAttempt.objects.filter(quiz=quiz, student=user).exists():
        messages.info(request, 'You have already attempted this quiz.')
        return redirect('quiz:result', quiz_id=quiz_id)

    if request.method == 'POST':
        questions = quiz.questions.prefetch_related('choices').all()
        attempt = QuizAttempt.objects.create(quiz=quiz, student=user, total=questions.count())
        score = 0
        for q in questions:
            choice_id = request.POST.get(f'q_{q.id}')
            chosen = None
            correct = False
            if choice_id:
                try:
                    chosen = Choice.objects.get(id=choice_id, question=q)
                    correct = chosen.is_correct
                    if correct: score += q.marks
                except Choice.DoesNotExist:
                    pass
            StudentAnswer.objects.create(attempt=attempt, question=q, choice=chosen, is_correct=correct)
        total_marks = sum(q.marks for q in questions)
        pct = round((score / total_marks * 100), 2) if total_marks else 0
        attempt.score = score
        attempt.percentage = pct
        attempt.passed = pct >= quiz.pass_score
        attempt.completed_at = timezone.now()
        attempt.save()
        # Send result email
        try:
            from notifications.email_utils import email_quiz_result
            email_quiz_result(attempt)
        except Exception: pass
        return redirect('quiz:result', quiz_id=quiz_id)

    questions = quiz.questions.prefetch_related('choices').all()
    return render(request, 'quiz/take_quiz.html', {'quiz': quiz, 'questions': questions})


@login_required
def quiz_result(request, quiz_id):
    quiz    = get_object_or_404(Quiz, id=quiz_id)
    attempt = get_object_or_404(QuizAttempt, quiz=quiz, student=request.user)
    answers = attempt.answers.select_related('question','choice').prefetch_related('question__choices').all()
    return render(request, 'quiz/quiz_result.html', {'quiz': quiz, 'attempt': attempt, 'answers': answers})
