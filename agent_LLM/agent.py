import os
import sys
import PyPDF2
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from groq import Groq

class AgentLLM:
    
    # PDF_PATH     = "agent_LLM/static/BLE.pdf" # chemin vers le PDF
    PDF_PATH     = "/home/haroun/Bureau/Assistant-Pedago-iot/agent_LLM/static/BLE.pdf" # chemin vers le PDF
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

    def build_index(self, chunks: list, embedder: SentenceTransformer):
        """
        CRÉATION DE L'INDEX VECTORIEL (FAISS)
        """
        embeddings = embedder.encode(chunks, show_progress_bar=True)
        embeddings = np.array(embeddings, dtype="float32")
        index = faiss.IndexFlatL2(embeddings.shape[1])
        index.add(embeddings)
        return index

    def search(self, query: str, index, chunks: list, embedder: SentenceTransformer) -> str:
        """
        RECHERCHE DES CHUNKS PERTINENTS
        """
        query_vec = np.array(embedder.encode([query]), dtype="float32")
        _, indices = index.search(query_vec, self.TOP_K)
        return "\n\n---\n\n".join(chunks[int(i)] for i in indices[0])

    def ask(self, question: str, context: str, client: Groq) -> str:
        """
        APPEL À GROQ AVEC LE CONTEXTE RAG
        """
        response = client.chat.completions.create(
            model = self.MODEL,
            messages = [
                {
                    "role": "system",
                    "content": (
                        "Tu es un assistant expert. Réponds uniquement en te basant "
                        "sur le contexte fourni. Si la réponse n'est pas dans le contexte, "
                        "dis-le clairement."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Contexte extrait du PDF :\n{context}\n\nQuestion : {question}",
                },
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content

