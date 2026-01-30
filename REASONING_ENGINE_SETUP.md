# Candidate Screening Reasoning Engine - Setup Guide

## 📋 Table of Contents
1. [Overview](#overview)
2. [Features](#features)
3. [Prerequisites](#prerequisites)
4. [Installation](#installation)
5. [Google API Setup (OAuth 2.0)](#google-api-setup-oauth-20-for-personal-accounts)
6. [Configuration](#configuration)
7. [Usage](#usage)
8. [Input Format](#input-format)
9. [Output Format](#output-format)
10. [Troubleshooting](#troubleshooting)
11. [Examples](#examples)

---

## 🎯 Overview

The Candidate Screening Reasoning Engine is an automated system that evaluates job candidates based on similarity scores, uploads resumes to Google Drive, generates comprehensive Excel reports, and sends email notifications via Gmail API. This version is configured to use OAuth 2.0, making it suitable for personal Gmail accounts.

### Decision Logic

The engine uses a **simple, score-based decision system**:

| Similarity Score | Decision | Reasoning |
|-----------------|----------|-----------|
| **≥ 69%** | Shortlisted | Strong match with job requirements |
| **50-68%** | Maybe | Moderate match, recommended for further review |
| **< 50%** | Rejected | Insufficient match with requirements |

---

## ✨ Features

- ✅ **Automated Decision Making** - Based solely on similarity scores
- 📤 **Google Drive Integration** - Upload resumes and generate shareable links
- 📊 **Professional Excel Reports** - Color-coded, formatted reports with reasoning
- 📧 **Gmail Notifications** - HTML email with summary statistics
- 🔐 **Secure Authentication** - Uses OAuth 2.0 for personal account access.
- 📝 **Comprehensive Logging** - Track all operations with detailed logs
- 🎨 **Professional Email Templates** - Branded HTML emails with statistics
- ⚙️ **Configurable Thresholds** - Adjust scoring criteria via environment variables

---

## 📦 Prerequisites

### Required Software
- Python 3.8 or higher
- pip (Python package manager)
- A web browser

### Required Accounts
- A standard Google (Gmail) account
- A Google Cloud Project (can be created for free)

---

## 🔧 Installation

### 1. Clone or Navigate to Project Directory

```bash
cd /path/to/ai-feature-extraction
```

### 2. Create Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate  # On Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `google-auth` - Google API authentication
- `google-auth-oauthlib` - OAuth2 support
- `google-auth-httplib2` - HTTP library support
- `google-api-python-client` - Google API client
- `pandas` - Data manipulation
- `openpyxl` - Excel file handling
- `python-dotenv` - Environment variable management

---

## 🔑 Google API Setup (OAuth 2.0 for Personal Accounts)

This guide details how to set up Google API access using **OAuth 2.0**, which is suitable for personal Gmail accounts and development environments. You do **not** need a Google Workspace account or Service Account for this method.

### Step 1: Create or Select a Google Cloud Project

1.  Go to the [Google Cloud Console](https://console.cloud.google.com/).
2.  Create a new project or select an existing one.

### Step 2: Enable Required APIs

You must enable the Gmail and Google Drive APIs for your project.

1.  Go to the [API Library](https://console.cloud.google.com/apis/library).
2.  Search for and enable the **Gmail API**.
3.  Search for and enable the **Google Drive API**.

### Step 3: Configure the OAuth Consent Screen

This screen is what you will see when you grant permission to the application.

1.  Navigate to [OAuth consent screen](https://console.cloud.google.com/apis/credentials/consent).
2.  Choose **External** for the User Type and click **Create**.
3.  Fill in the required application details:
    *   **App name:** "Candidate Screening Engine" (or a name of your choice).
    *   **User support email:** Your Gmail address.
    *   **Developer contact information:** Your Gmail address.
4.  Click **SAVE AND CONTINUE**.
5.  On the "Scopes" page, click **SAVE AND CONTINUE**. You don't need to add scopes here.
6.  On the "Test users" page, click **+ ADD USERS**.
7.  Enter your own Gmail address and click **ADD**. This is a critical step that allows you to use the app while it's in "testing" mode.
8.  Click **SAVE AND CONTINUE** and then **BACK TO DASHBOARD**.

### Step 4: Create OAuth 2.0 Client ID

This is the credential your application will use to authenticate.

1.  Navigate to [Credentials](https://console.cloud.google.com/apis/credentials).
2.  Click **+ CREATE CREDENTIALS** and select **OAuth client ID**.
3.  For **Application type**, select **Desktop app**.
4.  Give it a name, like "Screening Engine Desktop Client".
5.  Click **Create**.
6.  A dialog will appear. Click **DOWNLOAD JSON**.
7.  **Rename the downloaded file to `credentials.json`** and place it in your project directory.

---

## ⚙️ Configuration

### 1. Create `.env` File

Copy the example configuration file:

```bash
cp .env.example .env
```

### 2. Edit `.env` File

Open the `.env` file and update the variables:

-   `GOOGLE_CREDENTIALS_PATH`: The path to your `credentials.json` file.
    -   Example: `GOOGLE_CREDENTIALS_PATH=./credentials.json`
-   `GMAIL_SENDER_EMAIL`: Your personal Gmail address (the one you used as a test user).
-   `HR_EMAIL_RECIPIENT`: The email address where the final report will be sent.
-   `DRIVE_FOLDER_ID`: The ID of the Google Drive folder for resume uploads.

---

## 🚀 Usage

### First-Time Authorization

The very first time you run the script, you will need to authorize it:

1.  A new tab or window will open in your web browser.
2.  Log in to the Google account you designated as a "Test user".
3.  You may see a "Google hasn’t verified this app" warning. Click **"Advanced"** and then **"Go to [Your App Name] (unsafe)"**.
4.  Grant the requested permissions for Gmail and Google Drive.
5.  The script will then continue, and a `token.json` file will be created. This file stores your authorization for future runs.

### Running the Engine

Execute the script from your terminal:

```bash
python reasoning_engine.py --input path/to/your/candidates.json --output report.xlsx
```

### Examples

```bash
# Basic usage with sample data
python reasoning_engine.py -i sample_candidates.json -o first_report.xlsx

# Custom input and output files
python reasoning_engine.py \
  --input data/candidates.json \
  --output output/screening_report_2026.xlsx

# Short form
python reasoning_engine.py -i candidates.json -o report.xlsx

# Help
python reasoning_engine.py --help
```

---

## 📥 Input Format

### JSON Structure

Create a JSON file with candidate data:

```json
[
  {
    "candidate_name": "John Doe",
    "email": "john.doe@email.com",
    "phone": "+1-555-0101",
    "experience_years": 5,
    "skills": ["Python", "Machine Learning", "AWS"],
    "education": "BS Computer Science, Stanford University",
    "similarity_score": 85.5,
    "resume_file_path": "./resumes/john_doe_resume.pdf",
    "parsed_resume_text": "Optional: Full text of parsed resume"
  }
]
```

### Required Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `candidate_name` | string | Full name | "John Doe" |
| `email` | string | Email address | "john@email.com" |
| `phone` | string | Phone number | "+1-555-0101" |
| `experience_years` | number | Years of experience | 5 |
| `skills` | array | List of skills | ["Python", "AWS"] |
| `education` | string | Education background | "BS Computer Science" |
| `similarity_score` | number | Pre-calculated score (0-100) | 85.5 |
| `resume_file_path` | string | Path to resume file | "./resumes/resume.pdf" |

### Optional Fields

- `parsed_resume_text`: Full text content of resume

---

## 📤 Output Format

### Excel Report

The generated Excel file contains:

**Columns:**
- Candidate Name
- Email
- Phone
- Experience (Years)
- Similarity Score (%)
- Decision (Shortlisted/Maybe/Rejected)
- Reasoning (Detailed explanation)
- Resume URL (Google Drive link)
- Skills
- Education
- Processed Date

**Formatting:**
- Color-coded decisions:
  - 🟢 Green = Shortlisted
  - 🟡 Yellow = Maybe
  - 🔴 Red = Rejected
- Auto-adjusted column widths
- Frozen header row
- Professional styling

### Email Notification

**Subject:** `Candidate Screening Report - [Date]`

**Content:**
- Professional HTML template
- Summary statistics table
- Breakdown of Shortlisted/Maybe/Rejected counts
- Screening criteria explanation
- Next steps recommendations
- Excel report attachment

### Log Files

**app.log** contains:
- Timestamp for each operation
- Candidate processing status
- Upload confirmations
- Error messages with stack traces

---

## 🔍 Troubleshooting

### Common Issues

#### 1. "Credentials file not found"

**Problem:** `GOOGLE_CREDENTIALS_PATH` is incorrect or file doesn't exist

**Solution:**
```bash
# Use absolute path
GOOGLE_CREDENTIALS_PATH=/Users/username/project/credentials.json

# Verify file exists
ls -la /path/to/credentials.json
```

#### 2. "Insufficient permissions" for Drive

**Problem:** Script can't access Drive folder

**Solution:**
- Share folder with your Google account email
- Grant "Editor" permissions
- Wait a few minutes for permissions to propagate

#### 3. "Resume file not found"

**Problem:** Resume path in JSON is incorrect

**Solution:**
```json
{
  "resume_file_path": "./resumes/john_doe.pdf"  // Relative path
  // OR
  "resume_file_path": "/absolute/path/to/resume.pdf"  // Absolute path
}
```

#### 4. Import errors for Google libraries

**Problem:** Dependencies not installed

**Solution:**
```bash
pip install -r requirements.txt

# Or install individually
pip install google-auth google-api-python-client
```

#### 5. Email not sending

**Problem:** Gmail API authentication issues

**Solution:**
- Verify `GMAIL_SENDER_EMAIL` matches your Google account
- Ensure `credentials.json` is correctly configured
- Delete `token.json` and re-run the script to re-authorize

### Debug Mode

Enable detailed logging:

```python
# In reasoning_engine.py, change logging level
logging.basicConfig(level=logging.DEBUG)
```

### Verify Google API Setup

```bash
# Test Drive service
python google_drive_service.py

# Test Gmail service
python gmail_service.py

# Check environment variables
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('GOOGLE_CREDENTIALS_PATH'))"
```

---

## 📝 License

Copyright © 2026 AI Feature Extraction Team. All rights reserved.

---

## 🎉 Quick Start Checklist

- [ ] Python 3.8+ installed
- [ ] Google Cloud Project created
- [ ] Gmail API enabled
- [ ] Google Drive API enabled
- [ ] OAuth 2.0 Consent Screen configured with a test user
- [ ] OAuth 2.0 Client ID (for Desktop App) created and downloaded as `credentials.json`
- [ ] `.env` file configured with the path to `credentials.json` and other details
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Ready to authorize on first run

**Ready to go!** 🚀

```bash
python reasoning_engine.py -i sample_candidates.json -o first_report.xlsx
```
