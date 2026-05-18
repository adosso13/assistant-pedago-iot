import sys
import os
# Ajoute le dossier parent au chemin de recherche
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent_LLM import agent
from sentence_transformers import SentenceTransformer
from groq import Groq

from fastapi import FastAPI
from pydantic import BaseModel, Json
from typing import Any, Dict

from config import GROQ_API_KEY
import random

app = FastAPI()

class Form_Data(BaseModel):
    user_question: str
    user_answer: str
    qcm_question: Json[Dict[str, Any]]
    qcm_answer: str


LLM = agent.AgentLLM()
client = Groq(api_key=GROQ_API_KEY)

# Chargement du PDF
chunks = LLM.load_pdf()

# Création des embeddings
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# Création de l'index vectoriel
index = LLM.build_index(chunks, embedder)

@app.get("/generate_question")
def generate_question():
    
    # Pioche un chunk aléatoire comme base de la question
    chunk_aleatoire = random.choice(chunks)

    # Génération d'une question
    question = LLM.generate_question(chunk_aleatoire, client)
    
    return {"message": question}


@app.post("/evaluate_answer")
def evaluate_answer(data: Form_Data):
    
    question = data.user_question
    answer = data.user_answer
    
    # Recherche du contexte pertinent pour évaluer la réponse
    context = LLM.search(question, index, chunks, embedder)

    # Evaluation de la réponse
    correction = LLM.evaluate_answer(question, answer, context, client)
    
    return {"message": correction}


@app.post("/ask")
def ask_question(data: Form_Data):
    
    question = data.user_question
    
    # Recherche des chunks pertinents
    context = LLM.search(question, index, chunks, embedder)

    # Interrogation du PDF
    reponse = LLM.ask(question, context, client)
    
    return {"message": reponse}


@app.get("/generate_qcm_question")
def generate_qcm_question():
    
    # Pioche un chunk aléatoire comme base de la question
    chunk_aleatoire = random.choice(chunks)

    # Génération d'une question
    qcm = LLM.generate_qcm_question(chunk_aleatoire, client)
    
    return {"message": qcm}


@app.post("/evaluate_qcm_answer")
def evaluate_answer(data: Form_Data):
    
    qcm = data.qcm_question
    
    question = qcm["message"]["question"]
    choices = qcm["message"]["choices"]
    correct = qcm["message"]["answer"]

    answer = data.qcm_answer
    
    # Recherche du contexte pertinent pour évaluer la réponse
    context = LLM.search(question, index, chunks, embedder)

    # Evaluation de la réponse
    correction = LLM.evaluate_qcm_answer(question, choices, correct, answer, context, client)
    
    return {"message": correction}