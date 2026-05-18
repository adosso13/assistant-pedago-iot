# Moteur d'Évaluation et d'Apprentissage Interactif basé sur un PDF (RAG)

Ce projet implémente une application interactive en ligne de commande (CLI) qui utilise l'architecture **RAG (Retrieval-Augmented Generation)** pour interagir avec un document PDF. En combinant la recherche sémantique locale avec la puissance des LLM via l'API **Groq**, l'application permet de poser des questions libres, de générer des questions ouvertes avec correction personnalisée, ou de participer à un quiz sous forme de QCM.

## 🚀 Fonctionnalités Clés

* **Architecture RAG complète** :
  * Chargement et découpage sémantique du fichier PDF en blocs de texte (*chunks*).
  * Génération d'embeddings vectoriels à l'aide du modèle `all-MiniLM-L6-v2` (*SentenceTransformers*).
  * Indexation et recherche de contexte par similarité pour alimenter le LLM avec les informations exactes du document.
* **Mode 1 : Discussion Libre (Question-Answering)** : Posez n'importe quelle question sur le document et obtenez une réponse précise et sourcée basée sur le contexte extrait.
* **Mode 2 : Évaluation par Question Ouverte** : L'application sélectionne un extrait aléatoire du PDF, génère une question complexe et évalue intelligemment la réponse textuelle que vous formulez.
* **Mode 3 : Quiz QCM Interactif (1 à 5 questions)** : 
  * Génération dynamique de QCM (questions et options A, B, C, D) à partir du PDF.
  * Calcul du score en temps réel.
  * Corrigé final détaillé et argumenté généré par le LLM pour chaque question du quiz à partir du contexte textuel.

---

## 🛠️ Architecture et Fichiers

Le script principal s'appuie sur une structure modulaire :
* **`main.py`** : Point d'entrée de l'application gérant la CLI, la boucle principale et l'orchestration des flux de données.
* **`agent_LLM/agent.py`** : Contient la classe `AgentLLM` responsable du traitement du PDF, de la gestion de l'index vectoriel et des interactions de prompts avec Groq.
* **`config.py`** : Stocke les configurations de l'application, notamment la clé de l'API Groq.

---

## 📦 Prérequis

### 1. Lancement de l'Application
Se positionner à la racine du package Assistant-Pedago-iot

`source .venv/bin/activate`

`(venv) $ python -m CLI.main`