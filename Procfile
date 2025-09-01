release: python manage.py migrate && python create_superuser.py
web: gunicorn backend.wsgi --log-file -
