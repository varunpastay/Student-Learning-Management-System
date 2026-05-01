"""api/views/assignments.py"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from assignments.models import Assignment, Submission
from api.serializers.assignments import AssignmentSerializer, SubmissionSerializer
from accounts.permissions import IsTeacherOrAdmin


class AssignmentViewSet(viewsets.ModelViewSet):
    serializer_class   = AssignmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_teacher:
            return Assignment.objects.filter(created_by=user)
        return Assignment.objects.filter(course__enrollments__student=user, course__enrollments__is_active=True)

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsTeacherOrAdmin()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['get'])
    def submissions(self, request, pk=None):
        """Teacher: view all submissions for an assignment."""
        assignment = self.get_object()
        if not request.user.is_teacher:
            return Response({'detail': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)
        subs = assignment.submissions.select_related('student').all()
        return Response(SubmissionSerializer(subs, many=True).data)


class SubmissionViewSet(viewsets.ModelViewSet):
    serializer_class   = SubmissionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_teacher:
            return Submission.objects.filter(assignment__created_by=user)
        return Submission.objects.filter(student=user)

    def perform_create(self, serializer):
        assignment = serializer.validated_data['assignment']
        if assignment.is_past_deadline and not assignment.allow_late:
            from rest_framework.exceptions import ValidationError
            raise ValidationError('Deadline has passed and late submissions are not allowed.')
        submission_status = Submission.Status.LATE if assignment.is_past_deadline else Submission.Status.SUBMITTED
        serializer.save(student=self.request.user, status=submission_status)

    @action(detail=True, methods=['patch'], permission_classes=[IsTeacherOrAdmin])
    def grade(self, request, pk=None):
        submission = self.get_object()
        marks    = request.data.get('marks_obtained')
        feedback = request.data.get('feedback', '')
        if marks is None:
            return Response({'detail': 'marks_obtained is required.'}, status=status.HTTP_400_BAD_REQUEST)
        submission.marks_obtained = marks
        submission.feedback       = feedback
        submission.status         = Submission.Status.GRADED
        submission.graded_by      = request.user
        submission.graded_at      = timezone.now()
        submission.save()
        return Response(SubmissionSerializer(submission).data)
