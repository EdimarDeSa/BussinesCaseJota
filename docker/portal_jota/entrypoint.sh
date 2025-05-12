#! /bin/sh

python manage.py makemigrations
python manage.py makemigrations api_portal_jota
python manage.py migrate

gunicorn -w 2 -b '0.0.0.0:8000' 'portal_jota.wsgi:application'