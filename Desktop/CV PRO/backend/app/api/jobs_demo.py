"""Demo jobs endpoint - Works without API keys"""
from fastapi import APIRouter, Query
from typing import List

router = APIRouter(prefix="/api/jobs-demo", tags=["jobs-demo"])

# Demo jobs database
DEMO_JOBS = [
    {
        "id": "demo_1",
        "title": "Senior Software Engineer",
        "company": "Google",
        "location": "San Francisco, CA",
        "description": "We're looking for an experienced Senior Software Engineer to join our team.",
        "url": "https://careers.google.com",
        "salary": "$180,000 - $240,000",
        "source": "demo",
        "posted_date": "2024-01-08"
    },
    {
        "id": "demo_2",
        "title": "Full Stack Developer",
        "company": "Microsoft",
        "location": "Remote",
        "description": "Join Microsoft as a Full Stack Developer building cloud applications.",
        "url": "https://careers.microsoft.com",
        "salary": "$150,000 - $200,000",
        "source": "demo",
        "posted_date": "2024-01-07"
    },
    {
        "id": "demo_3",
        "title": "Data Scientist",
        "company": "Amazon",
        "location": "Seattle, WA",
        "description": "Work on ML models and big data at Amazon Web Services.",
        "url": "https://amazon.jobs",
        "salary": "$160,000 - $220,000",
        "source": "demo",
        "posted_date": "2024-01-06"
    },
    {
        "id": "demo_4",
        "title": "Product Manager",
        "company": "Meta",
        "location": "Menlo Park, CA",
        "description": "Lead product strategy for Meta's next billion users.",
        "url": "https://metacareers.com",
        "salary": "$170,000 - $230,000",
        "source": "demo",
        "posted_date": "2024-01-05"
    },
    {
        "id": "demo_5",
        "title": "DevOps Engineer",
        "company": "Netflix",
        "location": "Los Gatos, CA",
        "description": "Build and maintain infrastructure at Netflix scale.",
        "url": "https://netflix.com/jobs",
        "salary": "$155,000 - $210,000",
        "source": "demo",
        "posted_date": "2024-01-04"
    },
    {
        "id": "demo_6",
        "title": "Frontend Engineer",
        "company": "Airbnb",
        "location": "San Francisco, CA",
        "description": "Create beautiful user experiences for Airbnb.",
        "url": "https://airbnb.com/careers",
        "salary": "$145,000 - $195,000",
        "source": "demo",
        "posted_date": "2024-01-03"
    }
]

@router.get("/search")
async def search_demo_jobs(
    q: str = Query(..., description="Search query"),
    location: str = Query("Remote", description="Job location")
):
    """Search demo jobs (no API keys needed)"""
    
    query_lower = q.lower()
    location_lower = location.lower()
    
    # Filter jobs
    results = [
        job for job in DEMO_JOBS
        if (query_lower in job["title"].lower() or 
            query_lower in job["description"].lower())
        and (location_lower == "remote" or location_lower in job["location"].lower() or location_lower == "all")
    ]
    
    # If no exact match, return all
    if not results:
        results = DEMO_JOBS
    
    return {
        "query": q,
        "location": location,
        "count": len(results),
        "jobs": results,
        "message": "✅ Demo jobs loaded (add API keys for real job boards)"
    }

@router.get("/trending")
async def get_trending_demo_jobs():
    """Get trending demo jobs"""
    return {
        "trending": DEMO_JOBS[:3],
        "count": 3,
        "message": "✅ Here are trending jobs"
    }

@router.get("/all")
async def get_all_demo_jobs():
    """Get all demo jobs"""
    return {
        "jobs": DEMO_JOBS,
        "count": len(DEMO_JOBS),
        "message": f"✅ Showing all {len(DEMO_JOBS)} demo jobs"
    }
