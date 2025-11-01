"""AI-powered job classification using OpenAI GPT."""

from typing import Tuple, Optional
import os
from openai import OpenAI
from src.ingest.schemas import JobPosting
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class AIJobClassifier:
    """Use AI to intelligently classify and filter jobs."""
    
    def __init__(self):
        """Initialize AI classifier with OpenAI client."""
        self.logger = logger
        api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            self.logger.warning("OPENAI_API_KEY not set - AI classification disabled")
            self.enabled = False
            self.client = None
        else:
            self.client = OpenAI(api_key=api_key)
            self.enabled = True
            self.logger.info("AI Job Classifier initialized")
    
    def classify_job(self, job: JobPosting) -> Tuple[Optional[str], float, bool]:
        """
        Use AI to classify a job and determine relevance.
        
        Args:
            job: JobPosting to classify
            
        Returns:
            Tuple of (category, confidence_score, is_relevant)
            - category: Job category (backend, frontend, ml, data, etc.)
            - confidence_score: 0-1 score of classification confidence
            - is_relevant: Whether job is a relevant internship
        """
        if not self.enabled:
            # Fallback to basic classification
            return None, 0.0, True
        
        try:
            # Create prompt for GPT
            prompt = f"""
Analyze this job posting and provide:
1. Category (backend, frontend, fullstack, ml, data, devops, security, mobile, or other)
2. Confidence score (0.0 to 1.0)
3. Whether this is a relevant 2025/2026 software engineering internship (yes/no)

Job Title: {job.title}
Company: {job.company}
Location: {job.location or 'Remote'}
Description Preview: {job.description_md[:500] if job.description_md else 'N/A'}

Requirements for relevance:
- Must be an internship (not full-time)
- Must be for software engineering, CS, or related technical role
- Must be for 2025 or 2026 (not past years)
- Should not be: sales, recruiting, non-technical business roles

Respond in this exact format:
Category: [category]
Confidence: [0.0-1.0]
Relevant: [yes/no]
Reason: [brief 1-sentence explanation]
"""
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Cheaper and faster than gpt-4
                messages=[
                    {"role": "system", "content": "You are an expert at analyzing job postings for software engineering internships."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.3  # Lower temperature for more consistent results
            )
            
            # Parse response
            result = response.choices[0].message.content.strip()
            lines = result.split('\n')
            
            category = None
            confidence = 0.5
            is_relevant = True
            
            for line in lines:
                if line.startswith("Category:"):
                    category = line.split(":", 1)[1].strip().lower()
                elif line.startswith("Confidence:"):
                    try:
                        confidence = float(line.split(":", 1)[1].strip())
                    except ValueError:
                        confidence = 0.5
                elif line.startswith("Relevant:"):
                    relevant_str = line.split(":", 1)[1].strip().lower()
                    is_relevant = relevant_str == "yes" or relevant_str == "true"
                elif line.startswith("Reason:"):
                    reason = line.split(":", 1)[1].strip()
                    self.logger.debug(f"AI reasoning for {job.company} - {job.title}: {reason}")
            
            self.logger.info(f"AI classified {job.company} - {job.title}: {category} (confidence: {confidence:.2f}, relevant: {is_relevant})")
            
            return category, confidence, is_relevant
        
        except Exception as e:
            self.logger.error(f"Error in AI classification: {e}")
            # Fallback to assuming relevance
            return None, 0.0, True
    
    def extract_skills(self, job: JobPosting) -> list[str]:
        """
        Extract technical skills mentioned in job description.
        
        Args:
            job: JobPosting to analyze
            
        Returns:
            List of technical skills
        """
        if not self.enabled or not job.description_md:
            return []
        
        try:
            prompt = f"""
Extract all technical skills, programming languages, and technologies mentioned in this job description.

Job Description:
{job.description_md[:1000]}

List only the technical skills, one per line, no explanations. Example:
Python
React
AWS
Docker
"""
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert at extracting technical skills from job descriptions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            result = response.choices[0].message.content.strip()
            skills = [s.strip() for s in result.split('\n') if s.strip()]
            
            return skills[:15]  # Limit to 15 skills
        
        except Exception as e:
            self.logger.error(f"Error extracting skills: {e}")
            return []
    
    def check_visa_sponsorship(self, job: JobPosting) -> Optional[bool]:
        """
        Check if job mentions visa sponsorship.
        
        Args:
            job: JobPosting to analyze
            
        Returns:
            True if sponsors visa, False if not, None if unknown
        """
        if not self.enabled or not job.description_md:
            return None
        
        try:
            prompt = f"""
Does this job posting mention visa sponsorship or work authorization requirements?

Job Description:
{job.description_md[:800]}

Answer with ONLY one word:
- YES (if they sponsor visas or don't require work authorization)
- NO (if they explicitly state no visa sponsorship or require existing work authorization)
- UNKNOWN (if not mentioned)
"""
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=10,
                temperature=0
            )
            
            result = response.choices[0].message.content.strip().upper()
            
            if result == "YES":
                return True
            elif result == "NO":
                return False
            else:
                return None
        
        except Exception as e:
            self.logger.error(f"Error checking visa sponsorship: {e}")
            return None
