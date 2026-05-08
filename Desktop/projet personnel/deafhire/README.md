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
| Détection LSF via MediaPipe Holistic (14 signes, auto-confirm 1,5 s) | ✅ |
| Transmission des landmarks bruts vers le backend | ✅ |
| Reconnaissance vocale recruteur (Web Speech API) | ✅ |
| Affichage mots-clés LSF pour le candidat | ✅ |
| Transcript temps réel persisté en base à chaque message | ✅ |
| Transcript téléchargeable (.txt) depuis la salle ou le détail | ✅ |
| Page de détail de session (notes, décision, transcript) | ✅ |
| Page Entretiens (liste complète avec statut/décision) | ✅ |
| Page Candidats (tableau historique) | ✅ |
| Page Rapports (stats + graphe décisions + terminés) | ✅ |
| Page Paramètres (profil, préférences, déconnexion) | ✅ |
| Base de données SQLite persistante (WAL mode) | ✅ |
| Envoi d'email HTML (SMTP configurable) | ✅ |
| Modèle ML demo générable (RandomForest) | ✅ |
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
│   ├── dashboard.html          ← Tableau de bord (protégé, données live)
│   ├── interviews.html         ← Liste de tous les entretiens
│   ├── candidates.html         ← Tableau historique des candidats
│   ├── reports.html            ← Stats + graphe décisions
│   ├── settings.html           ← Profil, préférences, compte
│   ├── session-detail.html     ← Détail session : notes, décision, transcript
│   ├── join.html               ← Candidat : code + test caméra + validation
│   ├── interview.html          ← Salle d'entretien WebSocket + WebRTC
│   ├── css/
│   │   ├── main.css            ← Design system global (dashboard, pages, transcript…)
│   │   └── interview.css       ← Layout dark de la salle d'entretien
│   └── js/
│       ├── auth.js             ← JWT, route guard, expiry watchdog auto-logout
│       ├── app.js              ← Utilitaires globaux
│       ├── interview.js        ← Contrôleur principal + WebRTC P2P
│       ├── sign-detector.js    ← Détection LSF (MediaPipe Holistic + 14 signes)
│       ├── speech.js           ← Reconnaissance vocale (Web Speech API)
│       ├── avatar.js           ← Texte → mots-clés LSF
│       └── ws-client.js        ← WebSocket (keep-alive, reconnexion expo, WebRTC relay)
├── backend/
│   ├── main.py                 ← FastAPI + lifespan (init DB)
│   ├── database.py             ← SQLite WAL (sessions, users, transcripts)
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── core/config.py          ← Settings (pydantic-settings)
│   ├── routes/
│   │   ├── auth.py             ← POST /auth/login, /auth/register, GET /auth/me
│   │   ├── session.py          ← CRUD sessions + transcript + GET /validate/{id}
│   │   ├── translation.py      ← POST /translate/sign, /translate/text
│   │   └── ws.py               ← WebSocket /ws/{session_id}/{role} + WebRTC relay
│   ├── services/
│   │   ├── auth.py             ← Hash mot de passe + JWT
│   │   ├── sign_language.py    ← Traduction LSF → français
│   │   ├── email.py            ← Envoi invitation SMTP
│   │   └── nlp.py              ← Simplification texte + mots-clés
│   └── models/schemas.py       ← Schémas Pydantic
├── ml/
│   └── src/
│       ├── collect_data.py         ← Collecte landmarks (webcam)
│       ├── create_demo_model.py    ← Génère un modèle demo fonctionnel
│       ├── train.py                ← Entraîne sur données réelles
│       └── model.py                ← Classe d'inférence (ONNX / sklearn)
├── docker-compose.yml
├── .env.example
└── .gitignore
```

---

## Démarrage rapide

### Option A — Mode démo (sans installation)

```bash
# Lancer un serveur HTTP dans le dossier frontend
cd frontend
python3 -m http.server 5500
# Ouvrir http://localhost:5500
```

Le frontend détecte automatiquement l'absence de backend et bascule en **mode démo** :
- Détection LSF simulée (signes défilants)
- Auth locale (`admin@deafhire.fr` / `deafhire2026`)
- Toutes les pages sont accessibles et fonctionnelles

---

### Option B — Avec le backend complet

```bash
# 1. Copier et configurer les variables d'environnement
cp .env.example backend/.env

# 2. Installer les dépendances backend
cd backend
pip install -r requirements.txt

# 3. (Optionnel) Générer le modèle ML demo
cd ../ml
python src/create_demo_model.py
# → ml/model/lsf_model.pkl

# 4. Lancer le serveur (port 8001 si 8000 est occupé par Docker)
cd ../backend
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

Le backend démarre sur `http://localhost:8001`.
- Doc API interactive : `http://localhost:8001/docs`
- Santé : `http://localhost:8001/health`

> **Note :** Le frontend en mode dev (ports 5500/5501) pointe automatiquement vers `localhost:8001`. En production, il utilise l'origine de la page.

---

### Option C — Docker

```bash
docker-compose up --build
```

---

## Pages & URLs

| Page | URL (démo) | Description |
|---|---|---|
| Landing | http://localhost:5500 | Accueil public |
| Connexion | http://localhost:5500/login.html | Login recruteur |
| Dashboard | http://localhost:5500/dashboard.html | Tableau de bord (protégé) |
| Entretiens | http://localhost:5500/interviews.html | Liste complète des sessions |
| Candidats | http://localhost:5500/candidates.html | Historique candidats |
| Rapports | http://localhost:5500/reports.html | Stats & graphes |
| Paramètres | http://localhost:5500/settings.html | Profil & préférences |
| Détail session | http://localhost:5500/session-detail.html?session=XXX | Notes, décision, transcript |
| Rejoindre | http://localhost:5500/join.html | Candidat : saisie code |
| Entretien | http://localhost:5500/interview.html?role=recruiter&session=XXX | Salle d'entretien |

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
PATCH /sessions/{id}              Mettre à jour (statut, décision, notes, ended_at)
GET  /sessions/{id}/transcript    Récupérer le transcript (entries horodatées)
GET  /sessions/validate/{id}      Valider un code session (public, sans auth)

POST /translate/sign              Keypoints MediaPipe → texte français
POST /translate/text              Texte → simplifié + mots-clés LSF

WS   /ws/{session_id}/{role}      WebSocket temps réel (candidate | recruiter)
```

---

## Architecture temps réel

```
Candidat (navigateur)
  MediaPipe Holistic → landmarks mains + corps
  Sign Detector → signe + confiance (auto-confirm 1,5 s)
  → WS /ws/{id}/candidate  {type: "sign_keypoints", sign, confidence, keypoints}
  → backend : SignLanguageService.translate() → "Bonjour, je suis ravi…"
  → broadcast → Recruteur (affichage transcript + chat)
  → DB : transcript entry persistée en temps réel

Recruteur (navigateur)
  Tape ou dicte (Web Speech API)
  → WS /ws/{id}/recruiter  {type: "recruiter_message", text}
  → backend : NLPService.process() → texte simplifié + mots-clés LSF
  → broadcast → Candidat (chips LSF + texte clair)
  → DB : transcript entry persistée en temps réel

WebRTC P2P (vidéo/audio)
  Signalement via le même WebSocket :
    webrtc_ready → webrtc_offer → webrtc_answer → webrtc_ice
  Flux local : getUserMedia {video, audio}
  Flux distant : affiché en overlay dans le panel candidat (remote-video)
```

---

## Configuration SMTP (envoi d'emails)

Dans `backend/.env` :

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_TLS=true
SMTP_USER=votre@gmail.com
SMTP_PASSWORD=mot_de_passe_application_google
SMTP_FROM=noreply@deafhire.fr
```

Sans configuration SMTP, le lien d'invitation est loggué en console (mode démo).

---

## Pipeline ML — Entraîner votre propre modèle LSF

### 1. Générer un modèle demo (immédiat)

```bash
cd ml
python src/create_demo_model.py
# → ml/model/lsf_model.pkl (RandomForest sur données synthétiques)
```

### 2. Collecter de vraies données

```bash
pip install mediapipe opencv-python scikit-learn

python src/collect_data.py --sign "Bonjour" --samples 200
python src/collect_data.py --sign "Merci"   --samples 200
# ... répéter pour chaque signe (14 signes supportés)
```

### 3. Entraîner sur données réelles

```bash
python src/train.py --data data/keypoints.csv --output model/lsf_model.pkl
```

Le modèle est chargé automatiquement au démarrage du backend. Le frontend envoie également les landmarks bruts MediaPipe via WebSocket pour enrichir les données d'entraînement futures.

---

## Licence

MIT — Projet personnel inclusif.
