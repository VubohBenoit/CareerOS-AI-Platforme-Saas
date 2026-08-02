# CareerOS AI — Week 1-2 Implementation Guide

**Status:** Implementation Ready
**Target Audience:** Backend & Frontend Leads
**Duration:** 2 weeks
**Deliverable:** Local dev working + first APIs functional

---

## Overview

This guide breaks down exactly what each team needs to build in Weeks 1-2 to have a working local development environment and basic functionality.

---

## Week 1: Foundation & Setup

### Day 1: Environment & Onboarding

**All Team**
```bash
# Clone repo
git clone <your-repo> careeeros-ai
cd careeeros-ai

# Copy environment files
cp backend/.env.example backend/.env

# Start services (will take ~5 min on first run)
make setup

# Verify everything is running
make health-check
docker-compose ps
```

**Expected Output:**
```
CONTAINER ID   IMAGE                      STATUS
xxx            careeeros-db               Up 2 minutes (healthy)
xxx            careeeros-redis            Up 2 minutes (healthy)
xxx            careeeros-backend          Up 1 minute
xxx            careeeros-nginx            Up 1 minute
```

**Backend Lead**
- [ ] Review `ARCHITECTURE.md` (sections 3-5: tech stack, database, APIs)
- [ ] Review `docs/DATABASE_SCHEMA.md`
- [ ] Test: `docker-compose exec backend python -m pytest app/db/database.py`
- [ ] Confirm PostgreSQL accessible: `make shell-db`

**Frontend Lead**
- [ ] Review `ARCHITECTURE.md` (section 3: frontend stack)
- [ ] Review `QUICK_START.md` (frontend section)
- [ ] Test: `npm install` in `frontend/` folder
- [ ] Confirm dependencies resolve

**DevOps Engineer**
- [ ] Verify Docker Compose working
- [ ] Check Nginx config: `docker-compose exec nginx nginx -t`
- [ ] Confirm all containers healthy
- [ ] Create `.gitignore` updates if needed

---

### Days 2-3: Database Setup

**Backend Lead + DevOps**

**Goal:** Database schema created + migrations working

```bash
# Generate first migration
cd backend
alembic revision --autogenerate -m "Initial schema - users and profiles"

# Review migration file (backend/migrations/versions/xxx_initial_schema.py)
# Should include all models from app/models/

# Apply migration
alembic upgrade head

# Verify tables created
make shell-db
# In psql:
\dt
\d users
\d profiles
# etc.

# Test connection from backend
docker-compose exec backend python
>>> from app.db.database import SessionLocal
>>> db = SessionLocal()
>>> db.execute("SELECT 1")
# Should return successfully
```

**Deliverable:**
- [ ] All tables created in PostgreSQL
- [ ] Foreign keys & indexes in place
- [ ] Migration file committed to git
- [ ] Backup migration script tested

---

### Days 4-5: Basic Auth APIs

**Backend Team**

**Goal:** User signup/login working

```python
# backend/app/schemas/user.py (Create this)
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    is_active: bool
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
```

```python
# backend/app/services/auth_service.py (Create this)
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import jwt
from sqlalchemy.orm import Session
from app.models.user import User
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain: str, hashed: str) -> bool:
        return pwd_context.verify(plain, hashed)
    
    @staticmethod
    def create_access_token(user_id: str, expires_in: int = 15) -> str:
        """Create JWT access token (15 min default)"""
        expire = datetime.utcnow() + timedelta(minutes=expires_in)
        to_encode = {"sub": str(user_id), "exp": expire}
        encoded = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return encoded
    
    @staticmethod
    def create_tokens(user_id: str):
        """Create both access and refresh tokens"""
        access_token = AuthService.create_access_token(user_id)
        refresh_token = jwt.encode(
            {"sub": str(user_id), "type": "refresh"},
            settings.SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        return {"access_token": access_token, "refresh_token": refresh_token}

    @staticmethod
    def signup(db: Session, email: str, password: str, full_name: str) -> User:
        """Create new user"""
        # Check email exists
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            raise ValueError("Email already registered")
        
        # Hash password
        hashed = AuthService.hash_password(password)
        
        # Create user
        user = User(
            email=email,
            hashed_password=hashed,
            full_name=full_name,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def login(db: Session, email: str, password: str) -> User:
        """Authenticate user"""
        user = db.query(User).filter(User.email == email).first()
        if not user or not AuthService.verify_password(password, user.hashed_password):
            raise ValueError("Invalid email or password")
        if not user.is_active:
            raise ValueError("User account disabled")
        return user
```

```python
# backend/app/api/auth.py (Create this)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserResponse, TokenResponse
from app.services.auth_service import AuthService
from app.db.database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=UserResponse)
async def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    """Create new user account"""
    try:
        user = AuthService.signup(db, user_data.email, user_data.password, user_data.full_name)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=TokenResponse)
async def login(email: str, password: str, db: Session = Depends(get_db)):
    """Login and get tokens"""
    try:
        user = AuthService.login(db, email, password)
        tokens = AuthService.create_tokens(user.id)
        return tokens
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
```

**Then update main API router:**
```python
# backend/app/api/router.py
from app.api.auth import router as auth_router

router.include_router(auth_router, tags=["auth"])
```

**Tests:**
```python
# backend/tests/test_auth.py
import pytest
from app.schemas.user import UserCreate
from app.services.auth_service import AuthService

def test_signup(db):
    """Test user signup"""
    user = AuthService.signup(db, "test@example.com", "password123", "Test User")
    assert user.email == "test@example.com"
    assert user.is_active

def test_login(db):
    """Test login"""
    AuthService.signup(db, "test@example.com", "password123", "Test User")
    user = AuthService.login(db, "test@example.com", "password123")
    assert user.email == "test@example.com"

def test_password_hashing():
    """Test password is hashed"""
    hashed = AuthService.hash_password("mypassword")
    assert hashed != "mypassword"
    assert AuthService.verify_password("mypassword", hashed)
```

**Run:**
```bash
cd backend
pytest tests/test_auth.py -v
```

**Deliverable:**
- [ ] Signup API working (`POST /api/v1/auth/signup`)
- [ ] Login API working (`POST /api/v1/auth/login`)
- [ ] Returns JWT tokens
- [ ] Tests passing (password hashing, auth flow)
- [ ] Postman/curl can test it

---

## Week 2: Core Features

### Days 1-2: Profile Management

**Backend Team**

**Goal:** Profile CRUD APIs working

Create `backend/app/services/profile_service.py`:
```python
from sqlalchemy.orm import Session
from app.models.profile import Profile, Skill, Experience, Education
from app.models.user import User
from uuid import UUID

class ProfileService:
    @staticmethod
    def get_or_create(db: Session, user_id: UUID) -> Profile:
        """Get or create user profile"""
        profile = db.query(Profile).filter(Profile.user_id == user_id).first()
        if not profile:
            profile = Profile(user_id=user_id)
            db.add(profile)
            db.commit()
            db.refresh(profile)
        return profile
    
    @staticmethod
    def update(db: Session, user_id: UUID, data: dict) -> Profile:
        """Update profile fields"""
        profile = ProfileService.get_or_create(db, user_id)
        for key, value in data.items():
            if value is not None:
                setattr(profile, key, value)
        db.commit()
        db.refresh(profile)
        return profile
    
    @staticmethod
    def add_skill(db: Session, user_id: UUID, name: str, level: str) -> Skill:
        """Add skill to profile"""
        profile = ProfileService.get_or_create(db, user_id)
        skill = Skill(profile_id=profile.id, name=name, level=level)
        db.add(skill)
        db.commit()
        db.refresh(skill)
        return skill
```

Create `backend/app/api/profile.py`:
```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.profile_service import ProfileService
# Create schemas in backend/app/schemas/profile.py

router = APIRouter(prefix="/profile", tags=["profile"])

@router.get("")
async def get_profile(db: Session = Depends(get_db)):
    """Get current user profile"""
    # TODO: Add auth dependency to get current user
    pass

@router.put("")
async def update_profile(profile_data: dict, db: Session = Depends(get_db)):
    """Update profile"""
    pass

@router.post("/skills")
async def add_skill(name: str, level: str, db: Session = Depends(get_db)):
    """Add skill"""
    pass
```

**Deliverable:**
- [ ] Profile endpoints implemented
- [ ] Tests for CRUD operations
- [ ] Postman collection for testing

---

### Days 3-4: Job Search API (Mock Data)

**Backend Team**

**Goal:** Job search endpoints with mock data

```python
# backend/app/services/job_service.py
from sqlalchemy.orm import Session
from app.models.job import JobPosting

class JobService:
    @staticmethod
    def search(db: Session, skills: list = None, location: str = None, limit: int = 20):
        """Search jobs with filters"""
        query = db.query(JobPosting)
        
        if location:
            query = query.filter(JobPosting.location.ilike(f"%{location}%"))
        
        if skills:
            # JSONB contains any of the skills
            for skill in skills:
                query = query.filter(JobPosting.required_skills.contains([skill]))
        
        return query.limit(limit).all()

# Add to backend/app/api/jobs.py
@router.get("/search")
async def search_jobs(
    skills: list = None,
    location: str = None,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Search job postings"""
    jobs = JobService.search(db, skills, location, limit)
    return jobs
```

**Add mock data script:**
```python
# backend/scripts/seed_jobs.py
from app.db.database import SessionLocal
from app.models.job import JobPosting
from datetime import datetime

def seed_jobs():
    db = SessionLocal()
    
    jobs = [
        JobPosting(
            title="Senior Python Developer",
            company="TechCorp",
            description="Looking for experienced Python developer...",
            location="Paris",
            employment_type="CDI",
            source="manual",
            required_skills=["Python", "FastAPI", "PostgreSQL"],
            required_technologies=["Docker", "Kubernetes"],
            posted_date=datetime.utcnow(),
        ),
        # Add more jobs...
    ]
    
    db.add_all(jobs)
    db.commit()
    print(f"Seeded {len(jobs)} jobs")

if __name__ == "__main__":
    seed_jobs()
```

**Run seed:**
```bash
cd backend
python scripts/seed_jobs.py
```

**Deliverable:**
- [ ] Job search API implemented
- [ ] Mock data seeded
- [ ] Filters working (skills, location)
- [ ] API testable

---

### Days 5: Frontend Auth UI

**Frontend Team**

**Goal:** Login/Signup pages functional

Create `frontend/app/(auth)/login/page.tsx`:
```typescript
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      if (response.ok) {
        const { access_token } = await response.json();
        localStorage.setItem('token', access_token);
        router.push('/dashboard');
      } else {
        alert('Login failed');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen items-center justify-center">
      <form onSubmit={handleLogin} className="w-full max-w-sm space-y-4 p-6">
        <h1 className="text-2xl font-bold">Login</h1>
        
        <Input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        
        <Input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        
        <Button type="submit" disabled={loading} className="w-full">
          {loading ? 'Logging in...' : 'Login'}
        </Button>
      </form>
    </div>
  );
}
```

**Deliverable:**
- [ ] Login page created
- [ ] Signup page created
- [ ] Form validation working
- [ ] Token stored in localStorage
- [ ] Redirect to dashboard on success

---

## Integration: Week 2 End

### Full Flow Test

```bash
# Terminal 1: Start backend
cd backend
uvicorn app.main:app --reload

# Terminal 2: Start frontend
cd frontend
npm run dev

# Browser: http://localhost:3000
# 1. Click Signup
# 2. Fill form (email, password, name)
# 3. Submit → check backend logs for success
# 4. Click Login
# 5. Login with same credentials
# 6. Should see dashboard
```

---

## Milestone: Week 2 Complete

**What Should Work:**
- ✅ Docker-compose up runs all services
- ✅ PostgreSQL has schema
- ✅ User signup working
- ✅ User login working
- ✅ Profile CRUD working
- ✅ Job search API working
- ✅ Frontend login/signup pages working
- ✅ All tests passing

**Git Status:**
```bash
git log --oneline | head -10
# Should see commits like:
# - feat: implement auth APIs
# - feat: add job search endpoints
# - feat: create auth UI
# - feat: seed mock job data
```

---

## Week 3 Preview (What Comes Next)

- [ ] LLM integration (job analysis agent)
- [ ] CV upload & parsing
- [ ] Application creation
- [ ] Dashboard UI

---

**Status:** Implementation Ready
**Estimated Time:** 10 working days (2 weeks)
**Team:** 4-5 engineers
**Success Criteria:** All deliverables checked ✓

