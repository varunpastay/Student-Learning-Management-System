"""api/serializers/assignments.py"""
from rest_framework import serializers
from assignments.models import Assignment, Submission
from api.serializers.courses import CourseSerializer
from api.serializers.accounts import UserSerializer


class AssignmentSerializer(serializers.ModelSerializer):
    course         = CourseSerializer(read_only=True)
    is_past_deadline = serializers.ReadOnlyField()
    days_remaining   = serializers.ReadOnlyField()

    class Meta:
        model  = Assignment
        fields = [
            'id', 'course', 'title', 'description', 'deadline', 'total_marks',
            'allow_late', 'late_penalty', 'attachment',
            'is_past_deadline', 'days_remaining', 'created_at',
        ]
        read_only_fields = ['created_at']


class SubmissionSerializer(serializers.ModelSerializer):
    student        = UserSerializer(read_only=True)
    effective_marks = serializers.ReadOnlyField()

    class Meta:
        model  = Submission
        fields = [
            'id', 'assignment', 'student', 'file', 'notes', 'status',
            'submitted_at', 'marks_obtained', 'effective_marks', 'feedback',
            'graded_at', 'graded_by',
        ]
        read_only_fields = ['student', 'submitted_at', 'graded_at', 'graded_by', 'status']

    def create(self, validated_data):
        validated_data['student'] = self.context['request'].user
        return super().create(validated_data)
