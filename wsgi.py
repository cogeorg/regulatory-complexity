from app import app as application 
app = application

gunicorn app:app