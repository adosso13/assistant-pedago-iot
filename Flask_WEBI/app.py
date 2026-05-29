import os
import random  # Nécessaire pour piocher des morceaux de texte au hasard
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, session  # Ajout de session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from agent_LLM import agent
from sentence_transformers import SentenceTransformer
from groq import Groq
from models import db, User, QuizSession, QuizAnswer

load_dotenv()

print("Initialisation de l'agent IoT...")
LLM = agent.AgentLLM()
chunks = LLM.load_pdf()
embedder = SentenceTransformer("all-MiniLM-L6-v2")
index = LLM.build_index(chunks, embedder)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Chemin absolu vers Flask_WEBI/instance/app.db
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False         # ← ajout

db.init_app(app)  # ← lier db à l'app

# --- CONFIGURATION FLASK-LOGIN ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = "Veuillez vous connecter pour accéder à cette page."

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  # ← requête SQLite

# --- ROUTES DE BASE ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email    = request.form.get('email')
        password = request.form.get('password')

        if User.query.filter_by(email=email).first():  # ← vérif en BDD
            flash("Cet email est déjà utilisé.")
            return redirect(url_for('register'))

        new_user = User(email=email, password=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        flash("Compte créé avec succès !")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email    = request.form.get('email')
        password = request.form.get('password')
        user     = User.query.filter_by(email=email).first()  # ← requête BDD

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))

        flash('Identifiants incorrects')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# --- MODE 1 : RECHERCHE / QUESTION LIBRE ---
@app.route('/submit', methods=['POST'])
def submit():
    question = request.form.get('question')
    if not question:
        return redirect(url_for('home'))

    context = LLM.search(question, index, chunks, embedder)
    reponse = LLM.ask(question, context, client)
    return render_template('response.html', question=question, reponse=reponse)


# ─── MODE 2 : CHALLENGE (QUESTION OUVERTE) ───
@app.route('/challenge', methods=['GET', 'POST'])
def challenge():
    if request.method == 'POST':
        # L'utilisateur soumet sa réponse textuelle
        question = request.form.get('question')
        user_answer = request.form.get('user_answer')
        
        context = LLM.search(question, index, chunks, embedder)
        correction = LLM.evaluate_answer(question, user_answer, context, client)
        
        return render_template('challenge_result.html', question=question, user_answer=user_answer, correction=correction)
    
    # En GET : on génère une question ouverte à partir d'un chunk aléatoire
    chunk_aleatoire = random.choice(chunks)
    question = LLM.generate_question(chunk_aleatoire, client)
    return render_template('challenge.html', question=question)


# ─── MODE 3 : QUIZ QCM SIMULÉ (5 QUESTIONS) ───
@app.route('/qcm', methods=['GET', 'POST'])
def qcm():
    # Accès initial (GET) -> On prépare une liste de 5 questions QCM dans la session
    if request.method == 'GET':
        session['qcm_score'] = 0
        session['qcm_index'] = 0
        session['qcm_questions'] = []
        session['qcm_historique'] = []

        for _ in range(5):
            chunk = random.choice(chunks)
            qcm_data = LLM.generate_qcm_question(chunk, client)
            session['qcm_questions'].append(qcm_data)
        
        session.modified = True

    # Soumission d'une réponse (POST)
    if request.method == 'POST':
        user_choice = request.form.get('choice')
        current_idx = session.get('qcm_index', 0)
        questions = session.get('qcm_questions', [])
        
        if current_idx < len(questions):
            qcm_actuel = questions[current_idx]
            
            if user_choice == qcm_actuel.get('answer'):
                session['qcm_score'] += 1
            
            session['qcm_historique'].append({
                'question': qcm_actuel['question'],
                'choices': qcm_actuel['choices'],
                'answer': qcm_actuel['answer'],
                'user_choice': user_choice
            })
            
            session['qcm_index'] += 1
            session.modified = True

    # Détermination de la vue : question suivante ou page de résultats
    current_idx = session.get('qcm_index', 0)
    questions = session.get('qcm_questions', [])

    if current_idx >= len(questions):
        # Fin du quiz : calcul et récupération des corrections RAG détaillées
        score_final = session.get('qcm_score', 0)
        total_questions = len(questions)
        historique = session.get('qcm_historique', [])
        
        for item in historique:
            context = LLM.search(item['question'], index, chunks, embedder)
            item['correction'] = LLM.evaluate_qcm_answer(
                item['question'], item['choices'],
                item['answer'], item['user_choice'], context, client
            )
            
        # Nettoyage
        session.pop('qcm_questions', None)
        return render_template('qcm_result.html', score=score_final, total=total_questions, historique=historique)

    qcm_actuel = questions[current_idx]
    return render_template('qcm.html', qcm=qcm_actuel, numero=current_idx + 1)


if __name__ == '__main__':
    # use_reloader=False évite que l'agent s'initialise 2 fois de suite au démarrage en mode debug
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)