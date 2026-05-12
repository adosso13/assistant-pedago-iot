import sys
import os
# Ajoute le dossier parent au chemin de recherche
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI
from agent_LLM import agent

app = FastAPI()

@app.get("/")
def root():
    LLM = agent.AgentLLM()
    return {"message": "Bonjour à tous"}