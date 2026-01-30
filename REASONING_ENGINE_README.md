# Candidate Screening Reasoning Engine

🎯 **Automated intelligent candidate screening with Google Drive integration and Gmail notifications**

## Overview

A production-ready Python-based reasoning engine that automates candidate screening by:
- Evaluating candidates based on similarity scores
- Making intelligent hiring decisions (Shortlisted/Maybe/Rejected)
- Uploading resumes to Google Drive with shareable links
- Generating professional Excel reports with color-coded formatting
- Sending HTML email notifications via Gmail API

## Setup & Configuration (for Personal Gmail Accounts)

This engine now uses **OAuth 2.0** for authentication, which is ideal for personal Gmail accounts and development environments.

1.  **Enable APIs & Create Credentials:**
    *   Follow the detailed instructions in the `.env.example` file to:
        1.  Enable the Gmail and Google Drive APIs in your Google Cloud project.
        2.  Configure the OAuth Consent Screen.
        3.  Create and download an **OAuth 2.0 Client ID** for a **Desktop App**.
        4.  Save the downloaded file as `credentials.json`.

2.  **Configure Environment:**
    *   Copy the example environment file:
        ```bash
        cp .env.example .env
        ```
    *   Edit the `.env` file and update the following variables:
        *   `GOOGLE_CREDENTIALS_PATH`: Set this to the path of your `credentials.json` file.
        *   `GMAIL_SENDER_EMAIL`: Your personal Gmail address.
        *   `HR_EMAIL_RECIPIENT`: The email address where reports should be sent.
        *   `DRIVE_FOLDER_ID`: The ID of the Google Drive folder for resume uploads.

3.  **Authorize the Application (First Run Only):**
    *   The first time you run the script, a browser window will open.
    *   Log in with your Google account and grant the application permission to access your Drive and Gmail.
    *   A `token.json` file will be created. This file securely stores your authorization for future runs. **Do not commit this file.**

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment (see setup steps above)
cp .env.example .env
# Edit .env with your OAuth credentials path and other settings

# 3. Run the engine
python reasoning_engine.py --input sample_candidates.json --output report.xlsx
```

## Features

✅ **Score-Based Decision Logic**
- ≥69% = Shortlisted (Strong match)
- 50-68% = Maybe (Moderate match)
- <50% = Rejected (Insufficient match)

✅ **Google Drive Integration**
- Automated resume uploads
- Public shareable links
- Organized folder structure

✅ **Professional Excel Reports**
- Color-coded decisions (Green/Yellow/Red)
- Auto-formatted columns
- Comprehensive candidate data

✅ **Gmail Automation**
- HTML email templates
- Summary statistics
- Report attachments

✅ **Robust Error Handling**
- Detailed logging to `app.log`
- Graceful failure recovery
- Progress indicators

## Architecture

```
reasoning_engine.py          # Main orchestration module
├── google_drive_service.py  # Google Drive API integration
├── gmail_service.py          # Gmail API integration
├── email_template.py         # HTML email templates
└── .env                      # Configuration (not committed)
```

## Decision Logic

The engine uses **ONLY the similarity_score** to make decisions:

```python
if similarity_score >= 69:
    decision = "Shortlisted"
    reasoning = "Strong match with job requirements..."
elif similarity_score >= 50:
    decision = "Maybe"
    reasoning = "Moderate match, recommended for review..."
else:
    decision = "Rejected"
    reasoning = "Insufficient match with requirements..."
```

## Input Format

```json
[
  {
    "candidate_name": "John Doe",
    "email": "john@email.com",
    "phone": "+1-555-0101",
    "experience_years": 5,
    "skills": ["Python", "ML", "AWS"],
    "education": "BS Computer Science",
    "similarity_score": 85.5,
    "resume_file_path": "./resumes/john_doe.pdf"
  }
]
```

## Output Format

### Excel Report Columns:
- Candidate Name
- Email & Phone
- Experience (years)
- **Similarity Score (%)** - Center-aligned
- **Decision** - Color-coded (Green/Yellow/Red)
- **Reasoning** - Detailed explanation
- **Resume URL** - Google Drive shareable link
- Skills & Education
- Processed Date

### Email Notification:
- Professional HTML template
- Summary statistics table
- Breakdown: X Shortlisted, Y Maybe, Z Rejected
- Excel report attached

## Setup Requirements

### 1. Google Cloud Setup
- Create Google Cloud Project
- Enable Gmail API
- Enable Google Drive API
- Create Service Account
- Download credentials JSON

### 2. Google Workspace (for Gmail)
- Enable Domain-Wide Delegation
- Add OAuth scopes in Admin Console
- Configure sender email

### 3. Environment Configuration
```bash
GOOGLE_CREDENTIALS_PATH=/path/to/credentials.json
GMAIL_SENDER_EMAIL=sender@company.com
HR_EMAIL_RECIPIENT=hr@company.com
DRIVE_FOLDER_ID=your-folder-id
SHORTLIST_THRESHOLD=69
REJECT_THRESHOLD=50
```

## Usage Examples

### Basic Usage
```bash
python reasoning_engine.py --input candidates.json --output report.xlsx
```

### With Custom Paths
```bash
python reasoning_engine.py \
  --input data/jan2026_candidates.json \
  --output output/screening_jan2026.xlsx
```

### Test with Sample Data
```bash
python reasoning_engine.py -i sample_candidates.json -o test.xlsx
```

## Module Documentation

### reasoning_engine.py
Main orchestration module with:
- `parse_json()` - Load and validate candidate data
- `determine_decision()` - Apply scoring thresholds
- `generate_reasoning()` - Create professional explanations
- `upload_resume_to_drive()` - Upload files and get links
- `create_excel_report()` - Generate formatted Excel
- `send_email_with_report()` - Send Gmail notification

### google_drive_service.py
Google Drive API service:
- Service account authentication
- File upload with resumable uploads
- Permission management (public links)
- MIME type detection

### gmail_service.py
Gmail API service:
- Domain-wide delegation support
- HTML email composition
- File attachments
- Error handling

### email_template.py
Email template generation:
- Professional HTML design
- Summary statistics tables
- Color-coded breakdowns
- Responsive design

## Logging

All operations logged to `app.log`:
```
2026-01-23 10:15:30 - INFO - Processing candidate 1/10: John Doe
2026-01-23 10:15:32 - INFO - Resume uploaded successfully for John Doe
2026-01-23 10:15:33 - INFO - ✓ John Doe: Shortlisted (85.5%)
```

## Error Handling

The engine handles:
- Missing resume files (logs error, continues processing)
- Invalid JSON structure (validation errors)
- Google API failures (retries, fallback links)
- Network issues (graceful degradation)

## Security

🔒 **Security Best Practices:**
- Never commit `.env` file
- Rotate service account keys regularly
- Use least privilege API scopes
- Encrypt credentials at rest
- Monitor API usage logs

## Troubleshooting

### Common Issues:

**"Credentials file not found"**
→ Check `GOOGLE_CREDENTIALS_PATH` is absolute path

**"Domain-wide delegation required"**
→ Enable in service account + Google Workspace Admin

**"Resume upload failed"**
→ Share Drive folder with service account email

**"Email not sending"**
→ Verify delegation scopes in Workspace Admin Console

See [REASONING_ENGINE_SETUP.md](REASONING_ENGINE_SETUP.md) for detailed troubleshooting.

## Testing

### Test Individual Components
```bash
# Test Google Drive
python google_drive_service.py

# Test Gmail
python gmail_service.py

# Test Email Template
python email_template.py
open sample_email.html
```

## Performance

- Processes 100 candidates in ~2-3 minutes
- Handles batch uploads efficiently
- Resumable uploads for large files
- Parallel processing ready (future enhancement)

## Dependencies

```
google-auth==2.23.0
google-auth-oauthlib==1.1.0
google-auth-httplib2==0.1.1
google-api-python-client==2.100.0
pandas==2.1.1
openpyxl==3.1.2
python-dotenv==1.0.0
```

## File Structure

```
.
├── reasoning_engine.py           # Main engine
├── google_drive_service.py       # Drive API
├── gmail_service.py               # Gmail API
├── email_template.py              # Email templates
├── requirements.txt               # Dependencies
├── .env.example                   # Config template
├── sample_candidates.json         # Sample data
├── REASONING_ENGINE_SETUP.md      # Detailed guide
└── app.log                        # Runtime logs
```

## Contributing

When extending the engine:
1. Add comprehensive docstrings
2. Include error handling
3. Update logging
4. Write tests
5. Update documentation

## License

Copyright © 2026 AI Feature Extraction Team. All rights reserved.

## Support

For detailed setup instructions, see [REASONING_ENGINE_SETUP.md](REASONING_ENGINE_SETUP.md)

For issues:
1. Check `app.log` for errors
2. Review troubleshooting guide
3. Test components individually
4. Verify Google API setup

---

**Made with ❤️ by the AI Feature Extraction Team**

🚀 **Ready to automate your candidate screening!**
