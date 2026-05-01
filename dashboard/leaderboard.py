"""dashboard/leaderboard.py — Compute student rankings."""
from django.db.models import Avg, Count, Q
from assignments.models import Submission
from courses.models import Enrollment
from accounts.models import User


def get_leaderboard(limit=20):
    students = User.objects.filter(role='student', is_active=True)
    board = []
    for s in students:
        submissions = Submission.objects.filter(student=s, status='graded')
        avg_grade = submissions.aggregate(Avg('marks_obtained'))['marks_obtained__avg'] or 0
        sub_count  = submissions.count()
        courses    = Enrollment.objects.filter(student=s, is_active=True).count()
        # Score: weighted by avg grade and engagement
        score = round(avg_grade * 0.7 + sub_count * 2 + courses * 3, 1)
        board.append({
            'student': s, 'avg_grade': round(avg_grade, 1),
            'submissions': sub_count, 'courses': courses, 'score': score,
        })
    board.sort(key=lambda x: x['score'], reverse=True)
    return board[:limit]
