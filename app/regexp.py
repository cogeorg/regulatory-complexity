from app import app
from models import CorrectAnswer, db, Submission, User


@app.shell_context_processor
def make_shell_context():
    return {
        "db": db,
        "User": User,
        "Submission": Submission,
        "CorrectAnswer": CorrectAnswer,
    }
