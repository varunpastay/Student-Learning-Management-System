# SLMS — Student Learning Management System
## Setup & Run Guide

---

## 1. Project Setup Commands

```bash
# Step 1: Create virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# Step 2: Install dependencies
pip install -r requirements.txt

# Step 3: Create .env file (optional, defaults work for dev)
echo "SECRET_KEY=your-secret-key-here" > .env
echo "DEBUG=True" >> .env

# Step 4: Run migrations
python manage.py makemigrations accounts courses assignments notifications
python manage.py migrate

# Step 5: Create superuser
python manage.py createsuperuser

# Step 6: Run server
python manage.py runserver
```

Open: http://127.0.0.1:8000

---

## 2. Full Folder Structure

```
slms_project/
├── manage.py
├── requirements.txt
├── .env                          ← Environment variables
│
├── slms_project/                 ← Core Django config
│   ├── settings.py               ← All settings (DB, JWT, DRF, etc.)
│   ├── urls.py                   ← Root URL routing
│   ├── wsgi.py
│   └── asgi.py
│
├── accounts/                     ← Auth & Roles
│   ├── models.py                 ← User, StudentProfile, TeacherProfile
│   ├── views.py                  ← Register, Login, Logout, Profile
│   ├── forms.py                  ← Registration & login forms
│   ├── urls.py
│   ├── admin.py
│   ├── permissions.py            ← Role decorators + DRF permission classes
│   ├── signals.py                ← Auto-create profiles on user creation
│   └── templates/accounts/
│       ├── login.html
│       ├── register_student.html
│       └── register_teacher.html
│
├── courses/                      ← Course Management
│   ├── models.py                 ← Category, Course, Enrollment, CourseMaterial
│   ├── views.py                  ← CRUD + Enroll/Unenroll
│   ├── forms.py
│   ├── urls.py
│   ├── admin.py
│   ├── signals.py                ← Enrollment → auto notification
│   └── templates/courses/
│       ├── course_list.html      ← Search, filter, paginate
│       ├── course_detail.html
│       └── course_form.html
│
├── assignments/                  ← Assignment System
│   ├── models.py                 ← Assignment, Submission (with validators)
│   ├── views.py                  ← Create, submit, grade
│   ├── forms.py
│   ├── urls.py
│   ├── admin.py
│   ├── signals.py                ← Auto-notify on new assignment + grading
│   └── templates/assignments/
│       ├── assignment_list.html
│       ├── assignment_detail.html
│       ├── submit_assignment.html
│       └── grade_submission.html
│
├── dashboard/                    ← Role-specific dashboards
│   ├── views.py                  ← Student, Teacher, Admin dashboards
│   ├── urls.py
│   └── templates/dashboard/
│       ├── student_dashboard.html
│       ├── teacher_dashboard.html
│       └── admin_dashboard.html
│
├── notifications/                ← Alert System
│   ├── models.py                 ← Notification model
│   ├── views.py                  ← List, mark read, mark all read
│   ├── urls.py
│   ├── admin.py
│   ├── utils.py                  ← create_notification() helper
│   └── templates/notifications/
│       └── notification_list.html
│
├── api/                          ← Django REST Framework
│   ├── urls.py                   ← All API routes with inline docs
│   ├── serializers/
│   │   ├── accounts.py           ← User, Register, Login serializers
│   │   ├── courses.py            ← Course, Category, Enrollment
│   │   └── assignments.py        ← Assignment, Submission
│   └── views/
│       ├── accounts.py           ← JWT Register/Login/Logout/Me
│       ├── courses.py            ← CourseViewSet + enroll action
│       └── assignments.py        ← AssignmentViewSet + grade action
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── media/
│   ├── avatars/
│   ├── course_thumbnails/
│   ├── course_materials/
│   ├── assignment_attachments/
│   └── submissions/
│
└── templates/
    ├── base.html                 ← Global layout with navbar
    └── errors/
        ├── 403.html
        └── 404.html
```

---

## 3. Database Models & Relationships

```
User (CustomUser)
  ├── role: student | teacher | admin
  ├── StudentProfile (1:1) ← student_id, department, year, cgpa
  └── TeacherProfile (1:1) ← employee_id, department, specialization

Category ──< Course
               ├── teacher (FK → User[teacher])
               ├── CourseMaterial (1:N)
               └── Enrollment (M:M through table)
                     ├── student (FK → User[student])
                     └── progress, completed

Course ──< Assignment
               ├── created_by (FK → User[teacher])
               └── Submission (1:N)
                     ├── student (FK → User[student])
                     ├── status: pending|submitted|late|graded
                     ├── marks_obtained, feedback
                     └── graded_by (FK → User[teacher])

User ──< Notification
               ├── type: assignment|course|grade|system
               └── is_read
```

---

## 4. REST API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | /api/v1/auth/register/ | Register user | Public |
| POST | /api/v1/auth/login/ | Login → JWT tokens | Public |
| POST | /api/v1/auth/logout/ | Blacklist refresh token | Required |
| POST | /api/v1/auth/refresh/ | Refresh access token | Public |
| GET/PATCH | /api/v1/auth/me/ | Current user profile | Required |
| GET | /api/v1/courses/ | List courses (search/filter) | Public |
| POST | /api/v1/courses/ | Create course | Teacher |
| GET | /api/v1/courses/{id}/ | Course detail | Public |
| PUT/PATCH | /api/v1/courses/{id}/ | Update course | Teacher |
| DELETE | /api/v1/courses/{id}/ | Delete course | Teacher |
| POST | /api/v1/courses/{id}/enroll/ | Enroll in course | Student |
| POST | /api/v1/courses/{id}/unenroll/ | Unenroll | Student |
| GET | /api/v1/courses/my_courses/ | My courses | Required |
| GET | /api/v1/categories/ | List categories | Public |
| GET/POST | /api/v1/assignments/ | List / Create | Required |
| GET | /api/v1/assignments/{id}/submissions/ | View submissions | Teacher |
| GET/POST | /api/v1/submissions/ | List / Submit | Required |
| PATCH | /api/v1/submissions/{id}/grade/ | Grade submission | Teacher |
| GET | /api/docs/ | Swagger UI | Public |
| GET | /api/redoc/ | ReDoc API docs | Public |

---

## 5. Technologies Used

| Layer | Technology |
|-------|-----------|
| Backend | Django 4.2 |
| REST API | Django REST Framework 3.14 |
| Auth | JWT via djangorestframework-simplejwt |
| Database | SQLite (dev) / PostgreSQL (prod) |
| File Storage | Django MEDIA with Whitenoise for static |
| Frontend | Bootstrap 5.3 + Bootstrap Icons |
| Charts | Chart.js |
| Forms | django-crispy-forms + crispy-bootstrap5 |
| API Docs | drf-yasg (Swagger + ReDoc) |
| Task Queue | Celery + Redis (async email notifications) |

---

## 6. Resume-Ready Description

**Student Learning Management System (SLMS)**
*Django | DRF | JWT | Bootstrap 5 | PostgreSQL*

Designed and developed a full-stack, production-ready Learning Management System
serving students, teachers, and admins with role-based access control.

Key highlights:
- Built a custom Django User model with three distinct roles (Student, Teacher, Admin),
  each with extended profile models and automatic profile creation via Django signals.
- Implemented JWT authentication via Django REST Framework Simple JWT with token
  blacklisting on logout and role-scoped API permissions.
- Developed a Course Management module with category filtering, enrollment tracking,
  search/pagination, and progress tracking per student.
- Built a complete Assignment System with file upload validation (PDF, DOCX, ZIP),
  auto-status tracking (Submitted / Late / Graded), configurable late penalties, and
  teacher grading workflow.
- Engineered a real-time Notification System using Django signals to automatically
  alert students about new assignments, enrollment confirmations, and grades.
- Exposed 20+ REST API endpoints with filtering, search, ordering, and pagination;
  documented with Swagger UI and ReDoc.
- Designed role-specific dashboards (Student, Teacher, Admin) with analytics,
  Chart.js visualizations, and Bootstrap 5 responsive UI.

**GitHub:** github.com/yourusername/slms-project
**Live Demo:** (deploy on Railway / Render / Heroku)
