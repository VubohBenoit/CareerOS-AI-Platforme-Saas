"""Jobs API with real integrations to external job boards"""
from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.job_board_integration import job_aggregator
from typing import List
import asyncio

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

@router.get("/search")
async def search_jobs(
    q: str = Query(..., description="Search query (e.g., 'Software Engineer')"),
    location: str = Query(..., description="Location (e.g., 'San Francisco')"),
    source: str = Query(
        "all",
        description="Job source: all, indeed, linkedin, wttj, glassdoor"
    ),
    limit: int = Query(20, description="Number of results"),
    db: Session = Depends(get_db)
):
    """Search jobs across multiple job boards
    
    Sources:
    - indeed: Indeed.com
    - linkedin: LinkedIn Jobs
    - wttj: Welcome to the Jungle
    - glassdoor: Glassdoor
    - all: All sources combined (deduplicated)
    """
    
    if source == "all":
        # Get from all sources
        jobs = await job_aggregator.search_all(q, location, limit)
    elif source == "indeed":
        jobs = await job_aggregator.indeed.search_jobs(q, location, limit)
    elif source == "linkedin":
        jobs = await job_aggregator.linkedin.search_jobs(q, location, limit)
    elif source == "wttj":
        jobs = await job_aggregator.wttj.search_jobs(q, location, limit)
    elif source == "glassdoor":
        jobs = await job_aggregator.glassdoor.search_jobs(q, location, limit)
    else:
        return {"error": "Invalid source"}
    
    return {
        "query": q,
        "location": location,
        "source": source,
        "count": len(jobs),
        "jobs": jobs
    }

@router.get("/trending")
async def get_trending_jobs():
    """Get trending jobs across all sources"""
    trending_queries = [
        "Software Engineer",
        "Product Manager",
        "Data Scientist",
        "DevOps Engineer",
        "UX Designer"
    ]
    
    all_trending = []
    
    for query in trending_queries:
        jobs = await job_aggregator.search_all(query, "Remote", limit=5)
        all_trending.extend(jobs)
    
    return {
        "trending": all_trending[:30],
        "count": len(all_trending)
    }

@router.get("/by-source/{source}")
async def get_jobs_by_source(
    source: str = Query(...),
    query: str = Query("Software Engineer"),
    location: str = Query("Remote"),
    limit: int = Query(20)
):
    """Get jobs from specific source"""
    
    if source == "indeed":
        jobs = await job_aggregator.indeed.search_jobs(query, location, limit)
    elif source == "linkedin":
        jobs = await job_aggregator.linkedin.search_jobs(query, location, limit)
    elif source == "wttj":
        jobs = await job_aggregator.wttj.search_jobs(query, location, limit)
    elif source == "glassdoor":
        jobs = await job_aggregator.glassdoor.search_jobs(query, location, limit)
    else:
        return {"error": "Invalid source"}
    
    return {
        "source": source,
        "query": query,
        "location": location,
        "count": len(jobs),
        "jobs": jobs
    }

@router.get("/similar")
async def get_similar_jobs(
    job_title: str = Query(...),
    company: str = Query(...),
    location: str = Query(...),
    limit: int = Query(10)
):
    """Find similar jobs on all boards"""
    
    jobs = await job_aggregator.search_all(job_title, location, limit)
    
    return {
        "similar_to": f"{job_title} at {company}",
        "location": location,
        "count": len(jobs),
        "jobs": jobs
    }

@router.get("/recommendations/{user_id}")
async def get_job_recommendations(
    user_id: str,
    limit: int = Query(20),
    db: Session = Depends(get_db)
):
    """Get personalized job recommendations based on user profile"""
    
    # Get user profile
    from app.models.user import User
    from app.models.profile import UserProfile
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"error": "User not found"}
    
    # Get user skills
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    skills = profile.skills if profile else []
    
    # Search for jobs matching user skills
    recommended_jobs = []
    
    for skill in skills[:3]:  # Top 3 skills
        jobs = await job_aggregator.search_all(skill, "Remote", limit // 3)
        recommended_jobs.extend(jobs)
    
    return {
        "user_id": user_id,
        "recommendations": recommended_jobs[:limit],
        "count": len(recommended_jobs),
        "based_on_skills": skills
    }
