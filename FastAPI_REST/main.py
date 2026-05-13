import sys
import os
# Ajoute le dossier parent au chemin de recherche
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent_LLM import agent
from sentence_transformers import SentenceTransformer
from groq import Groq

from fastapi import FastAPI

from config import GROQ_API_KEY

app = FastAPI()

@app.get("/")
def root():
    LLM = agent.AgentLLM()
    
    # Chargement du PDF...
    chunks = LLM.load_pdf()

    # Création des embeddings...
    embedder = SentenceTransformer("all-MiniLM-L6-v2")
    index = LLM.build_index(chunks, embedder)

    client = Groq(api_key=GROQ_API_KEY)

    # question = input("Votre question : ").strip()
    question = "c'est quoi le BLE ?"
    
    context = LLM.search(question, index, chunks, embedder)
    reponse = LLM.ask(question, context, client)
    
    return {"message": reponse}