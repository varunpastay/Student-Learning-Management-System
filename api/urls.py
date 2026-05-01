"""api/urls.py — All REST API v1 routes."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from api.views.accounts    import RegisterAPIView, LoginAPIView, LogoutAPIView, MeAPIView
from api.views.courses     import CourseViewSet, CategoryViewSet
from api.views.assignments import AssignmentViewSet, SubmissionViewSet

router = DefaultRouter()
router.register(r'courses',     CourseViewSet,     basename='course')
router.register(r'categories',  CategoryViewSet,   basename='category')
router.register(r'assignments', AssignmentViewSet, basename='assignment')
router.register(r'submissions', SubmissionViewSet, basename='submission')

urlpatterns = [
    # Auth endpoints
    path('auth/register/', RegisterAPIView.as_view(), name='api-register'),
    path('auth/login/',    LoginAPIView.as_view(),    name='api-login'),
    path('auth/logout/',   LogoutAPIView.as_view(),   name='api-logout'),
    path('auth/refresh/',  TokenRefreshView.as_view(), name='api-token-refresh'),
    path('auth/me/',       MeAPIView.as_view(),        name='api-me'),

    # Resource endpoints
    path('', include(router.urls)),
]

# ─── Endpoint Reference ──────────────────────────────────────────────────────
# POST   /api/v1/auth/register/          Register new user
# POST   /api/v1/auth/login/             Login → JWT tokens
# POST   /api/v1/auth/logout/            Logout (blacklist refresh)
# POST   /api/v1/auth/refresh/           Refresh access token
# GET    /api/v1/auth/me/                Get current user profile
# PATCH  /api/v1/auth/me/                Update current user profile
#
# GET    /api/v1/courses/                List published courses (search/filter)
# POST   /api/v1/courses/                Create course (teacher only)
# GET    /api/v1/courses/{id}/           Course detail
# PUT    /api/v1/courses/{id}/           Update course (teacher only)
# DELETE /api/v1/courses/{id}/           Delete course (teacher only)
# POST   /api/v1/courses/{id}/enroll/    Enroll in course
# POST   /api/v1/courses/{id}/unenroll/  Unenroll from course
# GET    /api/v1/courses/my_courses/     My courses (enrolled/taught)
#
# GET    /api/v1/categories/             List categories
#
# GET    /api/v1/assignments/            List assignments (role-filtered)
# POST   /api/v1/assignments/            Create assignment (teacher only)
# GET    /api/v1/assignments/{id}/       Assignment detail
# GET    /api/v1/assignments/{id}/submissions/  View submissions (teacher)
#
# GET    /api/v1/submissions/            List submissions (role-filtered)
# POST   /api/v1/submissions/            Submit assignment (student)
# PATCH  /api/v1/submissions/{id}/grade/ Grade submission (teacher)
