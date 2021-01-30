from app import app as application 
app = application

gunicorn wsgi:app