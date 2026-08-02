# 🔗 Job Board Integration Setup

Connect CareerOS AI to real job sources: Indeed, LinkedIn, WTTJ, Glassdoor

---

## Setup Instructions

### 1. Indeed API

**Get API Key:**
1. Go to https://opensource.indeedeng.io/api-documentation/
2. Click "Get Started"
3. Register for Indeed API
4. Generate API key
5. Add to `.env`:

```bash
INDEED_API_KEY=your_indeed_api_key_here
```

**Test:**
```bash
curl "http://localhost:8000/api/jobs/search?q=Software%20Engineer&location=San%20Francisco&source=indeed"
```

---

### 2. LinkedIn API

**Get API Key:**
1. Go to https://www.linkedin.com/developers/
2. Create app in "My apps"
3. Request "Jobs" product
4. Wait for approval (1-2 days)
5. Generate access token
6. Add to `.env`:

```bash
LINKEDIN_API_KEY=your_linkedin_access_token_here
```

**Test:**
```bash
curl "http://localhost:8000/api/jobs/search?q=Software%20Engineer&location=San%20Francisco&source=linkedin"
```

---

### 3. Welcome to the Jungle (WTTJ)

**Get API Key:**
1. Go to https://developers.welcomeothejungle.com/
2. Sign up for developer account
3. Create app
4. Generate API key
5. Add to `.env`:

```bash
WTTJ_API_KEY=your_wttj_api_key_here
```

**Test:**
```bash
curl "http://localhost:8000/api/jobs/search?q=Software%20Engineer&location=Paris&source=wttj"
```

---

### 4. Glassdoor API

**Get API Key:**
1. Go to https://www.glassdoor.com/api/
2. Request API access
3. Fill out API request form
4. Get approval
5. Add to `.env`:

```bash
GLASSDOOR_API_KEY=your_glassdoor_api_key_here
```

**Test:**
```bash
curl "http://localhost:8000/api/jobs/search?q=Software%20Engineer&location=New%20York&source=glassdoor"
```

---

## Update .env File

```bash
# backend/.env

# Job Board APIs
INDEED_API_KEY=xxxxx
LINKEDIN_API_KEY=xxxxx
WTTJ_API_KEY=xxxxx
GLASSDOOR_API_KEY=xxxxx

# Other existing configs...
DATABASE_URL=sqlite:///./careerosai.db
SECRET_KEY=your_secret_key
JWT_ALGORITHM=HS256
```

---

## API Endpoints

### Search Across All Sources
```bash
GET /api/jobs/search?q=Software%20Engineer&location=San%20Francisco&source=all&limit=20
```

Response:
```json
{
  "query": "Software Engineer",
  "location": "San Francisco",
  "source": "all",
  "count": 20,
  "jobs": [
    {
      "id": "indeed_12345",
      "title": "Senior Software Engineer",
      "company": "Google",
      "location": "San Francisco, CA",
      "description": "...",
      "url": "https://indeed.com/...",
      "salary": "$150,000 - $200,000",
      "source": "indeed",
      "posted_date": "2024-01-08"
    },
    // ... more jobs
  ]
}
```

### Get Trending Jobs
```bash
GET /api/jobs/trending
```

### Get Jobs by Source
```bash
GET /api/jobs/by-source/indeed?query=Python%20Developer&location=Remote&limit=20
GET /api/jobs/by-source/linkedin?query=Data%20Scientist&location=New%20York&limit=20
GET /api/jobs/by-source/wttj?query=Product%20Manager&location=Paris&limit=20
```

### Get Similar Jobs
```bash
GET /api/jobs/similar?job_title=Senior%20Engineer&company=Google&location=SF
```

### Get Personalized Recommendations
```bash
GET /api/jobs/recommendations/user_123
```

---

## Frontend Integration

Update frontend API calls:

```typescript
// frontend/lib/api.ts

export async function searchJobs(query: string, location: string, source: string = 'all') {
  const response = await fetch(
    `/api/jobs/search?q=${query}&location=${location}&source=${source}`,
    {
      headers: { 'Authorization': `Bearer ${token}` }
    }
  );
  return response.json();
}

export async function getTrendingJobs() {
  const response = await fetch('/api/jobs/trending');
  return response.json();
}

export async function getJobRecommendations(userId: string) {
  const response = await fetch(`/api/jobs/recommendations/${userId}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return response.json();
}
```

---

## Feature: Real-Time Job Sync

Add periodic sync of jobs to database:

```python
# backend/app/services/job_sync_service.py
from celery import shared_task
from datetime import datetime, timedelta

@shared_task
def sync_jobs_daily():
    """Daily job sync from all sources"""
    jobs = await job_aggregator.search_all("*", "Remote", 100)
    
    for job in jobs:
        # Store in database
        db_job = Job(
            id=job['id'],
            title=job['title'],
            company=job['company'],
            location=job['location'],
            description=job['description'],
            url=job['url'],
            salary=job['salary'],
            source=job['source'],
            posted_date=job['posted_date'],
            synced_at=datetime.now()
        )
        db.add(db_job)
    
    db.commit()
    return f"Synced {len(jobs)} jobs"

# Schedule daily at 2 AM
from celery.schedules import crontab
app.conf.beat_schedule = {
    'sync-jobs-daily': {
        'task': 'app.services.job_sync_service.sync_jobs_daily',
        'schedule': crontab(hour=2, minute=0),
    },
}
```

---

## Cost Summary

| Service | Free Tier | Paid Tier | Features |
|---------|-----------|-----------|----------|
| Indeed | 1,000 req/month | $200+/month | Jobs search, company data |
| LinkedIn | Limited | $500+/month | Jobs, profiles, company |
| WTTJ | Free for 30 days | €99+/month | Jobs, companies, culture |
| Glassdoor | Free limited | Custom | Jobs, reviews, salaries |

**Recommendation:** Start with free tiers, scale to paid as needed.

---

## Troubleshooting

### API Key Not Working
- Check key is copied correctly
- Verify API is enabled in provider dashboard
- Check rate limits haven't been exceeded
- Try test request on provider's documentation

### No Results Returned
- Verify search query spelling
- Try "Remote" for location if specific city fails
- Check API documentation for location format
- Increase timeout if network is slow

### Rate Limiting
- Implement exponential backoff retry logic
- Cache results for 1 hour
- Use batch endpoints when available
- Consider upgrade to higher tier

---

## Next Steps

1. [ ] Get API keys from all 4 providers
2. [ ] Add to `.env` file
3. [ ] Test each endpoint locally
4. [ ] Deploy to production
5. [ ] Monitor API usage
6. [ ] Setup job sync task
7. [ ] Monitor search results quality

---

**You now have access to real jobs from 4 major job boards!** 🎉

