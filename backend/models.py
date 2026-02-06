from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class ContactInfo(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    portfolio: Optional[str] = None
    github: Optional[str] = None

class WorkExperience(BaseModel):
    company: str
    title: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    responsibilities: List[str] = []
    achievements: List[str] = []

class Education(BaseModel):
    degree: str
    institution: str
    graduation_date: Optional[str] = None
    gpa: Optional[str] = None
    honors: Optional[str] = None

class Project(BaseModel):
    name: str
    description: Optional[str] = None
    technologies: List[str] = []
    link: Optional[str] = None

class ResumeDetails(BaseModel):
    contact_info: Optional[ContactInfo] = None
    professional_summary: Optional[str] = None
    work_experience: List[WorkExperience] = []
    education: List[Education] = []
    technical_skills: List[str] = []
    soft_skills: List[str] = []
    certifications: List[str] = []
    projects: List[Project] = []
    languages: List[str] = []
    awards: List[str] = []

class MatchRequest(BaseModel):
    resume_details: Dict[str, Any]
    job_description: str

class MatchResult(BaseModel):
    match_percentage: int
    verdict: str
    matching_skills: List[str]
    missing_critical_requirements: List[str]
    missing_preferred_skills: List[str]
    experience_assessment: str
    education_fit: str
    key_strengths: List[str]
    gaps_to_address: List[str]
    recommendations: List[str]
    interview_likelihood: str
    summary: str

class AnalysisResponse(BaseModel):
    resume_details: Dict[str, Any]
    match_analysis: MatchResult