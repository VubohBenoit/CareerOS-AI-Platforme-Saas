"""AI-powered interview preparation service"""
from typing import List, Dict, Optional
import random

class InterviewPrepService:
    """Generate mock interview questions and track performance"""
    
    BEHAVIORAL_QUESTIONS = [
        "Tell me about a time you overcame a significant challenge at work.",
        "Describe a situation where you had to work with a difficult team member.",
        "Give an example of when you showed leadership.",
        "Tell me about a project you're proud of and your role in it.",
        "Describe a time you failed and what you learned.",
        "How do you prioritize when you have multiple deadlines?",
        "Tell me about a time you had to learn something quickly.",
        "Describe your proudest professional achievement.",
    ]
    
    TECHNICAL_QUESTIONS = {
        "Backend": [
            "Explain the difference between SQL and NoSQL databases.",
            "What is the CAP theorem?",
            "How would you design a scalable cache system?",
            "Explain RESTful API design principles.",
            "What are microservices and their advantages?",
        ],
        "Frontend": [
            "Explain the difference between var, let, and const in JavaScript.",
            "What is the virtual DOM and why is it important?",
            "How would you optimize a slow React application?",
            "What are CSS Grid and Flexbox used for?",
            "Explain async/await and Promises.",
        ],
        "Data Science": [
            "Explain overfitting and how to prevent it.",
            "What is the difference between supervised and unsupervised learning?",
            "How would you handle imbalanced datasets?",
            "Explain the bias-variance tradeoff.",
            "What evaluation metrics would you use for classification?",
        ],
    }
    
    def get_mock_interview(self, job_title: str, category: str = "Behavioral") -> Dict:
        """Get a mock interview with questions"""
        if category == "Behavioral":
            questions = self.BEHAVIORAL_QUESTIONS
        else:
            questions = self.TECHNICAL_QUESTIONS.get(category, self.BEHAVIORAL_QUESTIONS)
        
        selected_questions = random.sample(questions, min(3, len(questions)))
        
        return {
            "job_title": job_title,
            "category": category,
            "duration_minutes": 15,
            "questions": [
                {
                    "id": i,
                    "question": q,
                    "tips": self._get_tips_for_question(q, category),
                    "difficulty": random.choice(["Easy", "Medium", "Hard"])
                }
                for i, q in enumerate(selected_questions, 1)
            ]
        }
    
    def _get_tips_for_question(self, question: str, category: str) -> List[str]:
        """Generate tips for answering a question"""
        if "challenge" in question.lower() or "failed" in question.lower():
            return [
                "Use the STAR method (Situation, Task, Action, Result)",
                "Focus on what you learned",
                "Be honest but positive",
            ]
        elif "leadership" in question.lower():
            return [
                "Give a specific example",
                "Highlight impact on team",
                "Show growth mindset",
            ]
        elif category == "Technical":
            return [
                "Explain clearly, not too deep",
                "Ask clarifying questions",
                "Draw diagrams if needed",
            ]
        else:
            return [
                "Keep answer concise (2-3 minutes)",
                "Be specific with examples",
                "Connect to job requirements",
            ]
    
    def record_interview_performance(self, user_id: str, interview_data: Dict) -> Dict:
        """Record mock interview performance"""
        return {
            "user_id": user_id,
            "completed_at": "2024-01-01T00:00:00Z",
            "category": interview_data.get("category"),
            "job_title": interview_data.get("job_title"),
            "score": random.randint(60, 95),
            "feedback": self._generate_feedback(interview_data),
        }
    
    def _generate_feedback(self, interview_data: Dict) -> str:
        """Generate AI feedback on interview performance"""
        return """
        Great performance! Here's your feedback:
        
        ✅ Strengths:
        - Clear communication
        - Good use of examples
        - Addressed the question directly
        
        💡 Areas to improve:
        - Add more detail about the outcome
        - Practice speaking more concisely
        - Prepare more examples from your experience
        
        📚 Recommended topics to study:
        - STAR method for behavioral questions
        - Common interview questions for your role
        - Company research and culture fit
        """

interview_prep_service = InterviewPrepService()
