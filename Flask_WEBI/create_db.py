from app import app, db
import models  # importe les modèles pour que SQLAlchemy les connaisse

with app.app_context():
    db.create_all()
    print("Base créée ✓")

