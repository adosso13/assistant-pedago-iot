from app import app
from models import db, User

with app.app_context():
    # 1. Récupérer l'utilisateur
    user = db.session.get(User, 2)
    
    # 2. Supprimer
    db.session.delete(user)
    
    # 3. Sauvegarder
    db.session.commit()
    print(f"Utilisateur {user.id} ({user.email}) supprimé ✓")