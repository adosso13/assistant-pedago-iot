# config.py
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if GROQ_API_KEY is None:
    raise ValueError("ERREUR : GROQ_API_KEY est introuvable. Vérifiez votre fichier .env")
