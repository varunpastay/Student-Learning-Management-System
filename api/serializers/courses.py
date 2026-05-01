"""api/serializers/courses.py"""
from rest_framework import serializers
from courses.models import Category, Course, Enrollment, CourseMaterial
from api.serializers.accounts import UserSerializer


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model  = Category
        fields = ['id', 'name', 'slug', 'description', 'icon']


class CourseMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model  = CourseMaterial
        fields = ['id', 'title', 'material_type', 'file', 'url', 'description', 'order', 'uploaded_at']


class CourseSerializer(serializers.ModelSerializer):
    teacher       = UserSerializer(read_only=True)
    category      = CategorySerializer(read_only=True)
    category_id   = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True, required=False
    )
    enrolled_count = serializers.ReadOnlyField()
    is_full        = serializers.ReadOnlyField()

    class Meta:
        model  = Course
        fields = [
            'id', 'title', 'slug', 'description', 'teacher', 'category', 'category_id',
            'thumbnail', 'level', 'status', 'max_students', 'enrolled_count', 'is_full',
            'start_date', 'end_date', 'created_at',
        ]
        read_only_fields = ['slug', 'created_at', 'teacher']

    def create(self, validated_data):
        validated_data['teacher'] = self.context['request'].user
        return super().create(validated_data)


class EnrollmentSerializer(serializers.ModelSerializer):
    course  = CourseSerializer(read_only=True)
    student = UserSerializer(read_only=True)

    class Meta:
        model  = Enrollment
        fields = ['id', 'student', 'course', 'enrolled_at', 'is_active', 'progress', 'completed']
        read_only_fields = ['enrolled_at', 'student']
