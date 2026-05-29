from app import app
from models import db, User
from werkzeug.security import generate_password_hash

with app.app_context():
    # 1. Créer l'objet
    new_user = User(
        email="moussa@gmail.com",
        password=generate_password_hash("123")
    )
    
    # 2. Ajouter à la session
    db.session.add(new_user)
    
    # 3. Sauvegarder
    db.session.commit()
    print(new_user.id, new_user.email)