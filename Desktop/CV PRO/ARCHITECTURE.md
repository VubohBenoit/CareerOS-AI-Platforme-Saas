# CareerOS AI — Architecture technique

**Version:** 0.1 | **Date:** 2026-08-02 | **Status:** Proposition pour validation

---

## 1. Vue d'ensemble de l'architecture

### Principes fondamentaux

1. **Modularité** : Chaque module = responsabilité unique, découplé
2. **Scalabilité** : Horizontal scaling via Kubernetes, no single point of failure
3. **Asynchronicité** : Workers pour tâches longues (scraping, email, IA)
4. **Cacheabilité** : Redis pour data chaude, CDN pour assets
5. **Testabilité** : Code découplé, dépendances injectables
6. **Observabilité** : Logging, metrics, tracing (OpenTelemetry)
7. **Sécurité** : Defense in depth, chiffrement, audit logging

---

## 2. Diagramme d'architecture haute niveau

```
┌─────────────────────────────────────────────────────────────────┐
│                        CDN + WAF                                │
│                   (CloudFlare / AWS CloudFront)                 │
└────────────────────┬────────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
    ┌───▼────────┐          ┌────▼────────┐
    │  Frontend  │          │   Backend   │
    │ (Next.js)  │          │ (FastAPI)   │
    │  SPA/SSR   │          │ via nginx   │
    └────┬───────┘          └────┬────────┘
         │                       │
         └───────────┬───────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
    ┌────▼──────┐         ┌──────▼────┐
    │  Auth     │         │  API      │
    │  (OAuth)  │         │  (REST)   │
    │  (JWT)    │         │  (gRPC?)  │
    └────┬──────┘         └──────┬────┘
         │                       │
         └───────────┬───────────┘
                     │
        ┌────────────┴───────────────┐
        │                            │
    ┌───▼────────┐          ┌───────▼────┐
    │ PostgreSQL │          │  Redis     │
    │ (Primary)  │          │  (Cache)   │
    │ + Replicas │          │  + Queues  │
    └────────────┘          └────────────┘
        │                            │
        └────────────┬───────────────┘
                     │
         ┌───────────┴──────────────┐
         │                          │
    ┌────▼──────┐          ┌───────▼────┐
    │ Celery    │          │ Elasticsearch
    │ Workers   │          │ (Job Index) │
    │(Async)    │          │            │
    └───────────┘          └────────────┘
         │
    ┌────▼──────────────────────────┐
    │   AI Agents (LangGraph)       │
    │                              │
    │ ┌──────────┐ ┌────────────┐ │
    │ │ Scout    │ │ Analyst    │ │
    │ │ (Search) │ │ (Parse)    │ │
    │ └──────────┘ └────────────┘ │
    │                              │
    │ ┌──────────┐ ┌────────────┐ │
    │ │ ATS Exp  │ │ Writer     │ │
    │ │ (Optim)  │ │ (Letters)  │ │
    │ └──────────┘ └────────────┘ │
    │                              │
    │ ┌──────────┐ ┌────────────┐ │
    │ │ Tracker  │ │ Coach      │ │
    │ │ (CRM)    │ │ (Interview)│ │
    │ └──────────┘ └────────────┘ │
    │                              │
    │ ┌────────────────────────┐   │
    │ │ Orchestrator           │   │
    │ │ (Routes tasks)         │   │
    │ └────────────────────────┘   │
    │                              │
    └──────────────────────────────┘

External APIs:
├─ LinkedIn API (job search)
├─ Indeed API
├─ Welcome To The Jungle
├─ OpenAI / Anthropic Claude (IA)
├─ Crunchbase (Company data)
├─ Glassdoor (scraping)
└─ AWS S3 (Document storage)
```

---

## 3. Stack technologique et justifications

### Frontend

**Choix : Next.js 14 (App Router) + React 18 + TypeScript**

```
Raisons :
├─ SSR/SSG out-of-box (perfs, SEO)
├─ API routes (backend simple endpoints)
├─ Type-safety (TS)
├─ Mature ecosystem (shadcn/ui, tanstack libraries)
├─ Incremental builds (fast dev)
├─ Vercel deployment easy (but can self-host on EC2)
└─ Great DX (hot reload, error messages)

Alternatives rejetées :
├─ Vue.js : Moins d'ecosystem, moins de jobs
├─ Svelte : Petit community, moins mature
├─ Remix : Good but steeper learning curve
└─ Plain React : No SSR, more setup
```

**UI Framework : Shadcn/ui + Tailwind CSS**

```
Raisons :
├─ Headless (customizable)
├─ Accessibility defaults (a11y)
├─ Dark mode support (important for Léa/Marc)
├─ Copy-paste (not yarn add bloat)
├─ Design tokens extensible
└─ No arbitrary design decisions

Alternatives rejetées :
├─ Material-UI : Too opinionated
├─ Ant Design : Enterprise but heavy
├─ Bootstrap : Too 2015
└─ Custom CSS : Too slow to build
```

**State Management : TanStack Query (React Query) + Zustand**

```
Raisons :
├─ TanStack Query : server state management (perfect for API-heavy app)
├─ Zustand : lightweight client state (preference, modal visibility)
├─ No Redux boilerplate (simpler)
└─ Great devtools (React Query devtools)

Alternatives rejetted :
├─ Redux : Overkill for our needs
├─ Recoil : Experimental, smaller community
└─ MobX : Requires decorators (old React patterns)
```

**Key Libraries**

```
├─ zod : Runtime validation (forms, API responses)
├─ react-hook-form : Lightweight forms (with Zod)
├─ date-fns : Date manipulation (lightweight)
├─ recharts : Data viz (dashboard charts)
├─ pdf-lib : PDF generation (browser-side)
├─ stripe-js : Payment integration (future)
└─ next-auth : Auth middleware (easy integration)
```

**Project Structure**

```
frontend/
├─ app/                        # Next.js app router
│  ├─ (auth)/                  # Auth group (login/signup)
│  ├─ (dashboard)/             # Main dashboard group (protected)
│  │  ├─ profile/              # Profile management
│  │  ├─ search/               # Job search
│  │  ├─ applications/         # My applications
│  │  ├─ interviews/           # Interview coaching
│  │  └─ analytics/            # Dashboard stats
│  ├─ api/                     # API routes (if needed)
│  └─ layout.tsx               # Root layout
│
├─ components/
│  ├─ ui/                      # Shadcn components (copied)
│  ├─ auth/                    # Auth-related
│  ├─ profile/                 # Profile components
│  ├─ job/                     # Job search components
│  ├─ application/             # Application components
│  ├─ interview/               # Interview coaching
│  └─ shared/                  # Shared (navbar, footer, etc.)
│
├─ lib/
│  ├─ api.ts                   # API client (fetcher)
│  ├─ auth.ts                  # Auth helpers
│  ├─ queries.ts               # TanStack Query hooks
│  ├─ validators.ts            # Zod schemas
│  ├─ utils.ts                 # Utilities (dates, formatting)
│  └─ constants.ts             # App constants
│
├─ styles/
│  └─ globals.css              # Tailwind + global styles
│
├─ public/                     # Static assets
├─ package.json
├─ tsconfig.json
└─ next.config.js
```

---

### Backend

**Choix : FastAPI (Python 3.11) + Pydantic v2**

```
Raisons :
├─ Async first (great for I/O, LLM calls, DB queries)
├─ Type hints (Pydantic models auto-validate)
├─ OpenAPI auto-docs (Swagger UI)
├─ Performance (nearly as fast as Go for our use case)
├─ Python ecosystem (LLM libraries, ML tools)
├─ Excellent DX (error messages, request validation)
├─ Active community (LangGraph, LangChain mature here)
└─ Our team knows Python well

Alternatives considered :
├─ Django + DRF : Slower, more boilerplate, harder async
├─ Go (Gin/Echo) : Type-safe but LLM ecosystem weaker
├─ Rust (Axum) : Overkill, hire Rust engineers = expensive
└─ Node.js (Express) : JavaScript fatigue, less AI library support
```

**Job Execution : Celery + Redis**

```
Raisons :
├─ Distributed task queue (job scraping = slow)
├─ Retry logic built-in (failed scrapers retry)
├─ Priority queues (urgent emails first)
├─ Monitoring (Flower UI)
├─ Serialization (Pickle for Python objects)
└─ Redis backend (fast, no DB overhead)

Alternatives considered :
├─ APScheduler : For simple crons, but not distributed
├─ AWS SQS : Managed but cost + latency
├─ RabbitMQ : More complex, not needed
└─ Temporal : Overkill for our workflow needs
```

**Async Worker Pattern**

```python
# When to use async workers :
├─ Long-running : Job scraping (10-30 sec per source)
├─ I/O bound : API calls, DB queries, LLM calls
├─ Batch : Email sending (1000s of emails)
├─ Scheduled : Relances, daily job scans

# Fast path (synchronous) :
├─ Profile CRUD (< 100ms)
├─ Authentication (< 50ms)
├─ Simple queries (< 200ms)
└─ Validation (< 10ms)

# Slow path (async worker) :
├─ Job scraping (10-30s) → background task
├─ PDF generation (5-10s) → background task
├─ LLM calls (2-10s) → background task
├─ Email sending (1-3s per email) → bulk task
└─ Analytics recalc (5-30s) → scheduled job
```

**Key Libraries**

```
├─ SQLAlchemy 2.0 : ORM, async-first
├─ Alembic : Database migrations
├─ python-multipart : Form uploads
├─ python-jose : JWT tokens
├─ passlib : Password hashing (bcrypt)
├─ email-validator : Email validation
├─ python-dotenv : .env management
├─ httpx : Async HTTP client (API calls)
├─ BeautifulSoup4 : Web scraping
├─ pydantic-settings : Config management
├─ langchain : LLM abstractions
├─ langgraph : Agent orchestration
└─ opentelemetry : Observability
```

**Project Structure**

```
backend/
├─ app/
│  ├─ __init__.py
│  ├─ main.py                  # FastAPI app instance
│  ├─ config.py                # Settings (Pydantic)
│  ├─ dependencies.py          # Shared dependencies (DB, auth)
│  │
│  ├─ models/                  # SQLAlchemy models
│  │  ├─ __init__.py
│  │  ├─ user.py               # User model
│  │  ├─ profile.py            # Profile model
│  │  ├─ job.py                # Job posting model
│  │  ├─ application.py        # Application model
│  │  ├─ document.py           # CV/Letter versions
│  │  └─ audit.py              # Audit logging
│  │
│  ├─ schemas/                 # Pydantic request/response schemas
│  │  ├─ __init__.py
│  │  ├─ user.py               # User DTOs
│  │  ├─ profile.py
│  │  ├─ job.py
│  │  ├─ application.py
│  │  └─ common.py             # PaginatedResponse, etc.
│  │
│  ├─ api/
│  │  ├─ __init__.py
│  │  ├─ router.py             # Main router (combines all)
│  │  ├─ auth.py               # /auth endpoints
│  │  ├─ profile.py            # /profile endpoints
│  │  ├─ jobs.py               # /jobs endpoints
│  │  ├─ applications.py       # /applications endpoints
│  │  ├─ interviews.py         # /interviews endpoints
│  │  ├─ documents.py          # /documents endpoints
│  │  ├─ analytics.py          # /analytics endpoints
│  │  └─ health.py             # /health (k8s probes)
│  │
│  ├─ services/                # Business logic
│  │  ├─ __init__.py
│  │  ├─ auth_service.py       # User auth logic
│  │  ├─ profile_service.py    # Profile management
│  │  ├─ job_service.py        # Job search & filtering
│  │  ├─ application_service.py# Application management
│  │  ├─ document_service.py   # CV/Letter generation
│  │  ├─ email_service.py      # Email sending
│  │  ├─ llm_service.py        # LLM interactions (Claude, GPT)
│  │  └─ analytics_service.py  # Stats & insights
│  │
│  ├─ agents/                  # AI agent implementations
│  │  ├─ __init__.py
│  │  ├─ orchestrator.py       # Main coordinator
│  │  ├─ scout.py              # Job search agent
│  │  ├─ analyst.py            # Job analysis agent
│  │  ├─ ats_expert.py         # CV optimization agent
│  │  ├─ writer.py             # Letter generation agent
│  │  ├─ tracker.py            # Application tracking agent
│  │  ├─ reminder.py           # Follow-up scheduling agent
│  │  ├─ coach.py              # Interview coaching agent
│  │  └─ career_advisor.py     # Career analytics agent
│  │
│  ├─ tasks/                   # Celery/background tasks
│  │  ├─ __init__.py
│  │  ├─ scraping.py           # Job scraping tasks
│  │  ├─ email.py              # Email sending tasks
│  │  ├─ pdf.py                # PDF generation tasks
│  │  ├─ analytics.py          # Analytics computation
│  │  └─ cleanup.py            # Data cleanup jobs
│  │
│  ├─ utils/                   # Utilities
│  │  ├─ __init__.py
│  │  ├─ validators.py         # Custom validators
│  │  ├─ pdf_generator.py      # PDF lib wrappers
│  │  ├─ parsers.py            # CV/resume parsers
│  │  ├─ logger.py             # Logging setup
│  │  ├─ exceptions.py         # Custom exceptions
│  │  └─ converters.py         # Type converters
│  │
│  ├─ db/
│  │  ├─ __init__.py
│  │  └─ database.py           # SQLAlchemy setup, sessionmaker
│  │
│  ├─ middleware/
│  │  ├─ __init__.py
│  │  ├─ auth.py               # JWT verification middleware
│  │  ├─ logging.py            # Request logging
│  │  ├─ error_handling.py     # Global error handler
│  │  └─ rate_limiting.py      # Rate limiter (Redis-based)
│  │
│  └─ migrations/              # Alembic migrations
│     ├─ versions/
│     └─ env.py
│
├─ tests/
│  ├─ __init__.py
│  ├─ conftest.py              # Pytest fixtures
│  ├─ test_auth.py
│  ├─ test_profile.py
│  ├─ test_jobs.py
│  ├─ test_applications.py
│  ├─ test_agents/
│  └─ integration/             # Integration tests
│
├─ requirements.txt            # Pip dependencies
├─ Dockerfile                  # Docker build
├─ docker-compose.yml          # Local dev docker-compose
├─ pytest.ini                  # Pytest config
├─ .env.example                # Environment template
└─ main.py                     # Entry point (for local dev)
```

---

## 4. Architecture des données

### Database (PostgreSQL)

**Schéma conceptuel** :

```
User (Core)
├─ id (PK)
├─ email (unique)
├─ hashed_password
├─ full_name
├─ created_at
├─ updated_at
├─ deleted_at (soft delete)

Profile (One-to-One avec User)
├─ id (PK)
├─ user_id (FK)
├─ phone
├─ address
├─ about_me
├─ current_title
├─ years_experience
├─ preferred_contract (CDI, freelance, etc.)
├─ preferred_locations (JSONB array)
├─ salary_min_expectations
├─ available_date
├─ visa_sponsorship_required (boolean)

Experience (One-to-Many with Profile)
├─ id (PK)
├─ profile_id (FK)
├─ company
├─ title
├─ start_date
├─ end_date
├─ description
├─ technologies (JSONB array)
├─ impact_metrics (JSONB)

Education (One-to-Many with Profile)
├─ id (PK)
├─ profile_id (FK)
├─ institution
├─ degree
├─ field_of_study
├─ graduation_date

Skill (One-to-Many with Profile)
├─ id (PK)
├─ profile_id (FK)
├─ name
├─ level (junior, mid, senior, expert)
├─ category (technical, soft, language, etc.)

Document (One-to-Many with Profile)
├─ id (PK)
├─ profile_id (FK)
├─ type (cv, cover_letter)
├─ title
├─ version
├─ file_path (S3)
├─ status (active, archived)
├─ created_at

JobPosting (Scraped jobs)
├─ id (PK)
├─ external_id (source-unique)
├─ title
├─ company
├─ description (full text)
├─ required_skills (JSONB)
├─ required_experience (int years)
├─ location
├─ employment_type (CDI, freelance, stage)
├─ salary_min / salary_max (nullable)
├─ source (LinkedIn, Indeed, etc.)
├─ source_url
├─ posted_date
├─ scraped_at (created_at)
├─ updated_at

Application (Candidatures)
├─ id (PK)
├─ user_id (FK)
├─ job_id (FK)
├─ status (enum: DRAFT, READY, SENT, VIEWED, etc.)
├─ cv_version_id (FK Document)
├─ letter_version_id (FK Document)
├─ email_sent_at (nullable)
├─ email_opened_at (nullable, from tracking pixel)
├─ interviews (JSONB array of scheduled interviews)
├─ notes (text)
├─ result (enum: pending, rejected, offer, accepted)
├─ created_at
├─ updated_at

ApplicationEmail (Email tracker)
├─ id (PK)
├─ application_id (FK)
├─ email_sent_at
├─ email_opened_at (nullable)
├─ recipient_email
├─ email_type (initial, followup_1, followup_2, etc.)

Interview (Interview tracking)
├─ id (PK)
├─ application_id (FK)
├─ type (phone_screening, technical, round_n)
├─ scheduled_at
├─ completed_at (nullable)
├─ feedback (text, structured JSONB?)
├─ notes

SavedSearch (Saved job searches)
├─ id (PK)
├─ user_id (FK)
├─ name
├─ filters (JSONB: skills, locations, salary, etc.)
├─ created_at

AuditLog (RGPD requirement)
├─ id (PK)
├─ user_id (FK, nullable for system actions)
├─ entity_type (User, Profile, Application, etc.)
├─ entity_id
├─ action (create, update, delete)
├─ changes (JSONB: before/after)
├─ created_at
```

### Indexes

```sql
-- Performance indexes
CREATE INDEX idx_applications_user_id ON applications(user_id);
CREATE INDEX idx_applications_status ON applications(status);
CREATE INDEX idx_applications_created_at ON applications(created_at DESC);
CREATE INDEX idx_job_postings_title_gin ON job_postings USING GIN(to_tsvector('french', title));
CREATE INDEX idx_job_postings_description_gin ON job_postings USING GIN(to_tsvector('french', description));
CREATE INDEX idx_experiences_profile_id ON experiences(profile_id);
CREATE INDEX idx_skills_profile_id ON skills(profile_id);
CREATE INDEX idx_audit_log_user_id ON audit_log(user_id);
CREATE INDEX idx_audit_log_created_at ON audit_log(created_at DESC);

-- Unique constraints
ALTER TABLE users ADD CONSTRAINT uq_users_email UNIQUE(email);
ALTER TABLE profiles ADD CONSTRAINT uq_profiles_user_id UNIQUE(user_id);
```

### Cache Strategy (Redis)

```
Keys structure:

# User session
session:{session_id} → UserSession (TTL: 24h)

# User data (invalidate on write)
user:{user_id}:profile → Profile (TTL: 1h)
user:{user_id}:documents → [Document] (TTL: 30m)
user:{user_id}:skills → [Skill] (TTL: 1h)

# Job listings (long TTL, refresh periodically)
jobs:search:{search_hash} → [JobPosting] (TTL: 6h)
jobs:trending → [JobPosting] (TTL: 4h)
jobs:by_id:{job_id} → JobPosting (TTL: 24h)

# LLM cache (same prompts = same responses)
llm:cache:{prompt_hash} → {response} (TTL: 30d)

# Rate limiting
ratelimit:user:{user_id}:{endpoint} → counter (TTL: 1m)

# Background tasks
tasks:pending → {list of task IDs}
tasks:{task_id}:status → TaskStatus

# Queues
queue:emails → {list of email tasks}
queue:scraping → {list of scrape tasks}
queue:pdf_generation → {list of pdf tasks}
```

---

## 5. Architecture des agents IA

### Multi-Agent Orchestration (LangGraph)

**Pattern** : Supervisor + Specialized Agents

```python
# Pseudo-code structure

class CareerOSOrchestrator:
    """
    Main coordinator.
    Routes tasks to appropriate agents.
    Manages agent outputs and state.
    """
    
    def __init__(self):
        self.scout = ScoutAgent()           # Job search
        self.analyst = AnalystAgent()       # Job analysis
        self.ats_expert = ATSExpertAgent()  # CV optimization
        self.writer = WriterAgent()         # Letter generation
        self.tracker = TrackerAgent()       # Application tracking
        self.reminder = ReminderAgent()     # Follow-ups
        self.coach = InterviewCoachAgent()  # Interview prep
        self.advisor = CareerAdvisorAgent() # Analytics
        
    async def handle_user_request(self, user_id, request_type, params):
        """
        Routes request to appropriate agent(s).
        
        request_type ∈ [
            'search_jobs',
            'analyze_job',
            'prepare_application',
            'generate_letter',
            'prepare_interview',
            'get_analytics',
        ]
        """
        
        if request_type == 'search_jobs':
            jobs = await self.scout.search(params)
            return jobs
            
        elif request_type == 'analyze_job':
            analysis = await self.analyst.analyze(params['job_id'])
            return analysis
            
        elif request_type == 'prepare_application':
            # Multi-agent workflow
            job = await self.scout.get_job(params['job_id'])
            analysis = await self.analyst.analyze(job)
            optimized_cv = await self.ats_expert.optimize(job, user_profile)
            letter = await self.writer.generate(job, analysis, user_profile)
            return {
                'cv': optimized_cv,
                'letter': letter,
                'analysis': analysis,
            }
            
        # ... other request types
```

### Agents spécialisés

#### 1. Scout Agent (Job Search)

```python
class ScoutAgent:
    """
    Searches for job postings across multiple sources.
    
    Responsibilities:
    - Query LinkedIn, Indeed, Welcome To The Jungle APIs
    - Filter by user preferences
    - Dedup jobs
    - Rank by relevance
    """
    
    async def search(self, filters: SearchFilters) -> List[JobPosting]:
        tasks = [
            self.query_linkedin(filters),
            self.query_indeed(filters),
            self.query_wttj(filters),
            # ... other sources
        ]
        results = await asyncio.gather(*tasks)
        
        # Flatten and dedup
        all_jobs = [job for source in results for job in source]
        unique_jobs = self.dedup(all_jobs)
        
        # Rank by relevance
        ranked = await self.rank_by_relevance(unique_jobs, filters)
        return ranked
```

#### 2. Analyst Agent (Job Analysis)

```python
class AnalystAgent:
    """
    Deep analysis of job postings.
    
    Responsibilities:
    - Extract required skills
    - Extract technologies
    - Detect seniority level
    - Estimate salary
    - Identify ATS keywords
    - Generate compatibility score
    """
    
    async def analyze(self, job: JobPosting, user_profile: Profile) -> JobAnalysis:
        # Use LLM to extract structured data
        extraction = await self.llm.extract_job_requirements(job.description)
        
        # Calculate compatibility score
        compatibility = self.calculate_compatibility(
            extraction.required_skills,
            user_profile.skills,
            extraction.required_experience,
            user_profile.years_of_experience,
        )
        
        # Estimate salary if missing
        if not job.salary_min:
            job.salary_min, job.salary_max = await self.estimate_salary(
                job.title,
                job.company,
                job.location,
                extraction.required_experience,
            )
        
        return JobAnalysis(
            required_skills=extraction.required_skills,
            technologies=extraction.technologies,
            responsibilities=extraction.responsibilities,
            seniority_level=extraction.seniority_level,
            ats_keywords=extraction.ats_keywords,
            compatibility_score=compatibility,
            salary_estimate=(job.salary_min, job.salary_max),
        )
```

#### 3. ATS Expert Agent (CV Optimization)

```python
class ATSExpertAgent:
    """
    Optimizes CV for specific job posting.
    
    Responsibilities:
    - Parse CV structure
    - Extract keywords from job posting
    - Reorganize sections for relevance
    - Reword descriptions with keywords
    - Generate before/after report
    """
    
    async def optimize(self, cv: Document, job: JobPosting, analysis: JobAnalysis):
        # Parse CV
        cv_structure = self.parse_cv(cv.file_path)
        
        # Identify key sections and mutable parts
        sections = self.identify_sections(cv_structure)
        
        # LLM-powered rewriting
        optimized = await self.llm.rewrite_cv(
            cv_structure=cv_structure,
            job_keywords=analysis.ats_keywords,
            required_skills=analysis.required_skills,
            preserve_facts=True,  # Don't invent
        )
        
        # Generate report
        report = self.generate_report(cv_structure, optimized, analysis)
        
        return OptimizedCV(
            content=optimized,
            report=report,
            ats_score=await self.calculate_ats_score(optimized, analysis),
        )
```

#### 4. Writer Agent (Letter Generation)

```python
class WriterAgent:
    """
    Generates personalized cover letters and emails.
    
    Responsibilities:
    - Analyze company/job context
    - Generate letter structure
    - Create multiple tone variants
    - Personalize with user details
    """
    
    async def generate(self, job: JobPosting, analysis: JobAnalysis, user_profile: Profile):
        # Fetch company info (Crunchbase, Glassdoor)
        company_info = await self.fetch_company_context(job.company)
        
        # Generate letter with LLM
        letter = await self.llm.generate_cover_letter(
            job=job,
            analysis=analysis,
            user_profile=user_profile,
            company_info=company_info,
            tone='professional',
        )
        
        # Generate variants (modern, technical, etc.)
        variants = await asyncio.gather(
            self.llm.generate_cover_letter(..., tone='modern'),
            self.llm.generate_cover_letter(..., tone='technical'),
        )
        
        # Generate email body
        email = await self.llm.generate_email(
            letter=letter,
            tone='professional',
        )
        
        return {
            'letter': letter,
            'letter_variants': variants,
            'email': email,
        }
```

#### 5. Tracker Agent (Application Tracking)

```python
class TrackerAgent:
    """
    Tracks application status and updates.
    
    Responsibilities:
    - Monitor email opens (tracking pixels)
    - Update status based on interactions
    - Detect replies
    - Maintain history
    """
    
    async def track_application(self, application_id: str):
        app = await self.db.get_application(application_id)
        
        # Check if email was opened
        if app.email_opened_at:
            app.status = 'VIEWED'
        
        # Check if reply received
        reply = await self.check_email_reply(app.email_sent_to)
        if reply:
            app.status = 'INTERVIEWED' if reply.is_interview_request else 'REJECTED'
            app.last_interaction_at = now()
        
        await self.db.save(app)
```

#### 6. Reminder Agent (Follow-ups)

```python
class ReminderAgent:
    """
    Schedules and manages follow-up reminders.
    
    Responsibilities:
    - Schedule reminders (7 days after send)
    - Personalize follow-up messages
    - Respect business hours
    - Prevent spam
    """
    
    async def schedule_followups(self, application_id: str):
        app = await self.db.get_application(application_id)
        
        # Schedule 1st followup (7 days, business hours)
        followup_1_date = self.calculate_business_days(app.sent_at, days=7)
        await self.schedule_task(
            'send_followup_email',
            application_id=application_id,
            scheduled_at=followup_1_date,
            followup_number=1,
        )
        
        # Schedule 2nd followup (7 more days)
        followup_2_date = self.calculate_business_days(followup_1_date, days=7)
        await self.schedule_task(
            'send_followup_email',
            application_id=application_id,
            scheduled_at=followup_2_date,
            followup_number=2,
        )
```

#### 7. Coach Agent (Interview Preparation)

```python
class InterviewCoachAgent:
    """
    Prepares user for interviews.
    
    Responsibilities:
    - Fetch company/job context
    - Generate interview questions
    - Conduct simulated interview
    - Provide feedback
    """
    
    async def prepare_interview(self, application_id: str):
        app = await self.db.get_application(application_id)
        job = app.job
        
        # Fetch company context
        company_info = await self.fetch_company_context(job.company)
        
        # Generate questions
        hr_questions = await self.llm.generate_hr_questions(job, company_info)
        technical_questions = await self.llm.generate_technical_questions(job)
        
        # Create coaching session
        session = InterviewCoachingSession(
            application_id=application_id,
            hr_questions=hr_questions,
            technical_questions=technical_questions,
            company_info=company_info,
        )
        
        return session
    
    async def simulate_interview(self, session: InterviewCoachingSession, user_answers: List[str]):
        """
        Conduct simulated interview and provide feedback.
        """
        feedback = []
        
        for i, answer in enumerate(user_answers):
            question = session.all_questions[i]
            
            # Analyze answer
            analysis = await self.llm.analyze_interview_answer(
                question=question,
                answer=answer,
                job=session.job,
            )
            
            feedback.append(InterviewFeedback(
                question=question,
                answer=answer,
                clarity_score=analysis.clarity_score,
                relevance_score=analysis.relevance_score,
                confidence_score=analysis.confidence_score,
                suggestions=analysis.improvement_suggestions,
            ))
        
        return InterviewSimulationResult(
            feedback=feedback,
            overall_score=self.calculate_overall_score(feedback),
            readiness_level=self.calculate_readiness_level(feedback),
        )
```

#### 8. Career Advisor Agent (Analytics)

```python
class CareerAdvisorAgent:
    """
    Analyzes career search performance.
    
    Responsibilities:
    - Calculate conversion rates
    - Identify patterns
    - Provide recommendations
    - Predict offer timing
    """
    
    async def analyze_performance(self, user_id: str) -> CareerAnalytics:
        apps = await self.db.get_user_applications(user_id)
        
        metrics = {
            'total_applications': len(apps),
            'response_rate': self.calculate_response_rate(apps),
            'interview_rate': self.calculate_interview_rate(apps),
            'offer_rate': self.calculate_offer_rate(apps),
            'avg_time_to_interview': self.calculate_avg_time(apps, 'interview'),
            'avg_time_to_offer': self.calculate_avg_time(apps, 'offer'),
        }
        
        # Generate recommendations
        recommendations = await self.llm.generate_recommendations(
            metrics=metrics,
            applications=apps,
            user_profile=user_profile,
        )
        
        return CareerAnalytics(
            metrics=metrics,
            recommendations=recommendations,
        )
```

---

## 6. API Design (REST)

### Endpoints Overview

```
Authentication
├─ POST /auth/signup
├─ POST /auth/login
├─ POST /auth/logout
├─ POST /auth/refresh-token
└─ POST /auth/verify-email

Profile Management
├─ GET /profile
├─ PUT /profile
├─ POST /profile/avatar
├─ GET /profile/experiences
├─ POST /profile/experiences
├─ PUT /profile/experiences/{id}
├─ DELETE /profile/experiences/{id}
├─ GET /profile/education
├─ POST /profile/education
├─ GET /profile/skills
├─ POST /profile/skills
├─ PUT /profile/skills/{id}
└─ DELETE /profile/skills/{id}

Job Search
├─ GET /jobs/search (query: skills, location, salary, etc.)
├─ GET /jobs/{id}
├─ GET /jobs/trending
├─ POST /jobs/saved-searches
├─ GET /jobs/saved-searches
└─ PUT /jobs/saved-searches/{id}

Applications
├─ GET /applications
├─ GET /applications/{id}
├─ POST /applications (create draft)
├─ PUT /applications/{id} (update status)
├─ DELETE /applications/{id}
├─ POST /applications/{id}/send
├─ POST /applications/{id}/feedback
└─ GET /applications/stats

Documents
├─ GET /documents
├─ POST /documents (upload CV or letter)
├─ DELETE /documents/{id}
├─ POST /documents/{id}/generate-cv-variant
└─ POST /documents/{id}/generate-letter-variant

Interviews
├─ GET /interviews/{application_id}
├─ POST /interviews/{application_id}/start-coaching
├─ POST /interviews/{application_id}/submit-answer
├─ GET /interviews/{application_id}/feedback
└─ POST /interviews/{application_id}/schedule

Analytics
├─ GET /analytics/dashboard
├─ GET /analytics/applications
├─ GET /analytics/performance
└─ GET /analytics/trends

Health
├─ GET /health
└─ GET /readiness
```

### Example Endpoints (Detailed)

```yaml
# Search jobs
GET /jobs/search?
  skills=Python,Kubernetes&
  location=Paris,Remote&
  contract_type=CDI&
  salary_min=50000&
  years_experience_min=3&
  page=1&
  limit=20

Response 200:
{
  "total": 1250,
  "page": 1,
  "limit": 20,
  "jobs": [
    {
      "id": "job_xxx",
      "title": "Sr. Backend Engineer",
      "company": "TechCorp",
      "description": "...",
      "location": "Paris (Remote)",
      "employment_type": "CDI",
      "salary": {"min": 50000, "max": 65000},
      "required_skills": ["Python", "FastAPI", "Kubernetes"],
      "posted_date": "2026-08-01",
      "source": "LinkedIn",
      "source_url": "...",
      "compatibility_score": 0.82
    },
    ...
  ]
}

---

# Prepare application
POST /applications
{
  "job_id": "job_xxx"
}

Response 201:
{
  "application_id": "app_yyy",
  "status": "DRAFT",
  "job": {...},
  "analysis": {
    "required_skills": [...],
    "technologies": [...],
    "compatibility_score": 0.82,
    "ats_keywords": [...]
  },
  "optimized_cv": {
    "id": "cv_variant_1",
    "ats_score": 0.85,
    "changes_report": {
      "reordered_sections": ["Summary", "Skills", "Experience"],
      "added_keywords": ["Kubernetes", "Docker"],
      "modified_descriptions": [...]
    }
  },
  "generated_letter": {
    "id": "letter_draft_1",
    "content": "Dear Hiring Manager...",
    "variants": [
      {"tone": "modern", "content": "..."},
      {"tone": "technical", "content": "..."}
    ]
  },
  "generated_email": {
    "subject": "Application for Sr. Backend Engineer - Your Expertise in FastAPI",
    "body": "Hi there,..."
  }
}

---

# Send application
POST /applications/app_yyy/send
{
  "cv_variant_id": "cv_variant_1",
  "letter_variant_id": "letter_draft_1",
  "email_subject": "Application for Sr. Backend Engineer - Your Expertise in FastAPI",
  "email_body": "Hi there,..."
}

Response 200:
{
  "application_id": "app_yyy",
  "status": "SENT",
  "sent_at": "2026-08-02T14:30:00Z",
  "next_followup": "2026-08-09"
}
```

---

## 7. Security Architecture

### Authentication & Authorization

```
Flow:
1. User email + password → /auth/login
2. Backend verifies (bcrypt hash check)
3. Issues JWT token + refresh token
4. Client stores tokens (localStorage or secure cookie)
5. Subsequent requests: Authorization: Bearer {JWT}
6. Backend validates JWT + checks expiry

Tokens:
├─ Access token : 15 min TTL (short-lived)
├─ Refresh token : 30 days TTL (long-lived, httpOnly cookie)
└─ CSRF token : For form submissions

Middleware:
├─ Extract JWT from Authorization header
├─ Validate signature (verify it wasn't tampered)
├─ Check expiry
├─ If expired + refresh token valid → issue new access token
└─ If both expired → redirect to login
```

### Data Encryption

```
At-rest:
├─ Database passwords : bcrypt (one-way hash)
├─ Sensitive fields (SSN, salary) : AES-256 encryption (if stored)
├─ API keys : encrypted in vault (AWS Secrets Manager)
└─ Personal data (email, phone) : No encryption needed (GDPR compliant)

In-transit:
├─ HTTPS / TLS 1.3 everywhere
├─ Certificate pinning (if mobile app future)
└─ API-to-API : mTLS (if microservices)
```

### GDPR Compliance

```
Requirements:
├─ Data minimization : Only store needed data
├─ User consent : Email confirmation, privacy policy acceptance
├─ Right to access : Endpoint to export all user data (JSON)
├─ Right to be forgotten : Cascade delete user + all related data
├─ Audit logging : Track who accessed what, when
├─ Data processing agreement : For EU-based users
├─ Breach notification : Incident response plan

Implementation:
├─ DELETE /auth/delete-account → Cascade deletes everything
├─ GET /export-data → Generates JSON dump
├─ AuditLog table : Every CRUD operation logged
└─ Privacy policy + Terms of Service (lawyer-reviewed)
```

### Rate Limiting

```
Global:
├─ 10,000 requests per user per hour
├─ 100 requests per minute per IP

Per-endpoint:
├─ /auth/login : 5 attempts per minute (prevent brute force)
├─ /jobs/search : 30 searches per hour (scraping prevention)
├─ /documents/generate : 10 per hour (LLM cost control)
└─ Email sending : 100 emails per hour (prevent spam)

Implementation:
├─ Redis-backed sliding window counter
├─ Respond with 429 Too Many Requests
├─ Include Retry-After header
└─ Track in analytics
```

---

## 8. Deployment Architecture

### Container + Kubernetes

```yaml
# Docker image structure
Dockerfile:
├─ Base : python:3.11-slim
├─ Install dependencies : pip install -r requirements.txt
├─ Copy code
├─ Expose port 8000
└─ CMD : uvicorn app.main:app --host 0.0.0.0

# Kubernetes deployment
deployment.yaml:
├─ Replicas : 3 (high-availability)
├─ Resource requests/limits :
│  ├─ CPU : 500m requested, 1000m limit
│  └─ Memory : 512Mi requested, 1Gi limit
├─ Liveness probe : GET /health
├─ Readiness probe : GET /readiness
└─ Rolling update strategy

service.yaml:
├─ Type : ClusterIP (internal) or LoadBalancer (external)
├─ Port : 80/443
└─ Target port : 8000

ingress.yaml:
├─ Route : careeeros.ai/* → service:8000
├─ TLS : Let's Encrypt certificate
└─ Rate limiting : nginx rate limit module
```

### CI/CD Pipeline (GitHub Actions)

```yaml
# .github/workflows/deploy.yml

on: [push to main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest --cov=app tests/
      - run: flake8 app --max-line-length=100
      - run: mypy app --strict

  build-and-push:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}
      - uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: |
            ${{ secrets.DOCKERHUB_USERNAME }}/careeeros:latest
            ${{ secrets.DOCKERHUB_USERNAME }}/careeeros:${{ github.sha }}

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: azure/setup-kubectl@v3
      - name: Update deployment
        run: |
          kubectl set image deployment/careeeros-api \
            app=${{ secrets.DOCKERHUB_USERNAME }}/careeeros:${{ github.sha }} \
            -n production
          kubectl rollout status deployment/careeeros-api -n production
```

---

## 9. Observability & Monitoring

### Logging

```
Structured logging (JSON):
├─ Timestamp
├─ Level (INFO, WARNING, ERROR, CRITICAL)
├─ Logger name (module)
├─ Message
├─ Request ID (trace across services)
└─ User ID (GDPR-safe logging)

Aggregation:
├─ ELK Stack (Elasticsearch, Logstash, Kibana) or
├─ CloudWatch / DataDog
└─ Alert on error rates > 1%
```

### Metrics

```
Application metrics:
├─ Request latency (p50, p95, p99)
├─ Request count by endpoint
├─ Error rate
├─ LLM API latency
├─ Database query duration
└─ Job scraping duration

Business metrics:
├─ User sign-ups/day
├─ Applications sent/day
├─ Conversion rate (interviews/applications)
├─ Offer rate (offers/applications)
└─ Feature usage (% users using coaching, etc.)

Infrastructure metrics:
├─ CPU usage
├─ Memory usage
├─ Disk I/O
├─ Database connections
└─ Redis memory usage
```

### Tracing

```
Distributed tracing (OpenTelemetry):
├─ Trace request from frontend → backend → DB → LLM
├─ Identify slow spans
├─ Correlate errors with slow operations
└─ Tools: Jaeger, DataDog, or AWS X-Ray
```

---

## 10. Summary & Next Steps

### Architecture Highlights
✅ Modular multi-agent system (scalable, testable)
✅ Async-first backend (handles I/O, LLM calls)
✅ Serverless-ready (stateless services)
✅ Observability built-in (logging, metrics, tracing)
✅ Security-first (encryption, GDPR, audit logging)
✅ Production-grade (tests, CI/CD, load balancing)

### Trade-offs & Justifications
1. **FastAPI vs Django** : Speed, async-first, simpler for APIs
2. **PostgreSQL vs NoSQL** : Structured data, transactions, ACID guarantee
3. **LangGraph vs custom agents** : Proven framework, good DX, active community
4. **Kubernetes vs serverless** : Better for stateful services (background workers)
5. **Redis vs database cache** : Speed, TTL management, queue support

### Open Questions for Product/Design
1. Should we support user-created templates (for teams, future B2B)?
2. What's the max frequency for automated actions (emails, relances)?
3. Do we need real-time notifications, or polling is OK?
4. Should interview coaching support voice input (future)?
5. Do we need marketplace/partner integrations (future)?

---

**Next Phase** :
- [ ] Database schema finalized (detailed SQL)
- [ ] API specification complete (OpenAPI 3.0)
- [ ] UI/UX wireframes + design system
- [ ] Project repository setup (GitHub, Docker, K8s manifests)
- [ ] Spike on LLM cost optimization
- [ ] Security audit (penetration test checklist)

**Estimated effort** :
- Phase 1 (MVP) : 8-10 weeks
- Phase 2 (Extended features) : 6-8 weeks
- Phase 3 (Polish + launch) : 4-6 weeks

---

**Signoff** :
- [ ] Arch Lead approves tech stack choices
- [ ] Product validates persona support
- [ ] Sec Lead OK with GDPR/data handling
- [ ] Go ahead for Phase 1 implementation
