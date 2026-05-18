# API d'Évaluation et de Génération de Questions (RAG)

Ce projet est une API REST construite avec **FastAPI** qui exploite la puissance des Grands Modèles de Langage (LLM) via l'API **Groq** et de la recherche vectorielle (**RAG - Retrieval-Augmented Generation**) pour interagir intelligemment avec un document PDF. 

L'application permet d'automatiser la création de parcours pédagogiques ou de systèmes d'évaluation en générant des questions (ouvertes ou QCM) directement basées sur le contenu du document, puis en évaluant de manière contextuelle les réponses fournies par l'utilisateur.

---

## 🚀 Fonctionnalités Clés

* **Architecture RAG (Retrieval-Augmented Generation)** : Indexation complète d'un document PDF par découpage en blocs sémantiques (*chunks*) et génération d'embeddings vectoriels.
* **Recherche Sémantique Avancée** : Utilisation du modèle de pointe `all-MiniLM-L6-v2` pour projeter les requêtes et le contexte dans un espace vectoriel afin d'extraire les passages les plus pertinents.
* **Génération de Questions Ouvertes** : Analyse d'un bloc de texte aléatoire du PDF pour formuler une question ouverte pertinente grâce au LLM.
* **Génération de QCM** : Création automatique de Questions à Choix Multiples structurées contenant l'énoncé, plusieurs options de réponse et la solution correcte.
* **Évaluation Contextuelle (Réponses Ouvertes)** : Analyse et correction fine de la réponse textuelle de l'utilisateur en confrontant sa proposition avec le contexte extrait du PDF.
* **Validation de QCM** : Vérification automatisée de la réponse de l'utilisateur par rapport à la structure du QCM et validation de la cohérence par rapport au document source.
* **Mode Discussion (Question Answering)** : Interface de chat permettant de poser n'importe quelle question libre sur le document et d'obtenir une réponse sourcée.

---

## 🛠️ Architecture du Code & Cycle de Vie

Au démarrage de l'application :

1. **`LLM.load_pdf()`** : Le document PDF cible est chargé en mémoire, nettoyé et segmenté en blocs de texte (*chunks*).
2. **`SentenceTransformer("all-MiniLM-L6-v2")`** : Le modèle de re-ranking et d'embedding de phrases est instancié.
3. **`LLM.build_index(chunks, embedder)`** : Un index vectoriel est généré à partir de l'ensemble des blocs de texte pour permettre des requêtes à faible latence.

---

## 📦 Prérequis

### 1. Lancement de l'Application
Se positionner dans le repertoire FastAPI_REST

`source .venv/bin/activate`

`(venv) $ uvicorn main:app --reload`

Une fois le serveur démarré :

- Serveur local : `http://127.0.0.1:8000`
- Documentation interactive Swagger UI : `http://127.0.0.1:8000/docs`