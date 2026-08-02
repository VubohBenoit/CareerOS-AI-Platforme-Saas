"""Referral system for job opportunities"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import uuid

class ReferralService:
    """Manage job referrals and referral rewards"""
    
    def create_referral_link(self, user_id: str, job_id: str) -> Dict:
        """Create a shareable referral link for a job"""
        referral_code = str(uuid.uuid4())[:8].upper()
        
        return {
            "referral_code": referral_code,
            "referral_link": f"https://careerosai.com/job/{job_id}?ref={referral_code}",
            "share_urls": {
                "linkedin": f"https://www.linkedin.com/sharing/share-offsite/?url=https://careerosai.com/job/{job_id}?ref={referral_code}",
                "twitter": f"https://twitter.com/intent/tweet?text=Check%20this%20job&url=https://careerosai.com/job/{job_id}?ref={referral_code}",
                "email": f"mailto:?subject=Job Opportunity&body=Check this job: https://careerosai.com/job/{job_id}?ref={referral_code}",
            },
            "expires_at": (datetime.now() + timedelta(days=90)).isoformat(),
        }
    
    def track_referral(self, referral_code: str, referred_user_id: str) -> Dict:
        """Track when someone uses a referral link"""
        return {
            "referral_code": referral_code,
            "referred_user_id": referred_user_id,
            "tracked_at": datetime.now().isoformat(),
            "status": "pending",
        }
    
    def get_referral_stats(self, user_id: str) -> Dict:
        """Get user's referral statistics and rewards"""
        return {
            "user_id": user_id,
            "total_referrals": 12,
            "successful_placements": 3,
            "pending_referrals": 5,
            "rewards_earned": 450,  # Points or credits
            "referral_tier": "Silver",
            "next_tier_at": 500,
            "recent_referrals": [
                {
                    "id": "ref_001",
                    "job_title": "Senior Software Engineer",
                    "company": "TechCorp",
                    "referred_user": "john@example.com",
                    "status": "Applied",
                    "created_at": "2024-01-15",
                    "reward_points": 50,
                }
            ],
        }
    
    def apply_referral_bonus(self, user_id: str, amount: int) -> Dict:
        """Apply referral bonus to user"""
        return {
            "user_id": user_id,
            "bonus_type": "referral",
            "amount": amount,
            "currency": "USD" if amount > 50 else "points",
            "applied_at": datetime.now().isoformat(),
            "message": f"Congratulations! You earned ${amount} for referring a successful hire!" if amount > 50 else f"You earned {amount} reward points!",
        }
    
    def get_referral_rewards_catalog(self) -> Dict:
        """Get available rewards for referrals"""
        return {
            "cash_rewards": [
                {"referrals": 3, "amount": 50, "description": "Bronze tier - $50 bonus"},
                {"referrals": 5, "amount": 150, "description": "Silver tier - $150 bonus"},
                {"referrals": 10, "amount": 500, "description": "Gold tier - $500 bonus"},
                {"referrals": 20, "amount": 1500, "description": "Platinum tier - $1,500 bonus"},
            ],
            "exclusive_benefits": [
                {"tier": "Silver", "benefit": "Priority job matching"},
                {"tier": "Gold", "benefit": "1-on-1 career coach session"},
                {"tier": "Platinum", "benefit": "VIP support + career planning consultation"},
            ],
        }

referral_service = ReferralService()
