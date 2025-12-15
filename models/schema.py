"""
Data models for feature extraction schema.
Defines the structure of extracted information from resumes and job descriptions.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class ExtractedFeatures(BaseModel):
    """
    A simple, unified schema for extracted features from either a resume or a job description.
    """
    document_type: str = Field(description="Type of document: 'jd' or 'resume'")
    summary: Optional[str] = Field(default=None, description="A concise summary of the document.")
    experience_years: Optional[float] = Field(default=None, description="For a JD, the preferred years of experience. For a resume, the candidate's total years of experience.")
    skills: List[str] = Field(default_factory=list, description="A list of technical and soft skills.")
    certifications: List[str] = Field(default_factory=list, description="A list of professional certifications.")
    responsibilities: List[str] = Field(default_factory=list, description="A list of key responsibilities or job duties.")

    def to_dict(self) -> dict:
        """Convert to dictionary format."""
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: dict) -> "ExtractedFeatures":
        """Create instance from dictionary."""
        return cls(**data)
