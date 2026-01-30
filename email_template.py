"""
Email Template Module

Generates professional HTML email templates for candidate screening reports.

Author: AI Feature Extraction Team
Date: January 2026
"""

from datetime import datetime


def generate_email_html(
    total_candidates: int,
    shortlisted: int,
    maybe: int,
    rejected: int
) -> str:
    """
    Generate professional HTML email body for screening report.
    
    Args:
        total_candidates: Total number of candidates processed
        shortlisted: Number of shortlisted candidates
        maybe: Number of maybe candidates
        rejected: Number of rejected candidates
        
    Returns:
        HTML email body as string
    """
    
    current_date = datetime.now().strftime('%B %d, %Y')
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Candidate Screening Report</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; background-color: #f4f4f4;">
    
    <!-- Email Container -->
    <div style="background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); overflow: hidden;">
        
        <!-- Header -->
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #ffffff; padding: 30px; text-align: center;">
            <h1 style="margin: 0; font-size: 28px; font-weight: 600;">
                🎯 Candidate Screening Report
            </h1>
            <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.95;">
                Automated Analysis Complete - {current_date}
            </p>
        </div>
        
        <!-- Main Content -->
        <div style="padding: 40px 30px;">
            
            <!-- Greeting -->
            <p style="font-size: 16px; color: #555; margin-bottom: 25px;">
                Dear Hiring Team,
            </p>
            
            <p style="font-size: 16px; color: #555; margin-bottom: 30px;">
                The automated candidate screening engine has successfully processed and analyzed 
                <strong style="color: #667eea;">{total_candidates} candidate(s)</strong> based on similarity scoring 
                and job requirement matching. Please find the detailed results attached to this email.
            </p>
            
            <!-- Summary Statistics -->
            <div style="background-color: #f8f9fa; border-radius: 8px; padding: 25px; margin-bottom: 30px;">
                <h2 style="margin: 0 0 20px 0; font-size: 20px; color: #333; border-bottom: 2px solid #667eea; padding-bottom: 10px;">
                    📊 Screening Summary
                </h2>
                
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 15px; background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 6px; width: 60%;">
                            <span style="font-size: 16px; color: #155724; font-weight: 600;">✓ Shortlisted Candidates</span>
                        </td>
                        <td style="padding: 15px; background-color: #d4edda; border: 1px solid #c3e6cb; border-radius: 6px; text-align: center; width: 40%;">
                            <span style="font-size: 24px; color: #155724; font-weight: 700;">{shortlisted}</span>
                        </td>
                    </tr>
                    <tr style="height: 10px;"></tr>
                    <tr>
                        <td style="padding: 15px; background-color: #fff3cd; border: 1px solid #ffeeba; border-radius: 6px;">
                            <span style="font-size: 16px; color: #856404; font-weight: 600;">⚠ Requires Further Review (Maybe)</span>
                        </td>
                        <td style="padding: 15px; background-color: #fff3cd; border: 1px solid #ffeeba; border-radius: 6px; text-align: center;">
                            <span style="font-size: 24px; color: #856404; font-weight: 700;">{maybe}</span>
                        </td>
                    </tr>
                    <tr style="height: 10px;"></tr>
                    <tr>
                        <td style="padding: 15px; background-color: #f8d7da; border: 1px solid #f5c6cb; border-radius: 6px;">
                            <span style="font-size: 16px; color: #721c24; font-weight: 600;">✗ Not Shortlisted (Rejected)</span>
                        </td>
                        <td style="padding: 15px; background-color: #f8d7da; border: 1px solid #f5c6cb; border-radius: 6px; text-align: center;">
                            <span style="font-size: 24px; color: #721c24; font-weight: 700;">{rejected}</span>
                        </td>
                    </tr>
                </table>
            </div>
            
            <!-- Screening Criteria Info -->
            <div style="background-color: #e7f3ff; border-left: 4px solid #667eea; padding: 20px; margin-bottom: 30px; border-radius: 4px;">
                <h3 style="margin: 0 0 10px 0; font-size: 16px; color: #0056b3;">
                    ℹ️ Screening Criteria Applied
                </h3>
                <ul style="margin: 5px 0; padding-left: 20px; color: #555; font-size: 14px;">
                    <li><strong>Shortlisted:</strong> Similarity score ≥ 69% - Strong match with job requirements</li>
                    <li><strong>Maybe:</strong> Similarity score 50-68% - Moderate match, recommended for interview</li>
                    <li><strong>Rejected:</strong> Similarity score &lt; 50% - Insufficient match with requirements</li>
                </ul>
            </div>
            
            <!-- Attached Report Info -->
            <div style="background-color: #fff8e1; border-radius: 8px; padding: 20px; margin-bottom: 30px; border: 1px solid #ffe082;">
                <h3 style="margin: 0 0 10px 0; font-size: 16px; color: #f57f17;">
                    📎 Attached Report Details
                </h3>
                <p style="margin: 0; font-size: 14px; color: #555;">
                    The attached Excel file contains comprehensive information for each candidate including:
                </p>
                <ul style="margin: 10px 0 0 0; padding-left: 20px; color: #555; font-size: 14px;">
                    <li>Contact information (name, email, phone)</li>
                    <li>Experience and education details</li>
                    <li>Similarity scores and hiring decisions</li>
                    <li>Detailed reasoning for each decision</li>
                    <li>Direct links to resumes stored in Google Drive</li>
                    <li>Skills and qualifications summary</li>
                </ul>
            </div>
            
            <!-- Next Steps -->
            <div style="background-color: #f8f9fa; border-radius: 8px; padding: 25px; margin-bottom: 30px;">
                <h2 style="margin: 0 0 15px 0; font-size: 18px; color: #333;">
                    🎯 Recommended Next Steps
                </h2>
                <ol style="margin: 0; padding-left: 20px; color: #555; font-size: 15px; line-height: 1.8;">
                    <li><strong>Review Shortlisted Candidates:</strong> Prioritize candidates with high similarity scores for immediate interview scheduling</li>
                    <li><strong>Evaluate "Maybe" Candidates:</strong> Conduct phone screens or additional assessments to determine fit</li>
                    <li><strong>Access Resumes:</strong> Use the provided Google Drive links to review full resume documents</li>
                    <li><strong>Schedule Interviews:</strong> Coordinate with the hiring team to set up interview rounds</li>
                    <li><strong>Document Feedback:</strong> Record interview notes and final hiring decisions in the Excel report</li>
                </ol>
            </div>
            
            <!-- Call to Action -->
            <div style="text-align: center; margin: 30px 0;">
                <p style="font-size: 16px; color: #555; margin-bottom: 15px;">
                    Questions about the screening process or need additional information?
                </p>
                <a href="mailto:hr-support@company.com" style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #ffffff; text-decoration: none; padding: 14px 32px; border-radius: 6px; font-size: 16px; font-weight: 600; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                    Contact HR Support
                </a>
            </div>
            
            <!-- Closing -->
            <p style="font-size: 16px; color: #555; margin-top: 30px;">
                Best regards,<br>
                <strong style="color: #667eea;">AI-Powered Recruitment Team</strong><br>
                Automated Candidate Screening Engine
            </p>
            
        </div>
        
        <!-- Footer -->
        <div style="background-color: #f8f9fa; padding: 25px 30px; border-top: 1px solid #e9ecef; text-align: center;">
            <p style="margin: 0; font-size: 13px; color: #6c757d; line-height: 1.6;">
                This is an automated report generated by the AI Feature Extraction Candidate Screening System.<br>
                Report generated on {current_date} | Powered by Advanced Similarity Matching Algorithms
            </p>
            <p style="margin: 15px 0 0 0; font-size: 12px; color: #adb5bd;">
                © {datetime.now().year} AI Feature Extraction Team. All rights reserved.
            </p>
        </div>
        
    </div>
    
    <!-- Email Footer Note -->
    <div style="text-align: center; margin-top: 20px; padding: 15px;">
        <p style="font-size: 12px; color: #999; margin: 0;">
            Please do not reply to this email. For support, contact your HR administrator.
        </p>
    </div>
    
</body>
</html>
    """
    
    return html.strip()


def generate_plain_text_email(
    total_candidates: int,
    shortlisted: int,
    maybe: int,
    rejected: int
) -> str:
    """
    Generate plain text version of email for fallback.
    
    Args:
        total_candidates: Total number of candidates processed
        shortlisted: Number of shortlisted candidates
        maybe: Number of maybe candidates
        rejected: Number of rejected candidates
        
    Returns:
        Plain text email body as string
    """
    
    current_date = datetime.now().strftime('%B %d, %Y')
    
    text = f"""
CANDIDATE SCREENING REPORT
{current_date}

Dear Hiring Team,

The automated candidate screening engine has successfully processed and analyzed {total_candidates} candidate(s) 
based on similarity scoring and job requirement matching. Please find the detailed results attached to this email.

SCREENING SUMMARY
=================

✓ Shortlisted Candidates:           {shortlisted}
⚠ Requires Further Review (Maybe):  {maybe}
✗ Not Shortlisted (Rejected):       {rejected}

SCREENING CRITERIA APPLIED
==========================

- Shortlisted: Similarity score ≥ 69% - Strong match with job requirements
- Maybe: Similarity score 50-68% - Moderate match, recommended for interview
- Rejected: Similarity score < 50% - Insufficient match with requirements

ATTACHED REPORT DETAILS
=======================

The attached Excel file contains comprehensive information for each candidate including:
- Contact information (name, email, phone)
- Experience and education details
- Similarity scores and hiring decisions
- Detailed reasoning for each decision
- Direct links to resumes stored in Google Drive
- Skills and qualifications summary

RECOMMENDED NEXT STEPS
======================

1. Review Shortlisted Candidates: Prioritize candidates with high similarity scores for immediate interview scheduling
2. Evaluate "Maybe" Candidates: Conduct phone screens or additional assessments to determine fit
3. Access Resumes: Use the provided Google Drive links to review full resume documents
4. Schedule Interviews: Coordinate with the hiring team to set up interview rounds
5. Document Feedback: Record interview notes and final hiring decisions in the Excel report

Best regards,
AI-Powered Recruitment Team
Automated Candidate Screening Engine

---
This is an automated report generated by the AI Feature Extraction Candidate Screening System.
Report generated on {current_date} | Powered by Advanced Similarity Matching Algorithms

© {datetime.now().year} AI Feature Extraction Team. All rights reserved.
    """
    
    return text.strip()


# Example usage and testing
if __name__ == '__main__':
    # Generate sample email
    html = generate_email_html(
        total_candidates=10,
        shortlisted=3,
        maybe=4,
        rejected=3
    )
    
    # Save to file for preview
    with open('sample_email.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print("✓ Sample email HTML generated: sample_email.html")
    print("\nEmail preview:")
    print("=" * 80)
    
    # Print plain text version
    text = generate_plain_text_email(
        total_candidates=10,
        shortlisted=3,
        maybe=4,
        rejected=3
    )
    print(text)
