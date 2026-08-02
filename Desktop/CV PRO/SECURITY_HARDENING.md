# 🔐 Security Hardening Guide

## Authentication & Authorization

### JWT Best Practices
```python
# backend/app/services/auth_service.py
from datetime import datetime, timedelta
from jose import JWTError, jwt

class AuthService:
    def create_access_token(self, user_id: str) -> str:
        # Short expiration (15 minutes)
        expires = datetime.utcnow() + timedelta(minutes=15)
        payload = {
            "sub": user_id,
            "exp": expires,
            "iat": datetime.utcnow(),
            "type": "access"
        }
        return jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    
    def create_refresh_token(self, user_id: str) -> str:
        # Long expiration (7 days)
        expires = datetime.utcnow() + timedelta(days=7)
        payload = {
            "sub": user_id,
            "exp": expires,
            "type": "refresh"
        }
        return jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    
    def verify_token(self, token: str, token_type: str = "access"):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            if payload.get("type") != token_type:
                raise JWTError("Invalid token type")
            return payload["sub"]
        except JWTError:
            return None
```

### Password Security
```python
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # Strong hashing
)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)
```

---

## Data Protection

### Encryption at Rest
```python
from cryptography.fernet import Fernet

class EncryptionService:
    def __init__(self):
        self.cipher = Fernet(ENCRYPTION_KEY)
    
    def encrypt(self, data: str) -> str:
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted: str) -> str:
        return self.cipher.decrypt(encrypted.encode()).decode()

# Usage: Encrypt sensitive fields
class User:
    email = Column(String)
    ssn = Column(String)  # Encrypted
    
    @property
    def decrypted_ssn(self):
        return encryption_service.decrypt(self.ssn)
```

### HTTPS/TLS
```nginx
# nginx.conf
server {
    listen 443 ssl http2;
    
    ssl_certificate /etc/letsencrypt/live/careerosai.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/careerosai.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Force HTTPS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
}
```

---

## API Security

### Rate Limiting
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/auth/login")
@limiter.limit("5/minute")
async def login(credentials: LoginRequest):
    # Max 5 login attempts per minute
    pass

@app.get("/api/jobs")
@limiter.limit("100/minute")
async def list_jobs():
    # Max 100 requests per minute
    pass
```

### Input Validation
```python
from pydantic import BaseModel, EmailStr, validator

class UserSignup(BaseModel):
    email: EmailStr  # Validates email format
    password: str
    full_name: str
    
    @validator('password')
    def password_strong(cls, v):
        if len(v) < 12:
            raise ValueError('Password too short')
        if not any(c.isupper() for c in v):
            raise ValueError('Need uppercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Need digit')
        return v
    
    @validator('full_name')
    def no_sql_injection(cls, v):
        if any(c in v for c in ["'", '"', ";", "--"]):
            raise ValueError('Invalid characters')
        return v
```

### CORS Configuration
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://careerosai.com",
        "https://www.careerosai.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
    max_age=3600
)
```

---

## Infrastructure Security

### Security Groups
```hcl
resource "aws_security_group" "alb" {
  name = "careerosai-alb-sg"
  
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # HTTP
  }
  
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # HTTPS
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "api" {
  name = "careerosai-api-sg"
  
  ingress {
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]  # Only from ALB
  }
}

resource "aws_security_group" "database" {
  name = "careerosai-db-sg"
  
  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.api.id]  # Only from API
  }
}
```

### VPC Hardening
```hcl
# Private subnets for databases
resource "aws_subnet" "private" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "us-east-1b"
  
  # No internet access
  map_public_ip_on_launch = false
}

# NAT Gateway for outbound traffic
resource "aws_nat_gateway" "main" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public.id
}

resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id
  
  route {
    destination_cidr_block = "0.0.0.0/0"
    nat_gateway_id         = aws_nat_gateway.main.id
  }
}
```

---

## Compliance & Auditing

### GDPR Compliance
```python
# Implement right to be forgotten
@app.delete("/api/users/{user_id}")
async def delete_user(user_id: str, db: Session):
    # Delete all user data
    user = db.query(User).filter(User.id == user_id).first()
    db.delete(user)
    
    # Delete applications
    applications = db.query(Application).filter(
        Application.user_id == user_id
    ).all()
    for app in applications:
        db.delete(app)
    
    # Log for compliance
    audit_log.record("USER_DELETED", user_id=user_id)
    
    db.commit()
    return {"status": "deleted"}
```

### Audit Logging
```python
# backend/app/models/audit.py
class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(String, primary_key=True)
    user_id = Column(String)
    action = Column(String)  # LOGIN, CREATE_APP, DELETE_ACCOUNT
    resource = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String)
    user_agent = Column(String)
    
@app.middleware("http")
async def audit_middleware(request: Request, call_next):
    user_id = request.state.user_id if hasattr(request.state, 'user_id') else None
    
    response = await call_next(request)
    
    if user_id and request.method != "GET":
        audit_log = AuditLog(
            user_id=user_id,
            action=f"{request.method}_{request.url.path}",
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent")
        )
        db.add(audit_log)
        db.commit()
    
    return response
```

---

## Security Checklist

Before Production:
- [ ] All passwords hashed (bcrypt)
- [ ] All API endpoints authenticated
- [ ] HTTPS/TLS enabled
- [ ] Rate limiting configured
- [ ] Input validation on all endpoints
- [ ] CORS properly configured
- [ ] Security headers set
- [ ] Database backups encrypted
- [ ] API keys stored securely (.env)
- [ ] No hardcoded secrets in code
- [ ] SQL injection protection (ORM)
- [ ] XSS protection (output encoding)
- [ ] CSRF tokens implemented
- [ ] Secrets rotation policy
- [ ] DDoS protection (WAF)
- [ ] Regular security audits
- [ ] Penetration testing done
- [ ] Compliance audit passed

---

**Security is not optional. It's essential.** 🔐

