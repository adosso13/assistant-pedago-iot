# 📘 Assistant pédagogique IoT basé sur un LLM
## 🎯 Objectif

Ce projet consiste à développer une application Python permettant d’interagir avec un assistant intelligent spécialisé en IoT.

L’assistant doit être capable de :

- Répondre à des questions techniques à partir d’un cours fourni
- Tester les connaissances de l’utilisateur
- Générer automatiquement des quiz


## 🧩 Fonctionnalités
### 🔹 1. Mode Question / Réponse
L’utilisateur pose une question technique sur l’IoT
Le système répond uniquement à partir du contenu du cours

#### Contraintes :

Réponses claires et précises
Aucune invention hors du contenu fourni


### 🔹 2. Mode Challenge
Le système pose une question à l’utilisateur L’utilisateur répond
- Le système :
    - Donne une note sur 10
    - Fournit une explication
    - Donne une réponse idéale


### 🔹 3. Mode Quiz
- Génération automatique d’un quiz sur un thème IoT
- Minimum 5 questions
- Format QCM
- Calcul et affichage du score final


## ⚙️ Stack technique
### Backend
- Python
- Flask (API REST)
### LLM
- Groq API
- Modèle : Llama 3 (ou équivalent)
### Données
- Cours IoT fourni sous forme de texte
### Stockage
- SQLite (scores, historique)

## 🏗️ Architecture du projet

## 🚀 Installation
`$ git clone https://github.com/Adosso13/Assistant-Pedago-iot.git Assistant-Pedago-iot`

`$ cd Assistant-Pedago-iot`

Créer un environnement virtuel

`$ python3 -m venv .venv`

Activer l'environnement

`$ source .venv/bin/activate`

Installer les dépendances

`$ pip install -r requirements.txt`

Créer une Groq API Key sur `console.groq.com`.

Puis créer un fichier `.env` à la racine du projet, contenant la ligne ci-dessous.
```
GROQ_API_KEY = votre_cle
```
