@echo off
cd E:\todo
call venv\Scripts\activate
python manage.py runserver 0.0.0.0:8000
