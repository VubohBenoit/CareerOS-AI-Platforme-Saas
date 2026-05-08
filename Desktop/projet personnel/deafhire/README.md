# DeafHire — Plateforme d'entretiens inclusifs LSF ↔ Texte

DeafHire permet aux recruteurs de conduire des entretiens avec des candidats sourds ou malentendants **sans interprète humain**, grâce à une IA de traduction en temps réel entre la Langue des Signes Française (LSF) et le texte/la voix.

---

## Fonctionnalités

| Fonctionnalité | Statut |
|---|---|
| Landing page & design system complet | ✅ |
| Dashboard recruteur (stats live depuis l'API) | ✅ |
| Authentification JWT (login/register + expiry watchdog) | ✅ |
| Page candidat « Rejoindre » avec validation session + test caméra | ✅ |
| Salle d'entretien temps réel (WebSocket + keep-alive ping/pong) | ✅ |
| Vidéo P2P WebRTC (signalement via WebSocket) | ✅ |
| Détection LSF multicouche (GestureModel + TF.js + règles géométriques) | ✅ |
| Trainer IA in-browser — TF.js MLP, 14 signes, import/export dataset | ✅ |
| Guide visuel par signe (SVG + description + tags) | ✅ |
| Grand modèle Python — architecture 512→256→128, export TF.js auto | ✅ |
| Scraper Spreadthesign (5 916 signes LSF téléchargeables) | ✅ |
| Reconnaissance vocale recruteur (Web Speech API) | ✅ |
| Transcript temps réel persisté en base à chaque message | ✅ |
| Transcript téléchargeable (.txt) depuis la salle ou le détail | ✅ |
| Page de détail de session (notes, décision, transcript) | ✅ |
| Page Entretiens, Candidats, Rapports, Paramètres | ✅ |
| Base de données SQLite persistante (WAL mode) | ✅ |
| Envoi d'email HTML (SMTP configurable) | ✅ |
| Docker (production-ready) | ✅ |
| Avatar 3D LSF | 🗺️ Roadmap |
| Support LSE / ASL / BSL | 🗺️ Roadmap |

---

## Structure du projet

```
deafhire/
├── frontend/
│   ├── index.html              ← Landing page publique
│   ├── login.html              ← Connexion recruteur (JWT)
│   ├── dashboard.html          ← Tableau de bord (stats live)
│   ├── interviews.html         ← Liste de tous les entretiens
│   ├── candidates.html         ← Tableau historique des candidats
│   ├── reports.html            ← Stats + graphe décisions
│   ├── settings.html           ← Profil, préférences, compte
│   ├── session-detail.html     ← Détail session : notes, décision, transcript
│   ├── join.html               ← Candidat : code + test caméra + validation
│   ├── interview.html          ← Salle d'entretien WebSocket + WebRTC
│   ├── css/
│   │   ├── main.css            ← Design system global
│   │   └── interview.css       ← Layout dark de la salle d'entretien
│   ├── js/
│   │   ├── auth.js             ← JWT, route guard, expiry watchdog
│   │   ├── app.js              ← Utilitaires globaux
│   │   ├── interview.js        ← Contrôleur principal + WebRTC P2P
│   │   ├── sign-detector.js    ← Détection LSF 3 couches (ML → règles)
│   │   ├── sign-trainer.js     ← Trainer in-browser TF.js MLP (14 signes)
│   │   ├── gesture-model.js    ← Classificateur landmarks pur JS (12 signes)
│   │   ├── speech.js           ← Reconnaissance vocale (Web Speech API)
│   │   ├── avatar.js           ← Texte → mots-clés LSF
│   │   └── ws-client.js        ← WebSocket (keep-alive, reconnexion expo, WebRTC relay)
│   └── assets/
│       └── icons/
├── backend/
│   ├── main.py                 ← FastAPI + lifespan (init DB) + sert le frontend
│   ├── database.py             ← SQLite WAL (sessions, users, transcripts)
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── core/
│   │   └── config.py           ← Settings (pydantic-settings)
│   ├── routes/
│   │   ├── auth.py             ← POST /auth/login, /auth/register, GET /auth/me
│   │   ├── session.py          ← CRUD sessions + transcript
│   │   ├── translation.py      ← POST /translate/sign, /translate/text
│   │   ├── model.py            ← GET /model/status, /model/classes, /model/tfjs/*
│   │   └── ws.py               ← WebSocket /ws/{session_id}/{role} + WebRTC relay
│   ├── services/
│   │   ├── auth.py             ← Hash mot de passe + JWT
│   │   ├── sign_language.py    ← Traduction LSF → français
│   │   ├── email.py            ← Envoi invitation SMTP
│   │   └── nlp.py              ← Simplification texte + mots-clés LSF
│   └── models/
│       └── schemas.py          ← Schémas Pydantic
├── ml/
│   ├── requirements.txt
│   ├── notebooks/              ← Exploration / expériences (Jupyter)
│   ├── data/                   ← Datasets générés (ignorés par git)
│   │   ├── dataset_lsf.json    ← Exemples YouTube (landmarks 126-dim)
│   │   ├── dataset_sts.json    ← Exemples Spreadthesign (5 000+ signes)
│   │   └── videos/             ← Vidéos téléchargées (ignorées par git)
│   ├── model/                  ← Modèles entraînés (ignorés par git)
│   │   ├── tfjs_model/         ← Export TF.js servi par le backend
│   │   └── classes.json        ← Liste ordonnée des classes
│   └── src/
│       ├── spreadthesign_scraper.py  ← Scrape Spreadthesign.com (5 916 signes LSF)
│       ├── download_lsf_videos.py    ← Télécharge vidéos YouTube + extraction landmarks
│       ├── collect_dataset.py        ← Collecte webcam/vidéo/images + augmentation ×7
│       ├── record_all_signs.py       ← Enchaîne collect_dataset pour les 14 signes
│       ├── train_large.py            ← Entraîne MLP 512→256→128, exporte TF.js
│       └── create_demo_model.py      ← Génère un modèle demo rapide (données synthétiques)
├── docker-compose.yml
├── .env.example
└── .gitignore
```

---

## Démarrage rapide

### Option A — Mode démo (sans installation)

```bash
cd frontend
python3 -m http.server 5500
# Ouvrir http://localhost:5500
```

Le frontend bascule automatiquement en **mode démo** sans backend :
- Auth locale (`admin@deafhire.fr` / `deafhire2026`)
- Toutes les pages sont accessibles

---

### Option B — Backend complet

```bash
# 1. Variables d'environnement
cp .env.example backend/.env

# 2. Dépendances backend
cd backend
pip install -r requirements.txt

# 3. Lancer le serveur
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

- API interactive : `http://localhost:8001/docs`
- Santé : `http://localhost:8001/health`

> Le frontend en développement (ports 5500/5501) pointe automatiquement vers `localhost:8001`.

---

### Option C — Docker

```bash
docker-compose up --build
```

---

## Pages & URLs

| Page | URL (démo) | Description |
|---|---|---|
| Landing | `http://localhost:5500` | Accueil public |
| Connexion | `http://localhost:5500/login.html` | Login recruteur |
| Dashboard | `http://localhost:5500/dashboard.html` | Tableau de bord |
| Entretiens | `http://localhost:5500/interviews.html` | Liste des sessions |
| Candidats | `http://localhost:5500/candidates.html` | Historique |
| Rapports | `http://localhost:5500/reports.html` | Stats & graphes |
| Paramètres | `http://localhost:5500/settings.html` | Profil & préférences |
| Détail session | `http://localhost:5500/session-detail.html?session=XXX` | Notes, décision, transcript |
| Rejoindre | `http://localhost:5500/join.html` | Candidat — saisie code |
| Entretien | `http://localhost:5500/interview.html?role=recruiter&session=XXX` | Salle d'entretien |

**Compte de démonstration :**
```
Email    : admin@deafhire.fr
Password : deafhire2026
```

---

## API — Endpoints principaux

```
POST /auth/register               Créer un compte recruteur
POST /auth/login                  Connexion → JWT
GET  /auth/me                     Infos utilisateur connecté

POST /sessions                    Créer une session + envoi email
GET  /sessions                    Lister les sessions du recruteur
GET  /sessions/{id}               Détails d'une session
PATCH /sessions/{id}              Mettre à jour (statut, décision, notes)
GET  /sessions/{id}/transcript    Récupérer le transcript horodaté
GET  /sessions/validate/{id}      Valider un code session (public)

POST /translate/sign              Keypoints MediaPipe → texte français
POST /translate/text              Texte → simplifié + mots-clés LSF

GET  /model/status                Vérifie si un grand modèle TF.js est disponible
GET  /model/classes               Liste des classes du grand modèle
GET  /model/tfjs/{filename}       Sert les fichiers du modèle TF.js

WS   /ws/{session_id}/{role}      WebSocket temps réel (candidate | recruiter)
```

---

## Architecture de détection LSF

La détection fonctionne en **3 couches** — du plus précis au fallback :

```
Landmarks MediaPipe Holistic (21 pts × 2 mains)
          │
          ▼
1. Grand modèle Python (TF.js, 500+ signes)
   → chargé automatiquement depuis /model/ si le backend tourne
   → entraîné sur Spreadthesign (5 916 signes LSF)
          │ échec (modèle absent ou confiance < 0.65)
          ▼
2. TF.js in-browser (14 signes, localStorage)
   → MLP 126→128→64→N, entraîné dans le navigateur
   → l'utilisateur peut enregistrer ses propres exemples
          │ échec
          ▼
3. GestureModel (pur JS, sans modèle)
   → classifie la forme de la main (Open_Palm, Victory, Pointing…)
   → contextualise avec position (front / menton / poitrine) + 2 mains
   → couvre 12/14 signes, confiance 0.62–0.90
```

---

## Architecture temps réel

```
Candidat (navigateur)
  MediaPipe Holistic → landmarks mains + corps
  Sign Detector (3 couches) → signe + confiance (auto-confirm 1,5 s)
  → WS /ws/{id}/candidate  {type:"sign_keypoints", sign, confidence}
  → backend : SignLanguageService.translate() → phrase française
  → broadcast → Recruteur (transcript + chat)
  → DB : entry persistée en temps réel

Recruteur (navigateur)
  Tape ou dicte (Web Speech API)
  → WS /ws/{id}/recruiter  {type:"recruiter_message", text}
  → backend : NLPService.process() → texte simplifié + mots-clés LSF
  → broadcast → Candidat (chips LSF + texte clair)
  → DB : entry persistée en temps réel

WebRTC P2P (vidéo/audio)
  Signalement via le même WebSocket :
    webrtc_ready → webrtc_offer → webrtc_answer → webrtc_ice
```

---

## Pipeline ML — Entraîner le grand modèle

### Étape 1 — Télécharger les données

**Option A : Spreadthesign (recommandé — 5 916 signes LSF)**

```bash
cd ml
pip install -r requirements.txt

# Lister tous les signes disponibles
python src/spreadthesign_scraper.py list

# Télécharger les vidéos et extraire les landmarks
python src/spreadthesign_scraper.py all --limit 500

# → ml/data/dataset_sts.json
```

**Option B : YouTube (yt-dlp)**

```bash
python src/download_lsf_videos.py Bonjour Merci Oui Non Travail

# → ml/data/dataset_lsf.json
```

**Option C : Webcam**

```bash
python src/collect_dataset.py webcam --sign "Bonjour" --samples 150
python src/record_all_signs.py   # enchaîne les 14 signes automatiquement
```

### Étape 2 — Entraîner

```bash
python src/train_large.py
# ou avec options
python src/train_large.py --data data/dataset_sts.json --epochs 200 --min-samples 20
```

Architecture : `126 → Dense(512) → BN → Drop(0.3) → Dense(256) → BN → Drop(0.25) → Dense(128) → Drop(0.2) → Dense(N, softmax)`

Sorties :
- `ml/model/tfjs_model/` — modèle chargeable par le navigateur
- `ml/model/classes.json` — liste ordonnée des classes
- `ml/model/report.txt` — rapport de précision par classe

### Étape 3 — Servir

```bash
cd backend
uvicorn main:app --reload --port 8001
```

Le frontend charge le modèle automatiquement depuis `/model/` au démarrage. Aucune configuration supplémentaire.

---

## Configuration SMTP

Dans `backend/.env` :

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_TLS=true
SMTP_USER=votre@gmail.com
SMTP_PASSWORD=mot_de_passe_application_google
SMTP_FROM=noreply@deafhire.fr
```

Sans configuration SMTP, le lien d'invitation est loggué en console.

---

## Licence

MIT — Projet personnel inclusif.
