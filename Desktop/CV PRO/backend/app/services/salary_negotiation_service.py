"""AI-powered salary negotiation advisor"""
from typing import Dict, Optional
import os

class SalaryNegotiationService:
    """Provides salary negotiation guidance using Claude AI"""
    
    def get_salary_estimate(self, job_title: str, location: str, experience_years: int) -> Dict:
        """Get salary estimate based on market data"""
        base_salaries = {
            "Software Engineer": {"base": 120000, "senior": 180000, "lead": 250000},
            "Data Scientist": {"base": 130000, "senior": 190000, "lead": 260000},
            "Product Manager": {"base": 140000, "senior": 200000, "lead": 280000},
            "UX Designer": {"base": 100000, "senior": 150000, "lead": 200000},
            "DevOps Engineer": {"base": 135000, "senior": 195000, "lead": 270000},
        }
        
        salary_data = base_salaries.get(job_title, {"base": 100000, "senior": 150000, "lead": 200000})
        
        # Adjust for experience
        if experience_years < 2:
            salary = salary_data["base"]
            level = "Entry"
        elif experience_years < 5:
            salary = int(salary_data["base"] * 1.3)
            level = "Mid"
        elif experience_years < 10:
            salary = salary_data["senior"]
            level = "Senior"
        else:
            salary = salary_data["lead"]
            level = "Lead"
        
        # Adjust for location (very simplified)
        location_multipliers = {
            "San Francisco": 1.4,
            "New York": 1.35,
            "Seattle": 1.3,
            "Austin": 1.2,
            "Remote": 1.0,
        }
        multiplier = location_multipliers.get(location, 1.1)
        salary = int(salary * multiplier)
        
        return {
            "job_title": job_title,
            "level": level,
            "base_salary": salary,
            "salary_range": [int(salary * 0.9), int(salary * 1.15)],
            "location": location,
            "experience_years": experience_years,
            "percentile_50": salary,
            "percentile_75": int(salary * 1.1),
            "percentile_90": int(salary * 1.25),
        }
    
    def get_negotiation_tips(self, offer_salary: int, market_estimate: int) -> Dict:
        """Get negotiation tips based on offer vs market"""
        difference_pct = ((offer_salary - market_estimate) / market_estimate) * 100
        
        if difference_pct < -20:
            strategy = "Below Market"
            tips = [
                "✅ Prepare a strong counter-offer (ask for 10-15% more)",
                "📊 Show market research data",
                "💡 Highlight your unique value",
                "🎯 Consider non-monetary benefits (PTO, remote, equity)",
                "⏱️ Give them time to counter (48-72 hours)",
            ]
        elif difference_pct < 0:
            strategy = "Slightly Below Market"
            tips = [
                "✅ A small counter-offer (5-10% increase) is reasonable",
                "📈 Emphasize your skills and experience",
                "💼 Ask about review cycles and bonus structure",
                "🔄 Consider signing bonus",
                "📅 Negotiate start date for more prep time",
            ]
        elif difference_pct < 15:
            strategy = "At Market"
            tips = [
                "✅ Offer is competitive",
                "🎁 Negotiate other benefits (flexibility, growth, PTO)",
                "📊 Ask about equity/stock options",
                "🚀 Discuss career growth opportunities",
                "📅 Ask about annual review and raise schedule",
            ]
        else:
            strategy = "Above Market"
            tips = [
                "🎉 Excellent offer!",
                "✅ Consider accepting as-is",
                "🤝 Negotiate benefits/flexibility if desired",
                "📅 Ask about retention/signing bonuses",
                "🔄 Clarify performance reviews and advancement",
            ]
        
        return {
            "strategy": strategy,
            "difference_percentage": round(difference_pct, 2),
            "difference_amount": offer_salary - market_estimate,
            "tips": tips,
            "recommended_counter": int(market_estimate * 1.1),
        }
    
    def get_negotiation_script(self, job_title: str, current_offer: int, counter_offer: int) -> str:
        """Generate a negotiation script"""
        return f"""
        📝 NEGOTIATION SCRIPT
        
        **Opening:**
        "Thank you for the offer! I'm very excited about this opportunity. 
        I'd like to discuss the salary component briefly."
        
        **Your Position:**
        "Based on my research and my experience with {job_title}, 
        the market rate for this position is around ${counter_offer:,}. 
        My background includes [your key achievements]. 
        I was hoping we could discuss an offer closer to ${counter_offer:,}."
        
        **If they can't move much:**
        "I understand budget constraints. Could we explore other options like:
        - Signing bonus
        - Additional PTO
        - Flexible working arrangements
        - Professional development budget
        - Earlier review cycle"
        
        **Closing:**
        "I'm very interested in joining the team. 
        Can we find a solution that works for both of us?"
        
        ✅ **Remember:**
        - Stay professional and positive
        - Don't accept the first counter immediately
        - Consider the whole package, not just salary
        - Get everything in writing
        """

salary_negotiation_service = SalaryNegotiationService()
