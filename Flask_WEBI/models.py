from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

# ─── USER ────────────────────────────────────────────────────────────────────
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id       = db.Column(db.Integer, primary_key=True)
    email    = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    # Relations
    quiz_sessions    = db.relationship('QuizSession', backref='user', lazy=True)
    challenge_results = db.relationship('ChallengeResult', backref='user', lazy=True)
    submit_llm        = db.relationship('SubmitLLM', backref='user', lazy=True)  # ← ajoute

    def __repr__(self):
        return f'<User {self.email}>'


# ─── QUIZ SESSION ─────────────────────────────────────────────────────────────
class QuizSession(db.Model):
    __tablename__ = 'quiz_sessions'

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    score      = db.Column(db.Integer, nullable=False)
    total      = db.Column(db.Integer, nullable=False)
    date       = db.Column(db.DateTime, default=datetime.utcnow)

    # Relation vers les réponses
    answers    = db.relationship('QuizAnswer', backref='session', lazy=True)

    def __repr__(self):
        return f'<QuizSession user={self.user_id} score={self.score}/{self.total}>'


# ─── QUIZ ANSWER ──────────────────────────────────────────────────────────────
class QuizAnswer(db.Model):
    __tablename__ = 'quiz_answers'

    id              = db.Column(db.Integer, primary_key=True)
    session_id      = db.Column(db.Integer, db.ForeignKey('quiz_sessions.id'), nullable=False)
    question        = db.Column(db.Text, nullable=False)
    user_choice     = db.Column(db.String(1), nullable=False)   # A, B, C ou D
    correct_answer  = db.Column(db.String(1), nullable=False)
    is_correct      = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f'<QuizAnswer correct={self.is_correct}>'


# ─── CHALLENGE RESULT ─────────────────────────────────────────────────────────
class ChallengeResult(db.Model):
    __tablename__ = 'challenge_results'

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    question    = db.Column(db.Text, nullable=False)
    user_answer = db.Column(db.Text, nullable=False)
    correction  = db.Column(db.Text, nullable=False)
    date        = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ChallengeResult user={self.user_id}>'
    

# ─── SUBMIT RESULT ─────────────────────────────────────────────────────────
class SubmitLLM(db.Model):
    __tablename__ = 'submit_llm'

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    question    = db.Column(db.Text, nullable=False)
    answer      = db.Column(db.Text, nullable=False)
    date        = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<SubmitLLM user={self.user_id}>'