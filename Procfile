web: python manage.py migrate --no-input && python manage.py seed_demo && gunicorn slms_project.wsgi --bind 0.0.0.0:$PORT --workers 2 --timeout 120
