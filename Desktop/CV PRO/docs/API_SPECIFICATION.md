# CareerOS AI — API Specification (OpenAPI 3.0)

**Status:** Phase 1 MVP Endpoints
**Version:** 1.0.0
**Base URL:** `http://localhost:8000/api/v1` (dev) | `https://api.careeeros.ai/v1` (prod)

---

## Authentication

All endpoints (except auth) require JWT token in `Authorization` header:

```
Authorization: Bearer {access_token}
```

Tokens expire in 15 minutes. Use refresh token to get new access token.

---

## Endpoints

### Authentication

#### `POST /auth/signup`
Create new user account.

**Request:**
```json
{
  "email": "jane@example.com",
  "password": "securePassword123",
  "full_name": "Jane Doe"
}
```

**Response (201):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "jane@example.com",
  "full_name": "Jane Doe",
  "is_active": true,
  "created_at": "2026-08-02T10:00:00Z"
}
```

**Errors:**
- `400 Bad Request` - Invalid input or email already exists
- `422 Unprocessable Entity` - Validation error

---

#### `POST /auth/login`
Authenticate and get tokens.

**Request:**
```json
{
  "email": "jane@example.com",
  "password": "securePassword123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 900
}
```

**Errors:**
- `401 Unauthorized` - Invalid credentials
- `400 Bad Request` - User not found or inactive

---

#### `POST /auth/refresh`
Get new access token using refresh token.

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 900
}
```

---

### Profile

#### `GET /profile`
Get current user profile.

**Response (200):**
```json
{
  "id": "650e8400-e29b-41d4-a716-446655440001",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "phone": "+33612345678",
  "address": "10 Rue de la Paix, Paris, France",
  "about_me": "Senior Python developer...",
  "current_title": "Backend Engineer",
  "years_experience": 5,
  "preferred_contract": "CDI",
  "preferred_locations": ["Paris", "Remote"],
  "salary_min_expectations": 55000,
  "available_date": "2026-09-01T00:00:00Z",
  "visa_sponsorship_required": false,
  "created_at": "2026-08-02T10:00:00Z",
  "updated_at": "2026-08-02T10:00:00Z"
}
```

---

#### `PUT /profile`
Update user profile.

**Request:**
```json
{
  "phone": "+33612345678",
  "about_me": "Experienced Python developer...",
  "current_title": "Senior Backend Engineer",
  "years_experience": 5,
  "preferred_locations": ["Paris", "Remote"],
  "salary_min_expectations": 60000
}
```

**Response (200):** Updated profile object

---

#### `POST /profile/skills`
Add skill to profile.

**Request:**
```json
{
  "name": "Python",
  "level": "senior",
  "category": "technical"
}
```

**Response (201):**
```json
{
  "id": "750e8400-e29b-41d4-a716-446655440002",
  "profile_id": "650e8400-e29b-41d4-a716-446655440001",
  "name": "Python",
  "level": "senior",
  "category": "technical",
  "endorsement_count": 0,
  "created_at": "2026-08-02T10:00:00Z"
}
```

---

#### `GET /profile/skills`
List all skills for current user.

**Response (200):**
```json
[
  {
    "id": "750e8400-e29b-41d4-a716-446655440002",
    "name": "Python",
    "level": "senior",
    "category": "technical"
  },
  {
    "id": "750e8400-e29b-41d4-a716-446655440003",
    "name": "FastAPI",
    "level": "mid",
    "category": "technical"
  }
]
```

---

#### `DELETE /profile/skills/{skill_id}`
Remove skill from profile.

**Response (204):** No content

---

#### `POST /profile/experiences`
Add work experience.

**Request:**
```json
{
  "company": "TechCorp",
  "title": "Backend Engineer",
  "start_date": "2022-01-15T00:00:00Z",
  "end_date": "2026-08-02T00:00:00Z",
  "description": "Built APIs, led migrations...",
  "technologies": ["Python", "FastAPI", "PostgreSQL"],
  "impact_metrics": {"revenue_increase": "20%", "api_response_time": "50ms"}
}
```

**Response (201):** Experience object

---

#### `GET /profile/experiences`
List all work experiences.

**Response (200):**
```json
[
  {
    "id": "850e8400-...",
    "company": "TechCorp",
    "title": "Backend Engineer",
    "start_date": "2022-01-15T00:00:00Z",
    "end_date": "2026-08-02T00:00:00Z",
    "technologies": ["Python", "FastAPI", "PostgreSQL"]
  }
]
```

---

### Jobs

#### `GET /jobs/search`
Search job postings.

**Query Parameters:**
```
?skills=Python,Kubernetes
&location=Paris
&contract_type=CDI
&salary_min=50000
&experience_years_min=3
&limit=20
&offset=0
```

**Response (200):**
```json
{
  "total": 1250,
  "limit": 20,
  "offset": 0,
  "jobs": [
    {
      "id": "950e8400-...",
      "title": "Sr. Backend Engineer",
      "company": "StartupXYZ",
      "description": "Looking for...",
      "location": "Paris (Remote)",
      "employment_type": "CDI",
      "salary_min": 50000,
      "salary_max": 65000,
      "salary_currency": "EUR",
      "required_skills": ["Python", "FastAPI", "Kubernetes"],
      "required_technologies": ["Docker", "PostgreSQL"],
      "seniority_level": "senior",
      "source": "LinkedIn",
      "source_url": "https://linkedin.com/...",
      "posted_date": "2026-08-01T10:00:00Z",
      "compatibility_score": 0.82,
      "ats_keywords": ["Python", "backend", "api"]
    }
  ]
}
```

---

#### `GET /jobs/{job_id}`
Get single job details.

**Response (200):**
```json
{
  "id": "950e8400-...",
  "title": "Sr. Backend Engineer",
  "company": "StartupXYZ",
  "description": "Full job description...",
  "location": "Paris",
  "employment_type": "CDI",
  "salary_min": 50000,
  "salary_max": 65000,
  "required_skills": ["Python", "FastAPI"],
  "required_technologies": ["Docker", "PostgreSQL", "Kubernetes"],
  "seniority_level": "senior",
  "required_experience_years": 5,
  "source": "LinkedIn",
  "source_url": "https://linkedin.com/...",
  "posted_date": "2026-08-01T10:00:00Z",
  "ats_keywords": ["Python", "backend", "api", "microservices"],
  "company_metadata": {
    "size": "50-100",
    "industry": "FinTech",
    "funding_stage": "Series A"
  },
  "analysis": {
    "required_skills": ["Python", "FastAPI", "PostgreSQL"],
    "technologies": ["Docker", "Kubernetes", "AWS"],
    "responsibilities": ["Design APIs", "Optimize database", "Lead team"],
    "seniority_level": "senior",
    "estimated_salary": [50000, 65000],
    "compatibility_score": 0.82,
    "compatibility_explanation": "Strong match: 4/5 required skills, senior level matches your experience"
  }
}
```

---

### Applications

#### `POST /applications`
Create new application (draft).

**Request:**
```json
{
  "job_id": "950e8400-..."
}
```

**Response (201):**
```json
{
  "id": "a50e8400-...",
  "user_id": "550e8400-...",
  "job_id": "950e8400-...",
  "status": "DRAFT",
  "result": null,
  "created_at": "2026-08-02T10:00:00Z",
  "updated_at": "2026-08-02T10:00:00Z"
}
```

---

#### `GET /applications`
List all user applications.

**Query Parameters:**
```
?status=SENT
&limit=20
&offset=0
&sort=created_at:desc
```

**Response (200):**
```json
{
  "total": 45,
  "limit": 20,
  "offset": 0,
  "applications": [
    {
      "id": "a50e8400-...",
      "job": {
        "title": "Sr. Backend Engineer",
        "company": "StartupXYZ"
      },
      "status": "SENT",
      "result": null,
      "email_sent_at": "2026-08-02T10:00:00Z",
      "email_opened_at": "2026-08-02T11:00:00Z",
      "created_at": "2026-08-02T10:00:00Z"
    }
  ]
}
```

---

#### `GET /applications/{app_id}`
Get single application details.

**Response (200):**
```json
{
  "id": "a50e8400-...",
  "user_id": "550e8400-...",
  "job_id": "950e8400-...",
  "job": {
    "title": "Sr. Backend Engineer",
    "company": "StartupXYZ",
    "description": "..."
  },
  "status": "SENT",
  "result": null,
  "cv_version_id": "doc_001",
  "letter_version_id": "doc_002",
  "email_subject": "Application for Sr. Backend Engineer",
  "email_body": "Dear hiring team...",
  "email_sent_at": "2026-08-02T10:00:00Z",
  "email_opened_at": "2026-08-02T11:00:00Z",
  "recipient_email": "recruiter@startupxyz.com",
  "notes": "Good culture fit",
  "tags": ["priority", "follow-up"],
  "interviews": [
    {
      "id": "int_001",
      "type": "phone_screening",
      "scheduled_at": "2026-08-09T14:00:00Z",
      "completed_at": "2026-08-09T15:00:00Z",
      "interviewer_name": "John Smith",
      "feedback": "Very positive"
    }
  ],
  "created_at": "2026-08-02T10:00:00Z",
  "updated_at": "2026-08-02T12:00:00Z"
}
```

---

#### `PUT /applications/{app_id}`
Update application status.

**Request:**
```json
{
  "status": "SENT",
  "notes": "Added follow-up scheduled"
}
```

**Response (200):** Updated application object

---

#### `POST /applications/{app_id}/send`
Send application (email + track).

**Request:**
```json
{
  "cv_version_id": "doc_001",
  "letter_version_id": "doc_002",
  "email_subject": "Application for Sr. Backend Engineer",
  "email_body": "Dear hiring team...",
  "recipient_email": "recruiter@company.com"
}
```

**Response (200):**
```json
{
  "id": "a50e8400-...",
  "status": "SENT",
  "email_sent_at": "2026-08-02T10:00:00Z",
  "message": "Application sent successfully"
}
```

---

### Documents

#### `POST /documents`
Upload CV or cover letter.

**Request (multipart/form-data):**
```
file: <PDF or DOCX file>
type: "cv" or "cover_letter"
title: "CV - August 2026"
```

**Response (201):**
```json
{
  "id": "doc_001",
  "user_id": "550e8400-...",
  "type": "cv",
  "title": "CV - August 2026",
  "version": "1.0",
  "file_path": "s3://bucket/docs/doc_001.pdf",
  "file_size": "245KB",
  "mime_type": "application/pdf",
  "status": "active",
  "created_at": "2026-08-02T10:00:00Z"
}
```

---

#### `GET /documents`
List all documents for current user.

**Query Parameters:**
```
?type=cv
&status=active
```

**Response (200):**
```json
[
  {
    "id": "doc_001",
    "type": "cv",
    "title": "CV - August 2026",
    "version": "1.0",
    "status": "active",
    "created_at": "2026-08-02T10:00:00Z"
  }
]
```

---

### Analytics

#### `GET /analytics/dashboard`
Get dashboard statistics.

**Response (200):**
```json
{
  "summary": {
    "applications_sent": 45,
    "applications_opened": 15,
    "interviews_scheduled": 5,
    "offers_received": 1,
    "response_rate": 0.33,
    "interview_rate": 0.11,
    "offer_rate": 0.02
  },
  "timeline": {
    "applications_by_week": [
      {"week": "2026-08-01", "count": 10},
      {"week": "2026-08-08", "count": 15}
    ],
    "interviews_scheduled": [
      {"date": "2026-08-09", "count": 2},
      {"date": "2026-08-15", "count": 1}
    ]
  },
  "companies_most_responsive": [
    {"company": "StartupXYZ", "response_rate": 0.8},
    {"company": "TechCorp", "response_rate": 0.6}
  ]
}
```

---

## Common Response Patterns

### Success (2xx)
```json
{
  "data": { /* response object */ },
  "message": "Success message"
}
```

### Error (4xx/5xx)
```json
{
  "detail": "Error message",
  "status_code": 400,
  "type": "ValidationError",
  "errors": [
    {
      "field": "email",
      "message": "Invalid email format"
    }
  ]
}
```

---

## Rate Limiting

All endpoints are rate-limited:
- **Global:** 1,000 requests/hour per user
- **Auth:** 5 attempts/minute (per IP, for login)
- **Jobs search:** 30 searches/hour per user
- **Email send:** 100 emails/hour per user

Response includes rate-limit headers:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 2026-08-02T11:00:00Z
```

---

## Pagination

Endpoints returning lists support pagination:

**Query Parameters:**
```
?limit=20 (default: 20, max: 100)
&offset=0 (default: 0)
```

**Response:**
```json
{
  "total": 1250,
  "limit": 20,
  "offset": 0,
  "data": [...]
}
```

---

## Sorting

Some endpoints support sorting:

**Query Parameters:**
```
?sort=created_at:desc,title:asc
```

Valid directions: `asc`, `desc`

---

## Status Codes Summary

| Code | Meaning |
|------|---------|
| 200 | OK |
| 201 | Created |
| 204 | No Content |
| 400 | Bad Request (validation error) |
| 401 | Unauthorized (no/invalid token) |
| 403 | Forbidden (don't have permission) |
| 404 | Not Found |
| 409 | Conflict (duplicate email, etc.) |
| 429 | Too Many Requests (rate limited) |
| 500 | Internal Server Error |

---

## Testing

### Postman Collection

Import this in Postman:
```json
{
  "name": "CareerOS AI",
  "baseUrl": "http://localhost:8000/api/v1",
  "requests": [
    {
      "name": "Signup",
      "request": {
        "method": "POST",
        "url": "{{baseUrl}}/auth/signup",
        "body": {
          "email": "test@example.com",
          "password": "test123",
          "full_name": "Test User"
        }
      }
    },
    {
      "name": "Login",
      "request": {
        "method": "POST",
        "url": "{{baseUrl}}/auth/login",
        "body": {
          "email": "test@example.com",
          "password": "test123"
        }
      }
    }
  ]
}
```

### cURL Examples

```bash
# Signup
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "full_name": "Test User"
  }'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'

# Get Profile (with token)
curl -X GET http://localhost:8000/api/v1/profile \
  -H "Authorization: Bearer YOUR_TOKEN"

# Search Jobs
curl -X GET "http://localhost:8000/api/v1/jobs/search?skills=Python&location=Paris&limit=10"
```

---

**Status:** Phase 1 Complete
**Last Updated:** 2026-08-02
**Versioning:** Follows semantic versioning (v1, v2, etc.)

