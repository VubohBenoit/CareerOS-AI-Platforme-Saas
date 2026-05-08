"""
Auth routes
POST /auth/register  → create recruiter account
POST /auth/login     → login, returns JWT
GET  /auth/me        → current user info
POST /auth/logout    → client-side only (JWT is stateless)
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr

from services.auth import (
    get_user_by_email, create_user, verify_password,
    create_token, verify_token
)

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer(auto_error=False)


# ── Schemas ──────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    email: str
    name: str
    company: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


# ── Dependency ────────────────────────────────────────────

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        raise HTTPException(401, "Non authentifié")
    payload = verify_token(credentials.credentials)
    if not payload:
        raise HTTPException(401, "Token invalide ou expiré")
    return payload


# ── Endpoints ─────────────────────────────────────────────

@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest):
    user = get_user_by_email(body.email)
    if not user:
        raise HTTPException(401, "Identifiants incorrects")
    if not verify_password(body.password, user["password_hash"]):
        raise HTTPException(401, "Identifiants incorrects")

    token = create_token({
        "sub":     user["email"],
        "name":    user["name"],
        "company": user["company"],
    })
    return TokenResponse(
        access_token=token,
        user={"email": user["email"], "name": user["name"], "company": user["company"]},
    )


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(body: RegisterRequest):
    if get_user_by_email(body.email):
        raise HTTPException(409, "Cet e-mail est déjà utilisé")
    if len(body.password) < 8:
        raise HTTPException(422, "Le mot de passe doit comporter au moins 8 caractères")

    user = create_user(body.email, body.name, body.company, body.password)
    if not user:
        raise HTTPException(500, "Erreur lors de la création du compte")

    token = create_token({"sub": user["email"], "name": user["name"], "company": user["company"]})
    return TokenResponse(
        access_token=token,
        user={"email": user["email"], "name": user["name"], "company": user["company"]},
    )


@router.get("/me")
async def me(current_user: dict = Depends(get_current_user)):
    return current_user
