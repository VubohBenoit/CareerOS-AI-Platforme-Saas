# Security & Compliance Checklist

## Pre-Launch Security Review

### Authentication
- [ ] Passwords hashed with bcrypt (cost factor 12+)
- [ ] JWT tokens use HS256 or RS256
- [ ] Access tokens expire in 15-30 minutes
- [ ] Refresh tokens expire in 30 days
- [ ] HTTPS enforced everywhere
- [ ] Secure cookie flags set (HttpOnly, Secure, SameSite)
- [ ] No credentials in logs/error messages

### API Security
- [ ] Rate limiting enabled (60 req/min per user)
- [ ] Input validation (Pydantic schemas)
- [ ] SQL injection prevention (ORM + parameterized queries)
- [ ] CSRF protection enabled
- [ ] CORS origins whitelisted
- [ ] API versioning (/api/v1/)
- [ ] Expired/invalid tokens rejected
- [ ] Authorization checks on all endpoints

### Database Security
- [ ] PostgreSQL using strong passwords
- [ ] Database connections use SSL/TLS
- [ ] Backups encrypted
- [ ] Audit logging enabled (audit_log table)
- [ ] Foreign key constraints enforced
- [ ] Indexes optimized for query performance
- [ ] Regular backups tested (restore works)

### Data Protection (GDPR)
- [ ] Privacy policy updated
- [ ] Terms of Service reviewed
- [ ] User consent for data processing
- [ ] Data processing agreement (if EU users)
- [ ] Audit log retention policy (12 months)
- [ ] Data export functionality works
- [ ] Deletion cascade tested (deleting user deletes all data)
- [ ] PII encrypted at rest (optional: AES-256)
- [ ] No SSN/government IDs stored

### Infrastructure Security
- [ ] Firewall rules set (restrict to needed ports)
- [ ] SSH key-only access (no passwords)
- [ ] Secrets in environment variables (not in code)
- [ ] .env.example committed, but not .env
- [ ] AWS IAM policies least-privilege
- [ ] S3 buckets private by default
- [ ] Security groups restrict inbound traffic
- [ ] Cloudflare/WAF enabled (blocks common attacks)

### Monitoring & Logging
- [ ] Error monitoring (Sentry or DataDog)
- [ ] Structured logging (JSON format)
- [ ] Log aggregation (ELK, CloudWatch)
- [ ] Alerts for security events (failed auth, unusual activity)
- [ ] Regular log review process
- [ ] PII not logged (emails, passwords, tokens)

### Testing
- [ ] Security-focused unit tests
- [ ] SQL injection tests
- [ ] XSS vulnerability tests
- [ ] CSRF token tests
- [ ] Rate limit tests
- [ ] Authentication/authorization tests
- [ ] Dependency scanning for known vulnerabilities

### Third-Party Services
- [ ] OpenAI API key never exposed
- [ ] Anthropic API key never exposed
- [ ] SendGrid API key in secrets
- [ ] AWS credentials never in code
- [ ] LinkedIn API (if used) authenticated properly

### Code Quality
- [ ] No hardcoded secrets
- [ ] No debug mode in production
- [ ] Error messages generic (no SQL leaks)
- [ ] Dependencies up-to-date
- [ ] Code review process enforced (PRs)
- [ ] OWASP Top 10 addressed

### Deployment
- [ ] Secrets manager used (AWS Secrets, HashiCorp Vault)
- [ ] HTTPS certificate valid & renewed
- [ ] Database credentials rotated
- [ ] Backup disaster recovery tested
- [ ] Rollback plan documented
- [ ] Monitoring alerting on errors > 5%

### Regular Maintenance
- [ ] Patch schedule for OS/dependencies
- [ ] Monthly security audits
- [ ] Quarterly penetration testing (by 3rd party)
- [ ] Annual SOC 2 audit (if B2B)
- [ ] Security incident response plan

---

## GDPR-Specific Checklist

### User Rights
- [ ] Right to Access : `/export-data` endpoint works
- [ ] Right to Erasure : `/delete-account` cascades delete
- [ ] Right to Rectification : Users can edit profile
- [ ] Right to Data Portability : Export in JSON format
- [ ] Right to Restrict : Can pause account

### Data Handling
- [ ] Minimal data collection (only needed fields)
- [ ] Explicit consent for each processing purpose
- [ ] 3rd party data sharing disclosed
- [ ] Data retention policy (delete after 1 year if inactive)
- [ ] Breach notification plan (72h to notify)

### Documentation
- [ ] Privacy Policy (current, >50% users read it)
- [ ] Terms of Service (covers liability)
- [ ] Data Processing Agreement (for EU users)
- [ ] Cookie Policy (if cookies used)
- [ ] DPA signed with LLM providers (OpenAI, Anthropic)

### Incident Response
- [ ] Contact info for data protection officer
- [ ] Incident response plan (who, what, when)
- [ ] 72-hour breach notification process
- [ ] User communication templates

---

## Compliance by Region

### EU (GDPR)
- [ ] GDPR checklist above ✓
- [ ] Host data in EU (AWS eu-west-1 or similar)
- [ ] Respect right to be forgotten
- [ ] DPA with all processors

### US (State Laws)
- [ ] CCPA (California) compliant
- [ ] COPPA (children) not targeted
- [ ] State privacy laws reviewed

### Other
- [ ] Terms of Service ToS compliant with platform ToS (LinkedIn, Indeed)
- [ ] No automated scraping (respect robots.txt)
- [ ] Fair use of job board APIs

---

## Sign-Off

- [ ] Security Lead reviewed this checklist
- [ ] All items completed
- [ ] Signed off for launch

**Date:** ___________
**Reviewer:** ___________

---

## Post-Launch Monitoring

After launch, check:
- [ ] No security alerts in first week
- [ ] Error rates < 1%
- [ ] Response times < 500ms
- [ ] No unusual traffic patterns
- [ ] User feedback positive
