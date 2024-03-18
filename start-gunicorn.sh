#!/bin/bash

python manage.py migrate &&
python script.py &&

gunicorn --bind 0.0.0.0:8000 stockProject.wsgi:application
