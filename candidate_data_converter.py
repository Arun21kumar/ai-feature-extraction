"""
Candidate Data Converter Module

Converts feature extraction and similarity results into the format
expected by the reasoning engine for automated candidate screening.

Author: AI Feature Extraction Team
Date: February 2026
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any
import os

logger = logging.getLogger(__name__)


class CandidateDataConverter:
    """
    Converts similarity results and extracted features into reasoning engine format.
    """
    
    def __init__(self):
        """Initialize the converter."""
        pass
    
    def extract_candidate_name(self, resume_data: Dict[str, Any], resume_file_path: str) -> str:
        """
        Extract candidate name from resume data or filename.
        
        Args:
            resume_data: Extracted resume data
            resume_file_path: Path to the resume file
            
        Returns:
            Candidate name
        """
        # Try to get name from resume data (if available in summary or other fields)
        # For now, use filename as a fallback
        filename = Path(resume_file_path).stem
        # Clean up the filename
        name = filename.replace('_', ' ').replace('-', ' ')
        name = name.replace('.docx', '').replace('.pdf', '').replace('resume', '').strip()
        return name if name else "Unknown Candidate"
    
    def extract_contact_info(self, resume_data: Dict[str, Any]) -> tuple:
        """
        Extract email and phone from resume data.
        
        Args:
            resume_data: Extracted resume data
            
        Returns:
            Tuple of (email, phone)
        """
        # Since the current schema doesn't extract contact info,
        # we'll use placeholder values
        # TODO: Enhance schema to extract contact information
        email = resume_data.get('email', 'contact@example.com')
        phone = resume_data.get('phone', '+1-000-000-0000')
        return email, phone
    
    def extract_education(self, resume_data: Dict[str, Any]) -> str:
        """
        Extract education information from resume data.
        
        Args:
            resume_data: Extracted resume data
            
        Returns:
            Education string
        """
        # Check for education in certifications or summary
        education = resume_data.get('education', '')
        if not education:
            # Try to infer from certifications or summary
            certifications = resume_data.get('certifications', [])
            if certifications and isinstance(certifications, list):
                education = certifications[0] if certifications else 'Not specified'
            else:
                education = 'Not specified'
        return education
    
    def get_original_resume_path(self, extracted_json_path: str) -> str:
        """
        Get the path to the original resume file from the extracted JSON path.
        
        Args:
            extracted_json_path: Path to the extracted JSON file
            
        Returns:
            Path to original resume file
        """
        # The original file is likely in downloaded_attachments or sample-data
        json_path = Path(extracted_json_path)
        filename = json_path.stem  # e.g., "resume_Arun_Resume"
        
        # Remove prefix patterns
        for prefix in ['resume_', 'jd_']:
            if filename.startswith(prefix):
                filename = filename[len(prefix):]
        
        # Look for the original file in common locations
        base_dir = json_path.parent.parent
        search_dirs = [
            base_dir / 'downloaded_attachments',
            base_dir / 'sample-data',
            base_dir / 'resumes'
        ]
        
        # Create variations of the filename to search for
        filename_variations = [
            filename,                              # Original: "Arun_Resume"
            filename.replace('_', ' '),            # With spaces: "Arun Resume"
            filename.replace(' ', '_'),            # With underscores: "Arun_Resume"
        ]
        
        for search_dir in search_dirs:
            if search_dir.exists():
                # Try different extensions and filename variations
                for name_variant in filename_variations:
                    for ext in ['.docx', '.pdf', '.doc']:
                        potential_file = search_dir / f"{name_variant}{ext}"
                        if potential_file.exists():
                            return str(potential_file)
                
                # Also try fuzzy matching - find any file that contains the base name
                try:
                    for file in search_dir.glob('*.docx'):
                        # Normalize both filenames for comparison (lowercase, no spaces/underscores)
                        normalized_search = filename.lower().replace('_', '').replace(' ', '')
                        normalized_file = file.stem.lower().replace('_', '').replace(' ', '')
                        if normalized_search in normalized_file or normalized_file in normalized_search:
                            return str(file)
                except Exception:
                    pass
        
        # Return a relative path as fallback
        return f"./downloaded_attachments/{filename}.docx"
    
    def convert_similarity_results(
        self,
        similarity_results: List[Dict[str, Any]],
        output_path: str = None
    ) -> List[Dict[str, Any]]:
        """
        Convert similarity results to reasoning engine format.
        
        Args:
            similarity_results: List of similarity result dictionaries from vector pipeline
            output_path: Optional path to save the converted JSON
            
        Returns:
            List of candidate dictionaries in reasoning engine format
        """
        logger.info(f"Converting {len(similarity_results)} similarity results to reasoning engine format")
        
        candidates = []
        
        for result in similarity_results:
            resume_data = result.get('resume_data', {})
            resume_file = result.get('resume_file', '')
            similarity_score = result.get('similarity_score', 0.0)
            
            # Extract candidate information
            candidate_name = self.extract_candidate_name(resume_data, resume_file)
            email, phone = self.extract_contact_info(resume_data)
            experience_years = resume_data.get('experience_years', 0)
            skills = resume_data.get('skills', [])
            education = self.extract_education(resume_data)
            
            # Get original resume file path
            resume_file_path = self.get_original_resume_path(resume_file)
            
            # Create candidate entry
            candidate = {
                'candidate_name': candidate_name,
                'email': email,
                'phone': phone,
                'experience_years': experience_years,
                'skills': skills if isinstance(skills, list) else [skills],
                'education': education,
                'similarity_score': round(similarity_score, 2),
                'resume_file_path': resume_file_path,
                'section_scores': result.get('section_scores', {}),
                'jd_file': result.get('jd_file', ''),
                'extracted_resume_file': resume_file
            }
            
            candidates.append(candidate)
            logger.info(f"Converted candidate: {candidate_name} (Score: {similarity_score:.2f}%)")
        
        # Sort by similarity score (descending)
        candidates.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        # Save to file if output path is provided
        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(candidates, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Converted candidates saved to: {output_path}")
        
        return candidates


def main():
    """
    Command-line interface for testing the converter.
    """
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python candidate_data_converter.py <similarity_results.json> [output.json]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'output/candidates_for_reasoning_engine.json'
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Load similarity results
    with open(input_file, 'r', encoding='utf-8') as f:
        similarity_results = json.load(f)
    
    # Convert
    converter = CandidateDataConverter()
    candidates = converter.convert_similarity_results(similarity_results, output_file)
    
    print(f"\nConverted {len(candidates)} candidates")
    print(f"Output saved to: {output_file}")


if __name__ == '__main__':
    main()
