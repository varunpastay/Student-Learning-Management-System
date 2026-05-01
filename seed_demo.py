"""
Management command: python manage.py seed_demo
Seeds the database with demo users, courses, assignments, and notifications.
"""
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'slms_project.settings')

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Seed the database with demo data for development/testing.'

    def handle(self, *args, **options):
        from accounts.models import User, StudentProfile, TeacherProfile
        from courses.models  import Category, Course, Enrollment, CourseMaterial
        from assignments.models import Assignment, Submission
        from notifications.models import Notification

        self.stdout.write(self.style.MIGRATE_HEADING('\n🌱  Seeding SLMS demo data...\n'))

        # ── Admin ────────────────────────────────────────────────────────────
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser('admin', 'admin@slms.edu', 'Admin@1234')
            admin.role = User.Role.ADMIN
            admin.first_name = 'System'; admin.last_name = 'Admin'
            admin.save()
            self.stdout.write('  ✔  Admin user created  (admin / Admin@1234)')

        # ── Teachers ─────────────────────────────────────────────────────────
        teachers_data = [
            ('dr_alice',  'Alice',  'Chen',   'alice@slms.edu',  'Python & AI', 'PhD Computer Science'),
            ('prof_bob',  'Bob',    'Kumar',  'bob@slms.edu',    'Algorithms',  'MSc Computer Science'),
            ('ms_carol',  'Carol',  'Singh',  'carol@slms.edu',  'Web Dev',     'BTech IT'),
        ]
        teachers = []
        for uname, fn, ln, email, spec, qual in teachers_data:
            if not User.objects.filter(username=uname).exists():
                t = User.objects.create_user(uname, email, 'Teacher@1234',
                                             first_name=fn, last_name=ln, role=User.Role.TEACHER)
                TeacherProfile.objects.filter(user=t).update(
                    department='Computer Science', specialization=spec, qualification=qual
                )
            teachers.append(User.objects.get(username=uname))
        self.stdout.write(f'  ✔  {len(teachers)} teachers created')

        # ── Students ──────────────────────────────────────────────────────────
        students_data = [
            ('alice_s', 'Alice', 'Johnson', 'alice.s@slms.edu'),
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
                StudentProfile.objects.filter(user=s).update(department='Computer Science', year_of_study=2)
            students.append(User.objects.get(username=uname))
        self.stdout.write(f'  ✔  {len(students)} students created')

        # ── Categories ────────────────────────────────────────────────────────
        cats = {}
        for name, icon in [('Programming','code-slash'), ('Web Development','globe'), ('Data Science','bar-chart'), ('Databases','database')]:
            cat, _ = Category.objects.get_or_create(name=name, defaults={'icon': icon, 'description': f'{name} courses'})
            cats[name] = cat
        self.stdout.write(f'  ✔  {len(cats)} categories created')

        # ── Courses ───────────────────────────────────────────────────────────
        courses_data = [
            ('Introduction to Python',          teachers[0], cats['Programming'],    'beginner',     'Learn Python from scratch. Variables, loops, functions, OOP.',  50),
            ('Data Structures & Algorithms',    teachers[1], cats['Programming'],    'intermediate', 'Arrays, linked lists, trees, sorting and graph algorithms.',    40),
            ('Web Development Fundamentals',    teachers[2], cats['Web Development'],'beginner',     'HTML, CSS, JavaScript, and Django basics.',                     45),
            ('Database Management Systems',     teachers[1], cats['Databases'],      'intermediate', 'SQL, normalization, transactions, and NoSQL databases.',        35),
            ('Machine Learning Basics',         teachers[0], cats['Data Science'],   'advanced',     'Supervised learning, neural networks, model evaluation.',       30),
        ]
        courses = []
        today = timezone.now().date()
        for title, teacher, cat, level, desc, maxs in courses_data:
            course, created = Course.objects.get_or_create(
                title=title,
                defaults=dict(teacher=teacher, category=cat, level=level,
                              description=desc, max_students=maxs,
                              status='published',
                              start_date=today - timedelta(days=14),
                              end_date=today + timedelta(days=90))
            )
            courses.append(course)
        self.stdout.write(f'  ✔  {len(courses)} courses created')

        # ── Materials ─────────────────────────────────────────────────────────
        for c in courses[:3]:
            if not c.materials.exists():
                CourseMaterial.objects.create(course=c, title='Course Syllabus', material_type='link',
                                              url='https://example.com/syllabus', order=1)
                CourseMaterial.objects.create(course=c, title='Lecture Slides Week 1', material_type='link',
                                              url='https://example.com/slides', order=2)
        self.stdout.write('  ✔  Course materials added')

        # ── Enrollments ───────────────────────────────────────────────────────
        import itertools
        enroll_count = 0
        for i, student in enumerate(students):
            chosen = courses[i % len(courses): i % len(courses) + 3] or courses[:3]
            for course in chosen:
                _, created = Enrollment.objects.get_or_create(
                    student=student, course=course,
                    defaults={'is_active': True, 'progress': (i * 17 + 10) % 90}
                )
                if created:
                    enroll_count += 1
        self.stdout.write(f'  ✔  {enroll_count} enrollments created')

        # ── Assignments ───────────────────────────────────────────────────────
        now = timezone.now()
        assignments_data = [
            (courses[0], teachers[0], 'Python Basics Quiz',         now + timedelta(days=7),  20),
            (courses[0], teachers[0], 'Functions & OOP Lab',        now + timedelta(days=14), 50),
            (courses[0], teachers[0], 'Final Python Project',       now + timedelta(days=30), 100),
            (courses[1], teachers[1], 'Sorting Algorithms Report',  now + timedelta(days=5),  40),
            (courses[1], teachers[1], 'Tree Traversal Lab',         now - timedelta(days=3),  60),  # past
            (courses[2], teachers[2], 'Portfolio Website',          now + timedelta(days=21), 100),
            (courses[3], teachers[1], 'ER Diagram Exercise',        now + timedelta(days=10), 30),
            (courses[4], teachers[0], 'Linear Regression Report',   now - timedelta(days=7),  50),  # past
        ]
        asgn_objs = []
        for course, creator, title, deadline, marks in assignments_data:
            a, _ = Assignment.objects.get_or_create(
                title=title, course=course,
                defaults=dict(created_by=creator, description=f'Complete the {title} task.',
                              deadline=deadline, total_marks=marks,
                              allow_late=True, late_penalty=5)
            )
            asgn_objs.append(a)
        self.stdout.write(f'  ✔  {len(asgn_objs)} assignments created')

        # ── Submissions ───────────────────────────────────────────────────────
        # We can't create real file uploads in seed, so skip file-based submissions
        self.stdout.write('  ℹ  Submissions require file uploads (skipped in seed)')

        # ── Notifications ─────────────────────────────────────────────────────
        notif_count = 0
        for student in students[:3]:
            for course in courses[:2]:
                if not Notification.objects.filter(user=student, title__contains=course.title).exists():
                    Notification.objects.create(
                        user=student,
                        title=f'Welcome to {course.title}!',
                        message=f'You are enrolled in {course.title}. Check course materials and upcoming assignments.',
                        notification_type='course'
                    )
                    notif_count += 1
        for student in students[:4]:
            if not Notification.objects.filter(user=student, notification_type='assignment').exists():
                Notification.objects.create(
                    user=student,
                    title='New Assignment: Python Basics Quiz',
                    message='A new assignment has been posted in Introduction to Python. Due in 7 days.',
                    notification_type='assignment'
                )
                notif_count += 1
        self.stdout.write(f'  ✔  {notif_count} notifications created')

        self.stdout.write(self.style.SUCCESS(
            '\n✅  Demo data seeded successfully!\n'
            '\n   Login credentials:\n'
            '   Admin:   admin     / Admin@1234\n'
            '   Teacher: dr_alice  / Teacher@1234\n'
            '   Teacher: prof_bob  / Teacher@1234\n'
            '   Student: alice_s   / Student@1234\n'
            '   Student: bob_s     / Student@1234\n'
            '\n   Run: python manage.py runserver\n'
        ))
