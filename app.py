import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from agent_LLM import agent
from sentence_transformers import SentenceTransformer
from groq import Groq


print("Initialisation de l'agent IoT...")
LLM = agent.AgentLLM()
chunks = LLM.load_pdf()
embedder = SentenceTransformer("all-MiniLM-L6-v2")
index = LLM.build_index(chunks, embedder)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


app = Flask(__name__)

load_dotenv()
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
# print(f"Ma clé est : {app.config['SECRET_KEY']}") # À supprimer après le test

# --- CONFIGURATION FLASK-LOGIN ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # Redirige ici si accès refusé
login_manager.login_message = "Veuillez vous connecter pour accéder à cette page."

# --- MOCK DATABASE (Pour l'exemple) ---
# Dans un vrai projet, utilisez SQLAlchemy et une vraie DB
users = {
    "1": {
        "id": "1",
        "email": "admin@example.com", # Changé de 'username' à 'email'
        "password": generate_password_hash("password123")
    }
}

class User(UserMixin):
    def __init__(self, id, email):
        self.id = id
        self.email = email


@login_manager.user_loader
def load_user(user_id):
    user_data = users.get(user_id)
    if not user_data:
        return None
    # On passe user_data['email'] au lieu de user_data['username']
    return User(user_data['id'], user_data['email'])

# --- ROUTES ---

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email') # On récupère l'email du formulaire
        password = request.form.get('password')
        
        # --- LA LIGNE CORRIGÉE ICI ---
        # On vérifie si l'EMAIL existe déjà (et non le username)
        if any(u.get('email') == email for u in users.values()):
            flash("Cet email est déjà utilisé.")
            return redirect(url_for('register'))
        
        # Création du nouvel utilisateur
        new_id = str(len(users) + 1)
        users[new_id] = {
            "id": new_id,
            "email": email, # On stocke bien l'email
            "password": generate_password_hash(password)
        }
        
        flash("Compte créé avec succès !")
        return redirect(url_for('login'))
        
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email') # On récupère l'email
        password = request.form.get('password')
        
        # Simulation de recherche en DB
        user_entry = next((u for u in users.values() if u['email'] == email), None)
        
        if user_entry and check_password_hash(user_entry['password'], password):
            user_obj = User(user_entry['id'], user_entry['email'])
            login_user(user_obj)
            return redirect(url_for('home'))
        
        flash('Identifiants incorrects')
    return render_template('login.html') # Créez ce template !


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/submit', methods=['POST'])
def submit():
    # 1. Récupérer la question du formulaire
    question = request.form.get('question')
    
    if not question:
        return redirect(url_for('home'))

    # 2. Utiliser la logique de ton main.py
    # On récupère le contexte via RAG
    context = LLM.search(question, index, chunks, embedder)
    
    # On génère la réponse avec le LLM
    reponse = LLM.ask(question, context, client)

    # 3. Envoyer la réponse au template HTML
    return render_template('response.html', question=question, reponse=reponse)


@app.route('/qcm')
@login_required # Seuls les connectés voient le QCM
def qcm():
    return render_template('qcm.html')


@app.route('/challenge')
@login_required # Seuls les connectés voient le challenge
def challenge():
    return render_template('challenge.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)