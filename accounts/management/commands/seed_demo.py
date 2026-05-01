"""
Management command: python manage.py seed_demo
Seeds the database with demo users using REAL email addresses.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Seed the database with demo data for development/testing.'

    def handle(self, *args, **options):
        from accounts.models import User, StudentProfile, TeacherProfile
        from courses.models  import Category, Course, Enrollment, CourseMaterial
        from assignments.models import Assignment
        from notifications.models import Notification

        self.stdout.write(self.style.MIGRATE_HEADING('\n🌱  Seeding SLMS demo data...\n'))

        # ── Admin ────────────────────────────────────────────────────────────
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser('admin', 'varunnpastay@gmail.com', 'Admin@1234')
            admin.role = User.Role.ADMIN
            admin.first_name = 'Varun'; admin.last_name = 'Admin'
            admin.save()
            self.stdout.write('  ✔  Admin created  →  varunnpastay@gmail.com  /  Admin@1234')
        else:
            admin = User.objects.get(username='admin')
            admin.email = 'varunnpastay@gmail.com'
            admin.save()
            self.stdout.write('  ✔  Admin email updated  →  varunnpastay@gmail.com')

        # ── Teachers ─────────────────────────────────────────────────────────
        teachers_data = [
            ('dr_alice',  'Alice',  'Chen',   'varun23112003@gmail.com',  'Python & AI', 'PhD Computer Science'),
            ('prof_bob',  'Bob',    'Kumar',  'prof.bob@slms.edu',         'Algorithms',  'MSc Computer Science'),
            ('ms_carol',  'Carol',  'Singh',  'ms.carol@slms.edu',         'Web Dev',     'BTech IT'),
        ]
        teachers = []
        for uname, fn, ln, email, spec, qual in teachers_data:
            if not User.objects.filter(username=uname).exists():
                t = User.objects.create_user(uname, email, 'Teacher@1234',
                                             first_name=fn, last_name=ln, role=User.Role.TEACHER)
            else:
                t = User.objects.get(username=uname)
                t.email = email; t.save()
            TeacherProfile.objects.filter(user=t).update(
                department='Computer Science', specialization=spec, qualification=qual
            )
            teachers.append(t)
        self.stdout.write(f'  ✔  Teachers: dr_alice → varun23112003@gmail.com')

        # ── Students ──────────────────────────────────────────────────────────
        students_data = [
            ('alice_s', 'Alice', 'Johnson', 'varunvarunpastay@gmail.com'),
            ('bob_s',   'Bob',   'Martinez','bob.s@slms.edu'),
            ('charlie', 'Charlie','Lee',    'charlie@slms.edu'),
            ('diana',   'Diana', 'Patel',   'diana@slms.edu'),
            ('ethan',   'Ethan', 'Brown',   'ethan@slms.edu'),
            ('fiona',   'Fiona', 'Nguyen',  'fiona@slms.edu'),
        ]
        students = []
        for uname, fn, ln, email in students_data:
            if not User.objects.filter(username=uname).exists():
                s = User.objects.create_user(uname, email, 'Student@1234',
                                             first_name=fn, last_name=ln, role=User.Role.STUDENT)
            else:
                s = User.objects.get(username=uname)
                s.email = email; s.save()
            StudentProfile.objects.filter(user=s).update(department='Computer Science', year_of_study=2)
            students.append(s)
        self.stdout.write(f'  ✔  Students: alice_s → varunvarunpastay@gmail.com')

        # ── Categories ────────────────────────────────────────────────────────
        cats = {}
        for name, icon in [('Programming','code-slash'), ('Web Development','globe'),
                           ('Data Science','bar-chart'), ('Databases','database')]:
            cat, _ = Category.objects.get_or_create(name=name, defaults={'icon': icon, 'description': f'{name} courses'})
            cats[name] = cat

        # ── Courses ───────────────────────────────────────────────────────────
        courses_data = [
            ('Introduction to Python',       teachers[0], cats['Programming'],    'beginner',     'Learn Python from scratch.', 50),
            ('Data Structures & Algorithms', teachers[1], cats['Programming'],    'intermediate', 'Core CS concepts.',           40),
            ('Web Development Fundamentals', teachers[2], cats['Web Development'],'beginner',     'HTML, CSS, JS and Django.',   45),
            ('Database Management Systems',  teachers[1], cats['Databases'],      'intermediate', 'SQL, NoSQL and more.',        35),
            ('Machine Learning Basics',      teachers[0], cats['Data Science'],   'advanced',     'ML fundamentals.',            30),
        ]
        courses = []
        today = timezone.now().date()
        for title, teacher, cat, level, desc, maxs in courses_data:
            course, _ = Course.objects.get_or_create(
                title=title,
                defaults=dict(teacher=teacher, category=cat, level=level,
                              description=desc, max_students=maxs, status='published',
                              start_date=today - timedelta(days=14),
                              end_date=today + timedelta(days=90))
            )
            courses.append(course)

        # ── Enrollments ───────────────────────────────────────────────────────
        enroll_count = 0
        for i, student in enumerate(students):
            chosen = courses[i % len(courses): i % len(courses) + 3] or courses[:3]
            for course in chosen:
                _, created = Enrollment.objects.get_or_create(
                    student=student, course=course,
                    defaults={'is_active': True, 'progress': (i * 17 + 10) % 90}
                )
                if created: enroll_count += 1

        # ── Assignments ───────────────────────────────────────────────────────
        now = timezone.now()
        for course, creator, title, deadline, marks in [
            (courses[0], teachers[0], 'Python Basics Quiz',        now + timedelta(days=7),  20),
            (courses[0], teachers[0], 'Functions & OOP Lab',       now + timedelta(days=14), 50),
            (courses[1], teachers[1], 'Sorting Algorithms Report', now + timedelta(days=5),  40),
            (courses[2], teachers[2], 'Portfolio Website',         now + timedelta(days=21), 100),
        ]:
            Assignment.objects.get_or_create(
                title=title, course=course,
                defaults=dict(created_by=creator, description=f'Complete: {title}',
                              deadline=deadline, total_marks=marks, allow_late=True, late_penalty=5)
            )

        # ── Notifications ─────────────────────────────────────────────────────
        for student in students[:3]:
            for course in courses[:2]:
                if not Notification.objects.filter(user=student, title__contains=course.title).exists():
                    Notification.objects.create(
                        user=student,
                        title=f'Welcome to {course.title}!',
                        message=f'You are enrolled in {course.title}.',
                        notification_type='course'
                    )

        self.stdout.write(self.style.SUCCESS(
            '\n✅  Demo data seeded!\n'
            '\n   📧 Real email accounts:\n'
            '   Student: alice_s  /  Student@1234  →  varunvarunpastay@gmail.com\n'
            '   Teacher: dr_alice /  Teacher@1234  →  varun23112003@gmail.com\n'
            '   Admin:   admin    /  Admin@1234    →  varunnpastay@gmail.com\n'
            '\n   Run: python manage.py runserver\n'
        ))
