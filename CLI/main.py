import sys
import os
# Ajoute le dossier parent au chemin de recherche
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent_LLM import agent
from sentence_transformers import SentenceTransformer
from groq import Groq

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def main():

    LLM = agent.AgentLLM()

    print("Chargement du PDF...")
    chunks = LLM.load_pdf()
    print(f"   {len(chunks)} chunks extraits")

    print("Création des embeddings...")
    embedder = SentenceTransformer("all-MiniLM-L6-v2")
    index = LLM.build_index(chunks, embedder)

    client = Groq(api_key=GROQ_API_KEY)

    print("\nPrêt ! Posez vos questions (tapez 'quitter' pour arrêter)\n")
    while True:
        question = input("Votre question : ").strip()
        if question.lower() in ("quitter", "exit", "q"):
            break
        if not question:
            continue

        context = LLM.search(question, index, chunks, embedder)
        reponse = LLM.ask(question, context, client)
        print(f"\nRéponse :\n{reponse}\n")

main()