from app import app
from models import db, User
    
with app.app_context():
    # 1. Récupérer l'utilisateur
    user = User.query.get(1)
    
    # 2. Modifier le champ
    user.email = "test2@example.com"
    
    # 3. Sauvegarder
    db.session.commit()
    print(user.id, user.email)