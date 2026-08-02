"""Integration with external job boards (Indeed, LinkedIn, WTTJ, Glassdoor)"""
import httpx
import os
from typing import List, Dict, Optional
from datetime import datetime

class IndeedIntegration:
    """Integration with Indeed Jobs API"""
    
    def __init__(self):
        self.api_key = os.getenv("INDEED_API_KEY")
        self.base_url = "https://api.indeed.com/v3"
    
    async def search_jobs(self, 
                         query: str, 
                         location: str,
                         limit: int = 20) -> List[Dict]:
        """Search jobs on Indeed"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/jobs",
                    params={
                        "q": query,
                        "l": location,
                        "limit": limit,
                        "api_key": self.api_key
                    },
                    timeout=10.0
                )
                
                if response.status_code != 200:
                    return []
                
                jobs = response.json().get("data", [])
                
                # Normalize to our format
                normalized = []
                for job in jobs:
                    normalized.append({
                        "id": f"indeed_{job.get('id')}",
                        "title": job.get("jobtitle"),
                        "company": job.get("company"),
                        "location": job.get("formattedLocation"),
                        "description": job.get("snippet"),
                        "url": job.get("url"),
                        "salary": job.get("formattedLocationFull"),
                        "source": "indeed",
                        "posted_date": job.get("date"),
                    })
                
                return normalized
        
        except Exception as e:
            print(f"❌ Indeed API error: {str(e)}")
            return []

class LinkedInIntegration:
    """Integration with LinkedIn Jobs API"""
    
    def __init__(self):
        self.api_key = os.getenv("LINKEDIN_API_KEY")
        self.base_url = "https://api.linkedin.com/v2"
    
    async def search_jobs(self,
                         keywords: str,
                         location: str,
                         limit: int = 20) -> List[Dict]:
        """Search jobs on LinkedIn"""
        try:
            async with httpx.AsyncClient() as client:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                response = await client.get(
                    f"{self.base_url}/jobs/search",
                    params={
                        "keywords": keywords,
                        "location": location,
                        "limit": limit
                    },
                    headers=headers,
                    timeout=10.0
                )
                
                if response.status_code != 200:
                    return []
                
                jobs = response.json().get("elements", [])
                
                normalized = []
                for job in jobs:
                    normalized.append({
                        "id": f"linkedin_{job.get('id')}",
                        "title": job.get("title"),
                        "company": job.get("company", {}).get("name"),
                        "location": job.get("jobLocation", {}).get("city"),
                        "description": job.get("description"),
                        "url": job.get("url"),
                        "salary": job.get("salary", {}).get("salaryBudgetType"),
                        "source": "linkedin",
                        "posted_date": job.get("postedDate"),
                    })
                
                return normalized
        
        except Exception as e:
            print(f"❌ LinkedIn API error: {str(e)}")
            return []

class WTTJIntegration:
    """Integration with Welcome to the Jungle Jobs API"""
    
    def __init__(self):
        self.api_key = os.getenv("WTTJ_API_KEY")
        self.base_url = "https://api.welcomeothejungle.com/companies/jobs"
    
    async def search_jobs(self,
                         query: str,
                         location: str,
                         limit: int = 20) -> List[Dict]:
        """Search jobs on WTTJ"""
        try:
            async with httpx.AsyncClient() as client:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                response = await client.get(
                    self.base_url,
                    params={
                        "query": query,
                        "location": location,
                        "limit": limit
                    },
                    headers=headers,
                    timeout=10.0
                )
                
                if response.status_code != 200:
                    return []
                
                jobs = response.json().get("data", [])
                
                normalized = []
                for job in jobs:
                    normalized.append({
                        "id": f"wttj_{job.get('id')}",
                        "title": job.get("name"),
                        "company": job.get("company", {}).get("name"),
                        "location": job.get("location", {}).get("name"),
                        "description": job.get("description"),
                        "url": job.get("url"),
                        "salary": job.get("salary", {}).get("label"),
                        "source": "wttj",
                        "posted_date": job.get("published_at"),
                    })
                
                return normalized
        
        except Exception as e:
            print(f"❌ WTTJ API error: {str(e)}")
            return []

class GlassdoorIntegration:
    """Integration with Glassdoor Jobs API"""
    
    def __init__(self):
        self.api_key = os.getenv("GLASSDOOR_API_KEY")
        self.base_url = "https://api.glassdoor.com/api/api.htm"
    
    async def search_jobs(self,
                         keywords: str,
                         location: str,
                         limit: int = 20) -> List[Dict]:
        """Search jobs on Glassdoor"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.base_url,
                    params={
                        "v": "1",
                        "format": "json",
                        "action": "jobs-search",
                        "keyword": keywords,
                        "city": location,
                        "limit": limit,
                        "userip": "0.0.0.0",
                        "useragent": "Mozilla/5.0",
                        "key": self.api_key
                    },
                    timeout=10.0
                )
                
                if response.status_code != 200:
                    return []
                
                jobs = response.json().get("response", [])
                
                normalized = []
                for job in jobs:
                    normalized.append({
                        "id": f"glassdoor_{job.get('jobListingId')}",
                        "title": job.get("jobTitle"),
                        "company": job.get("employer", {}).get("name"),
                        "location": job.get("location"),
                        "description": job.get("jobDescription"),
                        "url": job.get("jobLinkUrl"),
                        "salary": f"${job.get('minSalary')} - ${job.get('maxSalary')}",
                        "source": "glassdoor",
                        "posted_date": job.get("postDate"),
                    })
                
                return normalized
        
        except Exception as e:
            print(f"❌ Glassdoor API error: {str(e)}")
            return []

class JobAggregatorService:
    """Aggregate jobs from multiple sources"""
    
    def __init__(self):
        self.indeed = IndeedIntegration()
        self.linkedin = LinkedInIntegration()
        self.wttj = WTTJIntegration()
        self.glassdoor = GlassdoorIntegration()
    
    async def search_all(self,
                        query: str,
                        location: str,
                        limit: int = 100) -> List[Dict]:
        """Search jobs across all sources"""
        
        import asyncio
        
        # Search in parallel
        results = await asyncio.gather(
            self.indeed.search_jobs(query, location, limit // 4),
            self.linkedin.search_jobs(query, location, limit // 4),
            self.wttj.search_jobs(query, location, limit // 4),
            self.glassdoor.search_jobs(query, location, limit // 4),
            return_exceptions=True
        )
        
        # Combine and deduplicate
        all_jobs = []
        seen_ids = set()
        
        for job_list in results:
            if isinstance(job_list, list):
                for job in job_list:
                    job_key = f"{job['company']}_{job['title']}_{job['location']}"
                    if job_key not in seen_ids:
                        all_jobs.append(job)
                        seen_ids.add(job_key)
        
        # Sort by posted date (newest first)
        all_jobs.sort(
            key=lambda x: datetime.fromisoformat(x.get('posted_date', '1970-01-01')),
            reverse=True
        )
        
        return all_jobs[:limit]

# Initialize global services
indeed = IndeedIntegration()
linkedin = LinkedInIntegration()
wttj = WTTJIntegration()
glassdoor = GlassdoorIntegration()
job_aggregator = JobAggregatorService()
