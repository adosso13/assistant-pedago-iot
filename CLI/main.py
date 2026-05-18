import random
import sys
import os
# Ajoute le dossier parent au chemin de recherche
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent_LLM import agent
from sentence_transformers import SentenceTransformer
from groq import Groq

from config import GROQ_API_KEY

# ─── AFFICHAGE QCM ────────────────────────────────────────────────────────────
def display_qcm(qcm: dict, numero: int):
    print(f"\n{'─'*50}")
    print(f"Question {numero} : {qcm['question']}\n")
    for lettre, texte in qcm["choices"].items():
        print(f"  {lettre}) {texte}")
    print()

# ─── MENU PRINCIPAL ────────────────────────────────────────────────────────────
def menu():
    print("\n┌───────────────────────────────────────┐")
    print("│  1. Poser une question sur le PDF     │")
    print("│  2. Question ouverte + correction     │")
    print("│  3. Quiz QCM (5 questions max)        │")
    print("│  4. Quitter                           │")
    print("└───────────────────────────────────────┘")
    return input("Votre choix : ").strip()

def main():

    LLM = agent.AgentLLM()

    print("Chargement du PDF ...")
    chunks = LLM.load_pdf()
    print(f"{len(chunks)} chunks extraits")

    print("Création des embeddings ...")
    embedder = SentenceTransformer("all-MiniLM-L6-v2")
    index = LLM.build_index(chunks, embedder)

    client = Groq(api_key=GROQ_API_KEY)
    
    while True:
        choix = menu()

        # ── Mode 1 : Question libre ──
        if choix == "1":
            question = input("\nVotre question : ").strip()
            if not question:
                continue
            context = LLM.search(question, index, chunks, embedder)
            reponse = LLM.ask(question, context, client)
            print(f"\nRéponse :\n{reponse}\n")
            
        # ── Mode 2 : Question ouverte générée par le LLM ──
        elif choix == "2":
            chunk_aleatoire = random.choice(chunks)
            print("\nGénération d'une question...\n")
            question = LLM.generate_question(chunk_aleatoire, client)
            print(f"Question : {question}\n")
            user_answer = input("Votre réponse : ").strip()
            if not user_answer:
                continue
            context = LLM.search(question, index, chunks, embedder)
            correction = LLM.evaluate_answer(question, user_answer, context, client)
            print(f"\nCorrection :\n{correction}\n")

        # ── Mode 3 : Quiz QCM ──
        elif choix == "3":
            nb_questions = int(input("\nNombre de questions (1 à 5) : ").strip() or "5")
            nb_questions = max(1, min(5, nb_questions))

            score = 0
            historique = []  # stocke les QCM pour le corrigé final

            for i in range(1, nb_questions + 1):
                chunk_aleatoire = random.choice(chunks)
                print(f"\nGénération de la question {i}/{nb_questions}...")
                qcm = LLM.generate_qcm_question(chunk_aleatoire, client)
                display_qcm(qcm, i)

                user_choice = input("Votre réponse (A/B/C/D) : ").strip().upper()
                while user_choice not in ("A", "B", "C", "D"):
                    user_choice = input("Entrez A, B, C ou D : ").strip().upper()

                if user_choice == qcm["answer"]:
                    score += 1

                historique.append((qcm, user_choice))

            # ── Corrigé final ──
            print(f"\n{'─'*50}")
            print(f"RÉSULTAT : {score}/{nb_questions}")
            print(f"{'─'*50}")
            print("\nCORRIGÉ DÉTAILLÉ :\n")

            for i, (qcm, user_choice) in enumerate(historique, 1):
                print(f"\n{'─'*50}")
                print(f"Question {i} : {qcm['question']}")
                context = LLM.search(qcm["question"], index, chunks, embedder)
                correction = LLM.evaluate_qcm_answer(
                    qcm["question"], qcm["choices"],
                    qcm["answer"], user_choice, context, client
                )
                print(correction)

        # ── Quitter ──
        elif choix == "4":
            print("\nAu revoir !")
            break

main()