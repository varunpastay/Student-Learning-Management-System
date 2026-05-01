"""api/views/courses.py"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from courses.models import Course, Category, Enrollment
from api.serializers.courses import CourseSerializer, CategorySerializer, EnrollmentSerializer
from accounts.permissions import IsTeacherOrAdmin


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.filter(status='published').select_related('teacher', 'category')
    serializer_class = CourseSerializer
    filter_backends  = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['level', 'category__slug', 'status']
    search_fields    = ['title', 'description', 'teacher__first_name']
    ordering_fields  = ['created_at', 'title', 'enrolled_count']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsTeacherOrAdmin()]
        return [AllowAny()]

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def enroll(self, request, pk=None):
        course = self.get_object()
        if course.is_full:
            return Response({'detail': 'Course is full.'}, status=status.HTTP_400_BAD_REQUEST)
        enrollment, created = Enrollment.objects.get_or_create(
            student=request.user, course=course, defaults={'is_active': True}
        )
        if not created:
            return Response({'detail': 'Already enrolled.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(EnrollmentSerializer(enrollment).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def unenroll(self, request, pk=None):
        course = self.get_object()
        Enrollment.objects.filter(student=request.user, course=course).update(is_active=False)
        return Response({'detail': 'Unenrolled successfully.'})

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_courses(self, request):
        if request.user.is_teacher:
            courses = Course.objects.filter(teacher=request.user)
        else:
            courses = Course.objects.filter(
                enrollments__student=request.user, enrollments__is_active=True
            )
        serializer = self.get_serializer(courses, many=True)
        return Response(serializer.data)
