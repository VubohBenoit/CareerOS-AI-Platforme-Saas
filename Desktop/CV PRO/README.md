# CareerOS AI — Copilote Intelligent de Recherche d'Emploi

## Vue d'ensemble

**CareerOS AI** est une plateforme SaaS intelligente qui automatise et optimise la recherche d'emploi. Elle aide les candidats à trouver les offres pertinentes, adapter leur candidature, et décrocher leurs entretiens.

**Status** : Phase 0 — Validation des spécifications (README + REQUIREMENTS + PERSONAS + ARCHITECTURE)

---

## Problème & Opportunité

### Pain points des job seekers

1. **Volume inutile** : Trop d'offres non-pertinentes, difficile à trier
2. **ATS invisibilité** : CVs rejetés par algorithmes, pas de feedback
3. **Temps perdu** : 30 min par candidature (adaption CV + lettre)
4. **Suivi chaotique** : Pas de suivi centralisé des candidatures
5. **Nervosité** : Pas de préparation avant entretiens
6. **Pas de feedback** : Refus = silence radio, pas d'apprentissage

### Solution CareerOS AI

✅ **Recherche intelligente** : 20-30 offres pertinentes/jour (vs 100 brutes)
✅ **Adaptation ATS** : CV optimisé avec rapport des changements
✅ **Automation éthique** : Lettre + email générés en 2 min (humain valide avant envoi)
✅ **Suivi complet** : Dashboard centralisé, analytics, prédictions
✅ **Coaching IA** : Simulation entretiens, feedback immédiat
✅ **Apprentissage** : Feedback loop = s'améliorer chaque semaine

---

## Personas & Personas

### Léa Moreau (Mid-career transition)
- Développeuse 4 ans, change de secteur (fintech → deeptech)
- **Objectif** : 3-5 entretiens/semaine, 1 offre en 4-6 semaines
- **Volume** : 75-100 candidatures/mois
- **Besoin clé** : ATS optimization + relances intelligentes

### Marc Dubois (Senior leader)
- Cadre 15 ans, licenciement économique, repositionnement
- **Objectif** : 2-3 offres sérieuses en 3-4 mois
- **Volume** : 10-20 candidatures/mois, qualité ultra-ciblée
- **Besoin clé** : Culture fit analysis + exec interview coaching

### Aminata Sow (Junior entry-level)
- Fraîche diplômée Master Data Science, 0 expérience pro
- **Objectif** : 1ère offre en 2-3 mois
- **Volume** : 200-300 candidatures/mois (spray & pray)
- **Besoin clé** : Feedback loop + technical prep + motivational coaching

---

## Scope du Produit

### MVP (Phase 1 — 8-10 semaines)
- ✅ Gestion du profil (CRUD, import CV)
- ✅ Recherche d'offres (APIs + filtres)
- ✅ Analyse job + score compatibilité
- ✅ Optimisation CV (ATS report)
- ✅ Génération lettre + email
- ✅ Application tracking (statuts, historique)
- ✅ Dashboard basique (stats)
- ✅ Auth (signup/login)

**Est. users on day 1** : 0 (beta testing)

### Phase 2 (Mois 3-4)
- Interview coaching (simulation + feedback)
- Relances intelligentes (auto-scheduling)
- Intégration Indeed + Welcome To The Jungle
- Glassdoor scraping (culture data)
- Advanced analytics (graphs, trends)
- Mobile iOS/Android

### Phase 3+ (Mois 5+)
- Chrome extension (quick apply)
- Slack integration
- ML (predict offer probability)
- Team collaboration (share templates)
- White-label / B2B plans

---

## Architecture

### Stack technologique

**Frontend** :
- Next.js 14 (App Router, SSR)
- React 18 + TypeScript
- Shadcn UI + Tailwind CSS
- TanStack Query + Zustand

**Backend** :
- FastAPI (Python 3.11, async)
- SQLAlchemy 2.0 ORM
- Celery + Redis (background tasks)
- LangGraph (multi-agent orchestration)

**Data** :
- PostgreSQL (primary)
- Redis (cache + queues)
- Elasticsearch (job index)
- AWS S3 (documents)

**AI** :
- OpenAI GPT-4 (LLM)
- Claude (alternative)
- LangGraph (agent framework)

**DevOps** :
- Docker (containerization)
- Kubernetes (orchestration)
- GitHub Actions (CI/CD)
- Terraform (IaC)

---

## Structure du dossier

```
CareerOS AI/
├─ README.md                   # Ce fichier
├─ REQUIREMENTS.md             # Spec produit complète
├─ PERSONAS.md                 # Personas + journey maps
├─ ARCHITECTURE.md             # Architecture technique
├─ MASTER_PROMPT.md            # (optionnel, ce prompt)
│
├─ frontend/                   # Next.js app
│  ├─ app/
│  ├─ components/
│  ├─ lib/
│  ├─ public/
│  ├─ package.json
│  ├─ tailwind.config.ts
│  ├─ tsconfig.json
│  ├─ Dockerfile
│  └─ .dockerignore
│
├─ backend/                    # FastAPI app
│  ├─ app/
│  │  ├─ __init__.py
│  │  ├─ main.py
│  │  ├─ config.py
│  │  ├─ models/
│  │  ├─ schemas/
│  │  ├─ api/
│  │  ├─ services/
│  │  ├─ agents/
│  │  ├─ tasks/
│  │  ├─ utils/
│  │  ├─ middleware/
│  │  └─ db/
│  ├─ tests/
│  ├─ requirements.txt
│  ├─ Dockerfile
│  ├─ pytest.ini
│  ├─ .env.example
│  └─ main.py (local dev entry)
│
├─ infra/                     # Infrastructure as Code
│  ├─ docker-compose.yml      # Local dev setup
│  ├─ kubernetes/             # K8s manifests
│  │  ├─ namespace.yaml
│  │  ├─ postgres.yaml
│  │  ├─ redis.yaml
│  │  ├─ backend.yaml
│  │  ├─ frontend.yaml
│  │  ├─ ingress.yaml
│  │  └─ kustomization.yaml
│  ├─ terraform/             # AWS/Cloud IaC
│  │  ├─ main.tf
│  │  ├─ variables.tf
│  │  ├─ outputs.tf
│  │  ├─ rds.tf
│  │  ├─ s3.tf
│  │  └─ networking.tf
│  └─ scripts/
│     ├─ setup.sh
│     ├─ deploy.sh
│     └─ migrate.sh
│
├─ docs/                      # Documentation
│  ├─ API.md                  # OpenAPI / API docs
│  ├─ DEVELOPER.md            # Dev setup guide
│  ├─ DEPLOYMENT.md           # Deployment guide
│  ├─ DATABASE.md             # Schema details
│  ├─ SECURITY.md             # Security considerations
│  └─ TESTING.md              # Test strategy
│
├─ .github/
│  ├─ workflows/
│  │  ├─ ci.yml               # Tests on PR
│  │  ├─ deploy.yml           # Deploy on merge
│  │  └─ security.yml         # Security checks
│  └─ CODEOWNERS
│
├─ .gitignore
├─ .env.example
├─ Makefile                   # Dev shortcuts (make run, make test, etc.)
└─ docker-compose.yml         # Local dev stack
```

---

## Roadmap haute-niveau

### Phase 0 : Validation (Semaine 1)
- [x] Spécifications complètes (REQUIREMENTS.md)
- [x] Personas détaillées (PERSONAS.md)
- [x] Architecture technique (ARCHITECTURE.md)
- [ ] **Validation PO** : Confirme scope + personas + priorités
- [ ] **Validation Arch** : Approuve tech stack + patterns
- [ ] **Validation Sec** : OK GDPR + data handling
- [ ] **Go/No-go** : Lancer Phase 1

### Phase 1 : MVP (Semaines 2-11)

**Semaines 2-3 : Backend scaffolding**
- [ ] FastAPI project setup
- [ ] PostgreSQL schema + migrations
- [ ] Auth (signup/login/JWT)
- [ ] User & Profile models + CRUD APIs
- [ ] Database seeding for testing

**Semaines 4-5 : Core features**
- [ ] Job API + filtering
- [ ] Application CRUD
- [ ] CV parsing + import
- [ ] Document versioning

**Semaines 6-7 : AI integration**
- [ ] LLM service setup (OpenAI / Claude)
- [ ] Analyst agent (job analysis)
- [ ] ATS Expert agent (CV optimization)
- [ ] Writer agent (letter generation)

**Semaines 8-9 : Frontend**
- [ ] Project setup (Next.js)
- [ ] Auth UI (login/signup)
- [ ] Profile UI
- [ ] Job search UI
- [ ] Application UI
- [ ] Dashboard UI

**Semaines 10-11 : Integration + Polish**
- [ ] End-to-end testing
- [ ] Performance optimization
- [ ] Bug fixes
- [ ] Deployment pipeline

### Phase 1.5 : Beta Launch (Semaine 12)
- [ ] Internal testing (team)
- [ ] 10-20 beta testers (friends/family)
- [ ] Feedback collection
- [ ] Quick fixes

### Phase 2 : Extended Features (Weeks 13-19)
- [ ] Interview coaching agent
- [ ] Smart follow-ups (Reminder agent)
- [ ] Additional job board integrations
- [ ] Mobile app (React Native)

### Phase 3 : Growth (Weeks 20+)
- [ ] Chrome extension
- [ ] Marketplace/partnerships
- [ ] Advanced ML features
- [ ] B2B/Team plans

---

## Metrics de succès

### Phase 1 (MVP Launch)
- ✅ Product functional (no major bugs)
- ✅ 50+ beta testers active
- ✅ NPS > 50
- ✅ Response time < 2s (p95)

### Post-MVP
- ✅ 1,000 sign-ups in first month
- ✅ 20% DAU (Daily Active Users)
- ✅ 3+ applications per user per week (avg)
- ✅ Response rate > 20%
- ✅ CAC payback in 4 months

---

## Constraints & Trade-offs

### Constraint 1 : LLM Costs
**Problem** : OpenAI/Claude expensive at scale

**Solutions** :
- Aggressive caching (Redis)
- Batch processing (not real-time for all)
- Ollama local for simple tasks
- Tiered pricing (starter free = limited features)
- Focus on high-impact AI (letter gen, interview coach)

### Constraint 2 : Job Board Integration
**Problem** : LinkedIn/Indeed have legal constraints

**Solutions** :
- APIs officially (LinkedIn, Indeed when available)
- RSS feeds + partners
- Respect robots.txt, rate limits
- Partner agreements for scale
- Focus on EU markets first (GDPR-friendly)

### Constraint 3 : Data Privacy
**Problem** : GDPR requirements complex

**Solutions** :
- Privacy by design (data minimization)
- Clear consent flows
- Right to delete (cascade delete)
- Audit logging complete
- DPA for EU users
- No SSN/sensitive docs

---

## Getting Started (Local Dev)

### Prerequisites
- Docker + Docker Compose
- Python 3.11
- Node.js 18+
- PostgreSQL 15+ (if not using Docker)
- Redis (if not using Docker)

### Local Setup

```bash
# 1. Clone repo
git clone <repo> CareerOS-AI
cd CareerOS-AI

# 2. Create .env
cp .env.example .env

# 3. Start services (Docker Compose)
docker-compose up -d

# 4. Run migrations
docker-compose exec backend python -m alembic upgrade head

# 5. Seed database (optional)
docker-compose exec backend python scripts/seed.py

# 6. Start backend (local)
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# 7. Start frontend (new terminal)
cd frontend
npm install
npm run dev
# Accessible at http://localhost:3000

# 8. Tests
cd backend && pytest
cd frontend && npm test
```

### Environment Variables (.env)

```
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/careeeros_ai

# Redis
REDIS_URL=redis://localhost:6379

# JWT
SECRET_KEY=<secret_key_for_jwt>
JWT_ALGORITHM=HS256

# LLM APIs
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# AWS S3
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_S3_BUCKET=careeeros-ai

# Email
SENDGRID_API_KEY=SG...

# LinkedIn API (if available)
LINKEDIN_ACCESS_TOKEN=...

# Environment
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=INFO
```

---

## Contributing

We're looking for early collaborators. If you're interested in contributing:

1. Pick a task from the roadmap
2. Create a feature branch
3. Implement + add tests
4. Open a PR with description
5. Code review + merge

See [DEVELOPER.md](./docs/DEVELOPER.md) for detailed guidelines.

---

## Governance

### Decision Making
- **Technical** : Arch team consensus
- **Product** : PO (you) final say
- **Design** : Design lead approval

### Communication
- **Sync** : Weekly 1h architecture review
- **Async** : Slack + GitHub PRs
- **Specs** : Markdown docs (this repo)

---

## Next Steps (Immediate)

### For Approval
1. **Confirm Personas** : Do these 3 personas resonate? Any others to add?
2. **Validate Scope** : Is MVP scope realistic? Any must-haves missing?
3. **Approve Tech Stack** : FastAPI + React OK? Any objections?
4. **Set Budget** : Cloud costs, LLM costs, team size, timeline?
5. **Decide Timeline** : Start Phase 1 immediately, or prep first?

### For Preparation (if GO)
1. **Setup GitHub repo** : Organize code, .gitignore, branch protection
2. **Buy domain** : careeeros.ai (or similar)
3. **Setup cloud account** : AWS or similar (billing, identity, networking)
4. **Hire team** : Backend lead, Frontend lead, Designer, DevOps lead
5. **Legal review** : Privacy policy, ToS, GDPR compliance

---

## Contact & Questions

**Questions about spec?** → See REQUIREMENTS.md
**Questions about design?** → See PERSONAS.md  
**Questions about code?** → See ARCHITECTURE.md + docs/
**Questions about business?** → Reach out directly

---

**Created** : 2026-08-02
**Version** : 0.1 (Draft for Validation)
**Status** : Awaiting approval

---

## Signoff Checklist

- [ ] **Product Owner** validates personas + scope
- [ ] **Technical Architect** approves tech stack + architecture
- [ ] **Security Lead** confirms GDPR + data security approach
- [ ] **Finance** approves budget + cost estimates
- [ ] **Executive** approves timeline + resource allocation
- **→ GO to Phase 1**
