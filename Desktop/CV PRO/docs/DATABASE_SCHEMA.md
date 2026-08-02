# CareerOS AI — Database Schema

**Status:** Version 1.0 (Ready for Migration)
**Database:** PostgreSQL 15+
**ORM:** SQLAlchemy 2.0

---

## Overview

The database schema is designed for:
- ✅ Structured data (ACID compliance)
- ✅ Complex queries (job matching, analytics)
- ✅ Scalability (proper indexing, partitioning-ready)
- ✅ GDPR (audit logging, soft deletes)

---

## Entity Diagram

```
User (1) ──→ (1) Profile
     │
     ├─→ (N) Experience
     ├─→ (N) Education
     ├─→ (N) Skill
     ├─→ (N) Document
     ├─→ (N) Application
     └─→ (N) AuditLog

Application (N) ──→ (1) JobPosting
     │
     └─→ (N) ApplicationEmail
     └─→ (N) Interview
```

---

## Tables & Columns

### 1. **users**

| Column | Type | Constraint | Notes |
|--------|------|-----------|-------|
| id | UUID | PK | Auto-generated |
| email | VARCHAR(255) | UNIQUE, INDEX | User's login email |
| hashed_password | VARCHAR(255) | NOT NULL | bcrypt hash |
| full_name | VARCHAR(255) | NULL | Displayable name |
| is_active | BOOLEAN | DEFAULT TRUE | Soft activation |
| is_verified | BOOLEAN | DEFAULT FALSE | Email verified |
| created_at | TIMESTAMP TZ | NOT NULL | Account creation |
| updated_at | TIMESTAMP TZ | NOT NULL | Last update |
| deleted_at | TIMESTAMP TZ | NULL | Soft delete flag |

**Indexes:**
```sql
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_is_active ON users(is_active);
CREATE INDEX idx_users_created_at ON users(created_at);
```

---

### 2. **profiles**

| Column | Type | Constraint | Notes |
|--------|------|-----------|-------|
| id | UUID | PK | Auto-generated |
| user_id | UUID | FK(users.id), UNIQUE | One profile per user |
| phone | VARCHAR(20) | NULL | Contact number |
| address | VARCHAR(500) | NULL | Full address |
| about_me | TEXT | NULL | Bio/introduction |
| current_title | VARCHAR(255) | NULL | Current job title |
| years_experience | INTEGER | NULL | Total years |
| preferred_contract | VARCHAR(50) | NULL | CDI, freelance, stage |
| preferred_locations | JSONB | DEFAULT '[]' | Array of locations |
| salary_min_expectations | INTEGER | NULL | Min acceptable salary |
| available_date | TIMESTAMP TZ | NULL | When available |
| visa_sponsorship_required | VARCHAR(50) | NULL | Visa needs |
| created_at | TIMESTAMP TZ | NOT NULL | Profile creation |
| updated_at | TIMESTAMP TZ | NOT NULL | Last update |

**Indexes:**
```sql
CREATE INDEX idx_profiles_user_id ON profiles(user_id);
CREATE INDEX idx_profiles_created_at ON profiles(created_at);
```

---

### 3. **experiences**

| Column | Type | Constraint | Notes |
|--------|------|-----------|-------|
| id | UUID | PK | Auto-generated |
| profile_id | UUID | FK(profiles.id) | Parent profile |
| company | VARCHAR(255) | NOT NULL | Company name |
| title | VARCHAR(255) | NOT NULL | Job title |
| start_date | TIMESTAMP TZ | NOT NULL | Start date |
| end_date | TIMESTAMP TZ | NULL | End date (NULL = current) |
| description | TEXT | NULL | Job description |
| technologies | JSONB | DEFAULT '[]' | Tech stack used |
| impact_metrics | JSONB | NULL | Quantifiable impact |
| created_at | TIMESTAMP TZ | NOT NULL | Record creation |

**Indexes:**
```sql
CREATE INDEX idx_experiences_profile_id ON experiences(profile_id);
CREATE INDEX idx_experiences_start_date ON experiences(start_date);
```

---

### 4. **education**

| Column | Type | Constraint | Notes |
|--------|------|-----------|-------|
| id | UUID | PK | Auto-generated |
| profile_id | UUID | FK(profiles.id) | Parent profile |
| institution | VARCHAR(255) | NOT NULL | School/university |
| degree | VARCHAR(255) | NOT NULL | Degree type |
| field_of_study | VARCHAR(255) | NULL | Major/specialization |
| graduation_date | TIMESTAMP TZ | NOT NULL | Graduation date |
| created_at | TIMESTAMP TZ | NOT NULL | Record creation |

**Indexes:**
```sql
CREATE INDEX idx_education_profile_id ON education(profile_id);
```

---

### 5. **skills**

| Column | Type | Constraint | Notes |
|--------|------|-----------|-------|
| id | UUID | PK | Auto-generated |
| profile_id | UUID | FK(profiles.id) | Parent profile |
| name | VARCHAR(255) | NOT NULL | Skill name (Python, etc.) |
| level | VARCHAR(50) | NULL | junior, mid, senior, expert |
| category | VARCHAR(50) | NULL | technical, soft, language |
| endorsement_count | INTEGER | DEFAULT 0 | LinkedIn-style endorsements |
| created_at | TIMESTAMP TZ | NOT NULL | Record creation |

**Indexes:**
```sql
CREATE INDEX idx_skills_profile_id ON skills(profile_id);
CREATE INDEX idx_skills_name ON skills(name);
```

---

### 6. **documents**

| Column | Type | Constraint | Notes |
|--------|------|-----------|-------|
| id | UUID | PK | Auto-generated |
| user_id | UUID | FK(users.id) | Owner |
| type | VARCHAR(50) | NOT NULL | 'cv' or 'cover_letter' |
| title | VARCHAR(255) | NOT NULL | Display name |
| version | VARCHAR(50) | NOT NULL | v1.0, v1.1, etc. |
| file_path | VARCHAR(500) | NOT NULL | S3 URI or local path |
| file_size | VARCHAR(50) | NULL | File size (MB) |
| mime_type | VARCHAR(100) | NULL | application/pdf, etc. |
| status | VARCHAR(50) | DEFAULT 'active' | active, archived, deleted |
| metadata | VARCHAR(1000) | NULL | Extra JSON data |
| created_at | TIMESTAMP TZ | NOT NULL | Upload time |
| updated_at | TIMESTAMP TZ | NOT NULL | Last update |

**Indexes:**
```sql
CREATE INDEX idx_documents_user_id ON documents(user_id);
CREATE INDEX idx_documents_type ON documents(type);
CREATE INDEX idx_documents_status ON documents(status);
```

---

### 7. **job_postings**

| Column | Type | Constraint | Notes |
|--------|------|-----------|-------|
| id | UUID | PK | Auto-generated |
| external_id | VARCHAR(500) | NULL | Source ID (LinkedIn, Indeed) |
| title | VARCHAR(500) | NOT NULL | Job title |
| company | VARCHAR(255) | NOT NULL | Company name |
| description | TEXT | NOT NULL | Full job description |
| required_skills | JSONB | DEFAULT '[]' | Extracted skills |
| required_technologies | JSONB | DEFAULT '[]' | Tech stack |
| required_experience_years | INTEGER | NULL | Years experience needed |
| seniority_level | VARCHAR(50) | NULL | junior, mid, senior, lead |
| location | VARCHAR(255) | NOT NULL | Job location |
| employment_type | VARCHAR(50) | NOT NULL | CDI, freelance, stage |
| salary_min | INTEGER | NULL | Min salary (EUR) |
| salary_max | INTEGER | NULL | Max salary (EUR) |
| salary_currency | VARCHAR(10) | DEFAULT 'EUR' | Currency code |
| source | VARCHAR(50) | NOT NULL | LinkedIn, Indeed, WTTJ |
| source_url | VARCHAR(1000) | NULL | Direct link |
| posted_date | TIMESTAMP TZ | NOT NULL | Publication date |
| expires_date | TIMESTAMP TZ | NULL | Expiration date |
| scraped_at | TIMESTAMP TZ | NOT NULL | When we scraped it |
| updated_at | TIMESTAMP TZ | NOT NULL | Last updated |
| ats_keywords | JSONB | DEFAULT '[]' | ATS keyword list |
| company_metadata | JSONB | NULL | Company info JSON |

**Indexes:**
```sql
CREATE INDEX idx_job_postings_company ON job_postings(company);
CREATE INDEX idx_job_postings_source ON job_postings(source);
CREATE INDEX idx_job_postings_posted_date ON job_postings(posted_date);
CREATE INDEX idx_job_postings_external_id ON job_postings(external_id);

-- Full-text search indexes (French)
CREATE INDEX idx_job_postings_title_gin ON job_postings 
  USING GIN(to_tsvector('french', title));
CREATE INDEX idx_job_postings_description_gin ON job_postings 
  USING GIN(to_tsvector('french', description));
```

---

### 8. **applications**

| Column | Type | Constraint | Notes |
|--------|------|-----------|-------|
| id | UUID | PK | Auto-generated |
| user_id | UUID | FK(users.id) | Applicant |
| job_id | UUID | FK(job_postings.id), NULLABLE | Job applied to |
| status | VARCHAR(50) | DEFAULT 'DRAFT' | Workflow state |
| result | VARCHAR(50) | NULL | pending, rejected, offer, accepted |
| cv_version_id | UUID | FK(documents.id), NULLABLE | CV used |
| letter_version_id | UUID | FK(documents.id), NULLABLE | Letter used |
| email_body | TEXT | NULL | Email content sent |
| email_subject | VARCHAR(500) | NULL | Email subject |
| email_sent_at | TIMESTAMP TZ | NULL | When sent |
| email_opened_at | TIMESTAMP TZ | NULL | Email open tracking |
| recipient_email | VARCHAR(255) | NULL | Recruiter's email |
| notes | TEXT | NULL | Internal notes |
| interviews | JSONB | DEFAULT '[]' | Interview records |
| feedback | JSONB | NULL | Interview feedback |
| tags | JSONB | DEFAULT '[]' | User-defined tags |
| created_at | TIMESTAMP TZ | NOT NULL | Application creation |
| updated_at | TIMESTAMP TZ | NOT NULL | Last update |

**Statuses:**
```
DRAFT → READY → SENT → VIEWED → [REJECTED | INTERVIEWED | OFFER | ACCEPTED]
```

**Indexes:**
```sql
CREATE INDEX idx_applications_user_id ON applications(user_id);
CREATE INDEX idx_applications_status ON applications(status);
CREATE INDEX idx_applications_created_at ON applications(created_at DESC);
CREATE INDEX idx_applications_job_id ON applications(job_id);
```

---

### 9. **application_emails**

| Column | Type | Constraint | Notes |
|--------|------|-----------|-------|
| id | UUID | PK | Auto-generated |
| application_id | UUID | FK(applications.id) | Parent application |
| email_type | VARCHAR(50) | NOT NULL | initial, followup_1, followup_2 |
| email_sent_at | TIMESTAMP TZ | NOT NULL | Send timestamp |
| email_opened_at | TIMESTAMP TZ | NULL | Email open tracking pixel |
| recipient_email | VARCHAR(255) | NOT NULL | Recipient's email |
| subject | VARCHAR(500) | NOT NULL | Email subject |
| body | TEXT | NOT NULL | Email body |

**Indexes:**
```sql
CREATE INDEX idx_application_emails_application_id ON application_emails(application_id);
CREATE INDEX idx_application_emails_email_type ON application_emails(email_type);
CREATE INDEX idx_application_emails_sent_at ON application_emails(email_sent_at DESC);
```

---

### 10. **interviews**

| Column | Type | Constraint | Notes |
|--------|------|-----------|-------|
| id | UUID | PK | Auto-generated |
| application_id | UUID | FK(applications.id) | Parent application |
| type | VARCHAR(50) | NOT NULL | phone_screening, technical, round_1 |
| scheduled_at | TIMESTAMP TZ | NOT NULL | Interview datetime |
| completed_at | TIMESTAMP TZ | NULL | When completed |
| interviewer_name | VARCHAR(255) | NULL | Interviewer's name |
| interviewer_email | VARCHAR(255) | NULL | Interviewer's email |
| interviewer_title | VARCHAR(255) | NULL | Job title |
| feedback | TEXT | NULL | Interview notes |
| notes | TEXT | NULL | Your notes |
| rating | VARCHAR(50) | NULL | positive, neutral, negative |
| created_at | TIMESTAMP TZ | NOT NULL | Record creation |

**Indexes:**
```sql
CREATE INDEX idx_interviews_application_id ON interviews(application_id);
CREATE INDEX idx_interviews_type ON interviews(type);
CREATE INDEX idx_interviews_scheduled_at ON interviews(scheduled_at);
```

---

### 11. **audit_log** (GDPR Requirement)

| Column | Type | Constraint | Notes |
|--------|------|-----------|-------|
| id | UUID | PK | Auto-generated |
| user_id | UUID | FK(users.id), NULLABLE | Who made the change |
| entity_type | VARCHAR(100) | NOT NULL | User, Profile, Application, etc. |
| entity_id | VARCHAR(500) | NOT NULL | ID of changed entity |
| action | VARCHAR(50) | NOT NULL | create, read, update, delete |
| changes | JSONB | NULL | Before/after values |
| ip_address | VARCHAR(45) | NULL | IPv4 or IPv6 |
| user_agent | VARCHAR(500) | NULL | Browser info |
| created_at | TIMESTAMP TZ | NOT NULL, INDEX | Timestamp |

**Indexes:**
```sql
CREATE INDEX idx_audit_log_user_id ON audit_log(user_id);
CREATE INDEX idx_audit_log_entity ON audit_log(entity_type, entity_id);
CREATE INDEX idx_audit_log_created_at ON audit_log(created_at DESC);
```

---

## Constraints & Relationships

```sql
-- Foreign Keys
ALTER TABLE profiles ADD CONSTRAINT fk_profiles_user_id 
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE experiences ADD CONSTRAINT fk_experiences_profile_id 
  FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE;

ALTER TABLE education ADD CONSTRAINT fk_education_profile_id 
  FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE;

ALTER TABLE skills ADD CONSTRAINT fk_skills_profile_id 
  FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE;

ALTER TABLE documents ADD CONSTRAINT fk_documents_user_id 
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE applications ADD CONSTRAINT fk_applications_user_id 
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE applications ADD CONSTRAINT fk_applications_job_id 
  FOREIGN KEY (job_id) REFERENCES job_postings(id) ON DELETE SET NULL;

ALTER TABLE application_emails ADD CONSTRAINT fk_application_emails_app_id 
  FOREIGN KEY (application_id) REFERENCES applications(id) ON DELETE CASCADE;

ALTER TABLE interviews ADD CONSTRAINT fk_interviews_app_id 
  FOREIGN KEY (application_id) REFERENCES applications(id) ON DELETE CASCADE;

ALTER TABLE audit_log ADD CONSTRAINT fk_audit_log_user_id 
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL;

-- Unique Constraints
ALTER TABLE users ADD CONSTRAINT uq_users_email UNIQUE(email);
ALTER TABLE profiles ADD CONSTRAINT uq_profiles_user_id UNIQUE(user_id);
```

---

## Partitioning Strategy (for scale)

As the database grows, consider partitioning:

```sql
-- Partition job_postings by month (if > 100M rows)
ALTER TABLE job_postings PARTITION BY RANGE (DATE_TRUNC('month', posted_date));

-- Partition applications by year
ALTER TABLE applications PARTITION BY RANGE (EXTRACT(YEAR FROM created_at));

-- Partition audit_log by month (grows fast!)
ALTER TABLE audit_log PARTITION BY RANGE (DATE_TRUNC('month', created_at));
```

---

## Migration Strategy

### Phase 1 (Initial Setup)
1. Create all tables + indexes
2. Add foreign keys + constraints
3. Create audit log triggers

### Phase 2 (Optimization - if needed)
1. Add partitioning (after reaching scale)
2. Archive old audit logs (GDPR: retention policy)
3. Add materialized views for analytics

---

## GDPR Considerations

✅ **Data Minimization** : Only required fields
✅ **Audit Logging** : All changes tracked in `audit_log`
✅ **Soft Delete** : `deleted_at` flag for recovery
✅ **Data Export** : Easy query to extract all user data
✅ **Data Retention** : Audit log entries should be purged after 12 months per GDPR

```sql
-- GDPR: Export user data
SELECT * FROM users WHERE id = 'user_id';
SELECT * FROM profiles WHERE user_id = 'user_id';
SELECT * FROM experiences WHERE profile_id IN (SELECT id FROM profiles WHERE user_id = 'user_id');
-- ... etc

-- GDPR: Delete user (cascade)
DELETE FROM users WHERE id = 'user_id'; -- Cascades to all related data

-- GDPR: Purge old audit logs (after 12 months)
DELETE FROM audit_log WHERE created_at < NOW() - INTERVAL '12 months';
```

---

## Backup & Recovery

```bash
# Backup entire database
pg_dump postgresql://user:pass@host:5432/careeeros_ai > backup.sql

# Backup specific table
pg_dump -t applications postgresql://user:pass@host:5432/careeeros_ai > apps.sql

# Restore from backup
psql postgresql://user:pass@host:5432/careeeros_ai < backup.sql
```

---

## Performance Metrics to Monitor

- [ ] Query response time (< 100ms for normal queries)
- [ ] Index hit ratio (> 99%)
- [ ] Table bloat (< 10%)
- [ ] Connection pool usage (< 80%)
- [ ] Disk space growth (< 10GB/month initially)

---

**Version:** 1.0
**Status:** Ready for Implementation
**Last Updated:** 2026-08-02
