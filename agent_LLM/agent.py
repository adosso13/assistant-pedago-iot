import os
import sys
import PyPDF2
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from groq import Groq
from config import PACKAGE_ROOT

class AgentLLM:
    
    PDF_PATH     = str(PACKAGE_ROOT) + "/agent_LLM/static/BLE.pdf" # chemin vers le PDF
    MODEL        = "llama-3.3-70b-versatile"  # ou "llama3-70b-8192" pour le grand modèle
    CHUNK_SIZE   = 500                        # taille des chunks en caractères
    TOP_K        = 3                          # nombre de chunks récupérés par requête
    
    def __init__(self):
        pass
    
    def load_pdf(self) -> list:
        """
        LECTURE ET DÉCOUPAGE DU PDF
        """
        chunks = []
        with open(self.PDF_PATH, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text = page.extract_text() or ""
                for i in range(0, len(text), self.CHUNK_SIZE):
                    chunk = text[i:i + self.CHUNK_SIZE].strip()
                    if chunk:
                        chunks.append(chunk)
        return chunks
    
    def build_index(self, chunks: list, embedder: SentenceTransformer, memory: bool = True,
            index_path: str = "index.faiss"):
        """
        CRÉATION DE L'INDEX VECTORIEL (FAISS)
        """
        if (os.path.exists(index_path) and memory ):
            print("Index FAISS trouvé, chargement depuis le fichier ...")
            index = faiss.read_index(index_path)
        else:
            print("Création de l'index FAISS (première fois uniquement) ...")
            embeddings = embedder.encode(chunks, show_progress_bar = False)
            embeddings = np.array(embeddings, dtype="float32")
            index = faiss.IndexFlatL2(embeddings.shape[1])
            index.add(embeddings)
            faiss.write_index(index, index_path)
            print(f"Index sauvegardé dans '{index_path}'")
        
        return index


    def search(self, query: str, index, chunks: list, embedder: SentenceTransformer) -> str:
        """
        RECHERCHE DES CHUNKS PERTINENTS
        """
        query_vec = np.array(embedder.encode([query]), dtype="float32")
        _, indices = index.search(query_vec, self.TOP_K)
        return "\n\n---\n\n".join(chunks[int(i)] for i in indices[0])

    
    def ask(self, question: str, context: str, history: list, client: Groq) -> str:
        """
        APPEL À GROQ AVEC LE CONTEXTE RAG
        """
        # 1. On définit le message système de base
        messages = [
            {
                "role": "system",
                "content": (
                    "Tu es un assistant expert. Réponds de manière conversationnelle en te basant "
                    "uniquement sur le contexte fourni et l'historique de la discussion. "
                    "Si la réponse n'est pas du tout dans le contexte ni dans l'historique, dis-le clairement."
                ),
            }
        ]
        
        # 2. On ajoute l'historique des échanges précédents s'il existe
        messages.extend(history)
        
        # 3. On prépare la nouvelle question de l'utilisateur enrichie du contexte PDF
        # Note : Intégrer le contexte ici permet au modèle de lier le document à la question actuelle
        new_user_message = {
            "role": "user",
            "content": f"Contexte extrait du PDF :\n{context}\n\nQuestion actuelle : {question}",
        }
        messages.append(new_user_message)
        
        # 4. Appel à l'API
        response = client.chat.completions.create(
            model = self.MODEL,
            messages = messages,
            temperature = 0.3, # Légèrement augmenté pour être un peu plus fluide dans la discussion
        )
        
        assistant_response = response.choices[0].message.content
        
        # 5. ON MET À JOUR L'HISTORIQUE POUR LE PROCHAIN TOUR
        # On stocke une version "propre" de la question (sans le bloc de contexte) pour ne pas saturer la mémoire
        history.append({"role": "user", "content": question})
        # history.append({"role": "assistant", "content": assistant_response})
        history.append({"role": "system", "content": assistant_response})
        
        return assistant_response

    def generate_question(self, context: str, client: Groq) -> str:
        """
        GÉNÉRER UNE QUESTION DEPUIS UN CHUNK
        """
        response = client.chat.completions.create(
            model = self.MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Tu es un professeur. À partir du contexte fourni, génère UNE SEULE "
                        "question claire et précise, sans donner la réponse. "
                        "Écris uniquement la question, rien d'autre."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Contexte :\n{context}\n\nGénère une question sur ce contenu.",
                },
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()

    def evaluate_answer(self, question: str, user_answer: str, context: str, client: Groq) -> str:
        """
        CORRIGER LA RÉPONSE DE L'UTILISATEUR
        """
        response = client.chat.completions.create(
            model = self.MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Tu es un professeur bienveillant. L'utilisateur a répondu à une question "
                        "basée sur un document. Évalue sa réponse en te basant UNIQUEMENT sur le contexte fourni. "
                        "Structure ta réponse ainsi :\n"
                        "Ce qui est correct\n"
                        "Ce qui manque ou est inexact\n"
                        "Complément d'information tiré du document"
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Contexte extrait du PDF :\n{context}\n\n"
                        f"Question posée : {question}\n"
                        f"Réponse de l'utilisateur : {user_answer}"
                    ),
                },
            ],
            temperature=0.3,
        )
        return response.choices[0].message.content

    def generate_qcm_question(self, context: str, client: Groq) -> dict:
        """
        GÉNÉRER UNE QUESTION QCM
        """
        # Retourne un dict : {question, choices: [A,B,C,D], answer: 'A'|'B'|'C'|'D'}
        response = client.chat.completions.create(
            model = self.MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Tu es un professeur. À partir du contexte fourni, génère UNE question QCM "
                        "avec exactement 4 choix (A, B, C, D), une seule réponse correcte. "
                        "Réponds UNIQUEMENT dans ce format strict, sans rien d'autre :\n"
                        "QUESTION: <la question>\n"
                        "A: <choix A>\n"
                        "B: <choix B>\n"
                        "C: <choix C>\n"
                        "D: <choix D>\n"
                        "REPONSE: <A ou B ou C ou D>"
                    ),
                },
                {
                    "role": "user",
                    "content": f"Contexte :\n{context}\n\nGénère une question QCM.",
                },
            ],
            temperature=0.7,
        )
        return self.parse_qcm(response.choices[0].message.content.strip())

    def parse_qcm(self, raw: str) -> dict:
        """
        Parse la réponse brute du LLM en dict structuré.
        """
        lines = {line.split(":")[0].strip(): ":".join(line.split(":")[1:]).strip() for line in raw.splitlines() if ":" in line}
        return {
            "question": lines.get("QUESTION", "Question non générée"),
            "choices": {
                "A": lines.get("A", ""),
                "B": lines.get("B", ""),
                "C": lines.get("C", ""),
                "D": lines.get("D", ""),
            },
            "answer": lines.get("REPONSE", "A").upper().strip(),
        }


    def evaluate_qcm_answer(self, question: str, choices: dict, correct: str, user_choice: str, context: str, client: Groq) -> str:
        
        if user_choice == correct:
            result = "Bonne réponse !"
        else:
            result = f"Mauvaise réponse. La bonne réponse était : ({correct}) {choices[correct]}"
        
        response = client.chat.completions.create(
            model = self.MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Tu es un professeur bienveillant. Apporte un complément d'information "
                        "basé UNIQUEMENT sur le contexte fourni, pour expliquer pourquoi "
                        "cette réponse est correcte ou non. Sois concis (3-4 phrases max)."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Contexte extrait du PDF :\n{context}\n\n"
                        f"Question : {question}\n"
                        f"Réponse correcte : {correct}) {choices[correct]}\n"
                        f"Réponse de l'utilisateur : {user_choice}) {choices.get(user_choice, '?')}\n"
                        "Explique et complète."
                    ),
                },
            ],
            temperature=0.3,
        )
        complement = response.choices[0].message.content.strip()
        return f"{result}\n\nExplication :\n{complement}"

