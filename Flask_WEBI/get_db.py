from app import app
from models import db, User

with app.app_context():
    users = User.query.all()
    for u in users:
        print(u.id, u.email)


