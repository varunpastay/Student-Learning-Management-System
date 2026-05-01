<div align="center">

# 📚 SLMS — Student Learning Management System

**A full-stack, production-ready Learning Management System built with Django**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.2-green?logo=django)](https://djangoproject.com)
[![DRF](https://img.shields.io/badge/DRF-3.14-red)](https://www.django-rest-framework.org)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple?logo=bootstrap)](https://getbootstrap.com)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

[Live Demo](#-deploy-in-one-click) · [Features](#-features) · [Setup](#-quick-start) · [API Docs](#-rest-api)

</div>

---

## ✨ Features

### 👤 Role-Based Access Control
| Role | Capabilities |
|------|-------------|
| **Student** | Browse & enroll in courses, submit assignments, track progress, view grades & feedback |
| **Teacher** | Create courses, upload materials, set assignments, grade submissions, view analytics |
| **Admin** | System-wide dashboard, manage all users/courses via Django Admin |

### 📖 Course Management
- Create courses with title, description, category, level, thumbnail, start/end dates
- Set max enrollment capacity — auto-closes when full
- Upload materials (PDF, video links, external links)
- Search & filter courses by category, level, and keyword

### 📝 Assignment System
- Create assignments with deadlines, total marks, and file attachments
- Students submit files (PDF, DOCX, ZIP, etc.) with optional notes
- Auto-detect **late submissions** and apply configurable **late penalty %**
- Teacher grades with marks + written feedback
- Students instantly notified when graded

### 🔔 Notification System
Real-time notifications auto-fired via Django Signals for:
- Course enrollment confirmation
- New assignment posted
- Assignment graded

### 📊 Dashboards & Analytics
- **Student**: enrolled courses with progress bars, upcoming deadlines, recent submissions
- **Teacher**: enrollment Chart.js graph, grading queue, submission inbox
- **Admin**: system-wide stats with charts, recent users & courses

### 🔌 REST API (20+ Endpoints)
- JWT Authentication (register, login, logout, refresh, `/me/`)
- Full CRUD for courses, assignments, submissions
- Role-scoped endpoints (teacher-only, student-only)
- Swagger UI at `/api/docs/` and ReDoc at `/api/redoc/`

---

## 🚀 Quick Start

### 1. Clone & Setup
```bash
git clone https://github.com/YOUR_USERNAME/slms-project.git
cd slms-project
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env — at minimum set SECRET_KEY and DEBUG=True
```

Generate a secret key:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 3. Run Migrations & Seed Demo Data
```bash
python manage.py migrate
python manage.py seed_demo        # Creates demo users, courses, assignments
python manage.py runserver
```

Open **http://127.0.0.1:8000**

### 4. Demo Login Credentials
| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `Admin@1234` |
| Teacher | `dr_alice` | `Teacher@1234` |
| Teacher | `prof_bob` | `Teacher@1234` |
| Student | `alice_s` | `Student@1234` |
| Student | `bob_s` | `Student@1234` |

---

## 🌐 Deploy in One Click

### Render (Free Tier)
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

1. Fork this repo
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect your forked repo
4. Render auto-detects `render.yaml` — click **Deploy**
5. Add env vars: `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS=yourapp.onrender.com`

### Railway
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template)

1. Fork this repo
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
3. `railway.toml` is pre-configured — add a PostgreSQL plugin
4. Set `SECRET_KEY` and `DATABASE_URL` env vars

### Manual VPS / Heroku
```bash
# Set environment variables
export SECRET_KEY="your-production-secret-key"
export DEBUG=False
export DATABASE_URL="postgresql://..."
export ALLOWED_HOSTS="yourdomain.com"
export CSRF_TRUSTED_ORIGINS="https://yourdomain.com"

# Collect static & migrate
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py seed_demo   # optional

# Start with gunicorn
gunicorn slms_project.wsgi --bind 0.0.0.0:8000 --workers 3
```

---

## 📁 Project Structure

```
slms_project/
├── accounts/              # Custom User model, roles, profiles, auth
│   ├── models.py          # User + StudentProfile + TeacherProfile
│   ├── views.py           # Register, Login, Logout, Profile, Password
│   ├── forms.py           # Registration & profile forms (Bootstrap-ready)
│   ├── permissions.py     # Role decorators + DRF permission classes
│   └── signals.py         # Auto-create profile on user creation
│
├── courses/               # Course management
│   ├── models.py          # Category, Course, Enrollment, CourseMaterial
│   ├── views.py           # CRUD + Enroll/Unenroll + search/filter
│   └── signals.py         # Enrollment → auto notification
│
├── assignments/           # Assignment & submission system
│   ├── models.py          # Assignment, Submission (file validation + late penalty)
│   └── views.py           # Create, submit, grade, notify
│
├── dashboard/             # Role-specific dashboards with Chart.js
├── notifications/         # Notification model + mark-read views
├── api/                   # Django REST Framework layer
│   ├── serializers/       # accounts, courses, assignments
│   └── views/             # JWT auth, CourseViewSet, AssignmentViewSet
│
├── templates/             # Global base.html + error pages
├── static/                # CSS / JS / images
├── Procfile               # Heroku/Railway process file
├── render.yaml            # Render deployment config
├── railway.toml           # Railway deployment config
├── runtime.txt            # Python version pin
└── requirements.txt       # All dependencies
```

---

## 🔌 REST API

Base URL: `/api/v1/`  
Docs: `/api/docs/` (Swagger) · `/api/redoc/`

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/auth/register/` | Register user | Public |
| POST | `/auth/login/` | Login → JWT tokens | Public |
| POST | `/auth/logout/` | Blacklist refresh token | Required |
| POST | `/auth/refresh/` | Refresh access token | Public |
| GET/PATCH | `/auth/me/` | Current user profile | Required |
| GET | `/courses/` | List published courses | Public |
| POST | `/courses/` | Create course | Teacher |
| GET | `/courses/{id}/` | Course detail | Public |
| POST | `/courses/{id}/enroll/` | Enroll in course | Student |
| GET | `/courses/my_courses/` | My courses | Required |
| GET | `/categories/` | List categories | Public |
| GET/POST | `/assignments/` | List / Create | Required |
| GET | `/assignments/{id}/submissions/` | View submissions | Teacher |
| GET/POST | `/submissions/` | List / Submit | Required |
| PATCH | `/submissions/{id}/grade/` | Grade submission | Teacher |

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 4.2 |
| REST API | Django REST Framework 3.14 |
| Auth | JWT (djangorestframework-simplejwt) + Session |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Static Files | WhiteNoise |
| Frontend | Bootstrap 5.3 + Bootstrap Icons + Chart.js |
| Forms | django-crispy-forms + crispy-bootstrap5 |
| API Docs | drf-yasg (Swagger UI + ReDoc) |
| Deployment | Gunicorn + Render / Railway / Heroku |

---

## 📸 Screenshots

| Student Dashboard | Teacher Dashboard | Course List |
|---|---|---|
| Enrolled courses, deadlines, submissions | Chart.js graphs, grading queue | Search, filter, paginate |

---

## 🤝 Contributing

1. Fork the repo
2. Create a branch: `git checkout -b feature/my-feature`
3. Commit: `git commit -m 'Add my feature'`
4. Push: `git push origin feature/my-feature`
5. Open a Pull Request

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">Built with ❤️ using Django · Bootstrap · DRF</div>
