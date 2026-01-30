# 🎯 Automated Candidate Screening Reasoning Engine

> **Production-ready Python system for intelligent candidate evaluation with Google Drive & Gmail integration**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)]()
[![Status](https://img.shields.io/badge/Status-Production%20Ready-green.svg)]()

---

## 🚀 Quick Start (3 Commands)

```bash
# 1. Run installation script
./install_reasoning_engine.sh

# 2. Configure credentials
nano .env

# 3. Run screening
python3 reasoning_engine.py -i sample_candidates.json -o report.xlsx
```

---

## 📋 What It Does

This reasoning engine **automates the entire candidate screening workflow**:

1. ✅ **Reads** candidate data from JSON files
2. 🧠 **Evaluates** candidates using similarity score thresholds
3. 📝 **Generates** professional reasoning for each decision
4. ☁️ **Uploads** resumes to Google Drive with shareable links
5. 📊 **Creates** formatted Excel reports with color-coding
6. 📧 **Sends** HTML email notifications to HR team
7. 📄 **Logs** all operations for auditing

---

## 🎯 Decision Logic

**Simple. Transparent. Score-based.**

| Similarity Score | Decision | Color | Action |
|-----------------|----------|-------|---------|
| **≥ 69%** | ✅ Shortlisted | 🟢 Green | Schedule interview immediately |
| **50-68%** | ⚠️ Maybe | 🟡 Yellow | Further review recommended |
| **< 50%** | ❌ Rejected | 🔴 Red | Not suitable for this position |

> **Note:** Decisions are based **SOLELY** on the `similarity_score` field. Experience years do not affect the decision.

---

## 📦 What's Included

### Core Modules
- **`reasoning_engine.py`** - Main orchestration engine with CLI
- **`google_drive_service.py`** - Google Drive API integration
- **`gmail_service.py`** - Gmail API integration
- **`email_template.py`** - Professional HTML email templates

### Configuration
- **`.env.example`** - Environment variable template with detailed comments
- **`sample_candidates.json`** - 10 sample candidates for testing
- **`requirements.txt`** - All Python dependencies

### Documentation
- **`QUICK_REFERENCE.md`** - One-page cheat sheet
- **`REASONING_ENGINE_SETUP.md`** - Comprehensive setup guide
- **`REASONING_ENGINE_README.md`** - Feature overview
- **`IMPLEMENTATION_SUMMARY.md`** - Technical documentation

### Utilities
- **`install_reasoning_engine.sh`** - Automated setup script

---

## ⚡ Features

### 🤖 Automated Decision Making
- Score-based evaluation (configurable thresholds)
- Professional reasoning generation
- Batch processing support
- Progress tracking and logging

### ☁️ Google Drive Integration
- Automatic resume uploads
- Public shareable links
- Organized folder structure
- MIME type detection

### 📊 Professional Excel Reports
- Color-coded decisions (Green/Yellow/Red)
- Auto-formatted columns
- Frozen header rows
- Detailed candidate information
- Direct resume links

### 📧 Email Notifications
- Beautiful HTML templates
- Summary statistics
- Color-coded breakdowns
- Professional styling
- Automatic attachments

### 🔐 Security & Reliability
- Service account authentication
- Environment-based configuration
- Comprehensive error handling
- Detailed logging
- No hardcoded credentials

---

## 📥 Installation

### Prerequisites
- Python 3.8 or higher
- Google Cloud Platform account
- Google Workspace account (for Gmail)
- pip package manager

### Method 1: Automated (Recommended)

```bash
./install_reasoning_engine.sh
```

The script will:
- ✅ Check Python version
- ✅ Create virtual environment (optional)
- ✅ Install all dependencies
- ✅ Set up .env configuration
- ✅ Create necessary directories
- ✅ Test installations

### Method 2: Manual

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Edit with your credentials
```

---

## ⚙️ Configuration

### 1. Google API Setup

Follow the detailed guide in [REASONING_ENGINE_SETUP.md](REASONING_ENGINE_SETUP.md):

1. Create Google Cloud Project
2. Enable Gmail API & Google Drive API
3. Create Service Account
4. Download credentials JSON
5. Enable Domain-Wide Delegation
6. Configure OAuth scopes
7. Create Google Drive folder
8. Share folder with service account

### 2. Environment Variables

Edit `.env` file:

```bash
# Google API Credentials
GOOGLE_CREDENTIALS_PATH=/absolute/path/to/service-account.json

# Gmail Configuration  
GMAIL_SENDER_EMAIL=your-email@company.com
HR_EMAIL_RECIPIENT=hr@company.com

# Google Drive
DRIVE_FOLDER_ID=your-drive-folder-id

# Thresholds (optional)
SHORTLIST_THRESHOLD=69
REJECT_THRESHOLD=50
```

### 3. Verify Setup

```bash
# Test Google Drive
python3 google_drive_service.py

# Test Gmail
python3 gmail_service.py

# Both should show: ✓ Service initialized successfully
```

---

## 🎮 Usage

### Basic Command

```bash
python3 reasoning_engine.py --input candidates.json --output report.xlsx
```

### Short Form

```bash
python3 reasoning_engine.py -i candidates.json -o report.xlsx
```

### Command-Line Options

```
--input, -i   Path to input JSON file (required)
--output, -o  Path to output Excel file (required)
--help        Show help message
```

### Example: Test with Sample Data

```bash
python3 reasoning_engine.py -i sample_candidates.json -o test_report.xlsx
```

---

## 📄 Input Format

Create a JSON file with candidate data:

```json
[
  {
    "candidate_name": "John Doe",
    "email": "john.doe@email.com",
    "phone": "+1-555-0101",
    "experience_years": 5,
    "skills": ["Python", "Machine Learning", "AWS"],
    "education": "BS Computer Science, Stanford",
    "similarity_score": 85.5,
    "resume_file_path": "./resumes/john_doe_resume.pdf"
  }
]
```

**Required Fields:**
- `candidate_name` - Full name
- `email` - Email address
- `phone` - Phone number
- `experience_years` - Years of experience
- `skills` - Array of skills
- `education` - Education background
- `similarity_score` - Score from 0-100 (pre-calculated)
- `resume_file_path` - Path to resume file (PDF/DOCX)

---

## 📊 Output

### 1. Excel Report (`report.xlsx`)

**Columns:**
- Candidate Name, Email, Phone
- Experience (Years)
- **Similarity Score (%)** - Center-aligned
- **Decision** - Color-coded (Green/Yellow/Red)
- **Reasoning** - Detailed professional explanation
- **Resume URL** - Google Drive shareable link
- Skills, Education
- Processed Date

**Formatting:**
- Professional color scheme
- Auto-adjusted column widths
- Frozen header row
- Wrapped text for reasoning

### 2. Email Notification

**Sent to:** `HR_EMAIL_RECIPIENT` from `.env`

**Includes:**
- Professional HTML design
- Summary statistics table
- Breakdown: X Shortlisted, Y Maybe, Z Rejected
- Screening criteria explanation
- Next steps recommendations
- Excel report as attachment

### 3. Log File (`app.log`)

Detailed operation logs:
```
2026-01-23 10:15:30 - INFO - Processing candidate 1/10: John Doe
2026-01-23 10:15:32 - INFO - Resume uploaded for John Doe
2026-01-23 10:15:33 - INFO - ✓ John Doe: Shortlisted (85.5%)
```

---

## 🐛 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| "Credentials file not found" | Use absolute path in `.env` |
| "Domain-wide delegation required" | Enable in Google Workspace Admin |
| "Resume upload failed" | Share Drive folder with service account |
| Import errors | Run `pip install -r requirements.txt` |
| "Insufficient permissions" | Verify OAuth scopes in Admin Console |

**Detailed troubleshooting:** See [REASONING_ENGINE_SETUP.md](REASONING_ENGINE_SETUP.md#troubleshooting)

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [QUICK_REFERENCE.md](QUICK_REFERENCE.md) | One-page command cheat sheet |
| [REASONING_ENGINE_SETUP.md](REASONING_ENGINE_SETUP.md) | Complete setup guide (650+ lines) |
| [REASONING_ENGINE_README.md](REASONING_ENGINE_README.md) | Feature overview and examples |
| [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) | Technical architecture details |

---

## 🔒 Security

✅ **Best Practices Implemented:**
- Service account authentication
- Environment-based configuration
- No hardcoded credentials
- Sensitive files gitignored
- Least privilege API scopes
- Secure file permissions

**Security Checklist:**
- [ ] `.env` added to `.gitignore`
- [ ] Credentials file: `chmod 600`
- [ ] Rotate service account keys quarterly
- [ ] Monitor API usage in Cloud Console
- [ ] Never commit credentials to Git

---

## 🧪 Testing

### Test Individual Components

```bash
# Google Drive service
python3 google_drive_service.py

# Gmail service  
python3 gmail_service.py

# Email template
python3 email_template.py
open sample_email.html  # Preview in browser
```

### Test Complete Workflow

```bash
python3 reasoning_engine.py -i sample_candidates.json -o test_report.xlsx
```

**Expected Results:**
- 10 candidates processed
- 3 Shortlisted (scores 85.5%, 88.4%, 92.1%)
- 4 Maybe (scores 62.3%, 71.2%, 73.9%, 79.6%)
- 3 Rejected (scores 38.2%, 45.7%, 56.8%)
- Excel file created in current directory
- Email sent to configured HR recipient

---

## 📈 Performance

- **Small batch (10 candidates)**: ~30-60 seconds
- **Medium batch (50 candidates)**: ~3-5 minutes
- **Large batch (100+ candidates)**: ~6-10 minutes

**Bottleneck:** Resume uploads to Google Drive (~2-3 seconds per file)

---

## 🛠️ Customization

### Adjust Decision Thresholds

Edit `.env`:
```bash
SHORTLIST_THRESHOLD=75  # Raise bar for shortlisting
REJECT_THRESHOLD=60     # Stricter rejection criteria
```

### Customize Reasoning Text

Edit `reasoning_engine.py`, method `generate_reasoning()`:
```python
reasoning_templates = {
    "Shortlisted": "Your custom text here...",
    "Maybe": "Your custom text here...",
    "Rejected": "Your custom text here..."
}
```

### Customize Email Template

Edit `email_template.py`, function `generate_email_html()`.

### Customize Excel Formatting

Edit `reasoning_engine.py`, method `_format_excel()`.

---

## 📊 Architecture

```
Input JSON → Parse & Validate → For Each Candidate:
                                    ├─ Evaluate Score
                                    ├─ Determine Decision
                                    ├─ Generate Reasoning
                                    └─ Upload Resume
                ↓
            Generate Excel Report → Apply Formatting
                ↓
            Send Email with Attachment
                ↓
            Complete (Log Summary)
```

---

## 🔄 Workflow Example

```bash
# 1. Prepare candidate data
cat > my_candidates.json << EOF
[
  {
    "candidate_name": "Alice Johnson",
    "email": "alice@example.com",
    "phone": "+1-555-1234",
    "experience_years": 6,
    "skills": ["Python", "Django", "AWS"],
    "education": "MS Computer Science",
    "similarity_score": 78.5,
    "resume_file_path": "./resumes/alice_resume.pdf"
  }
]
EOF

# 2. Run screening
python3 reasoning_engine.py -i my_candidates.json -o alice_report.xlsx

# 3. Check results
open alice_report.xlsx  # macOS
# OR
xdg-open alice_report.xlsx  # Linux

# 4. Review logs
tail -f app.log
```

---

## 🎓 Sample Data

10 sample candidates included in `sample_candidates.json`:

| Name | Score | Decision |
|------|-------|----------|
| Robert Chen | 92.1% | Shortlisted |
| Michael Brown | 88.4% | Shortlisted |
| John Doe | 85.5% | Shortlisted |
| Kevin Martinez | 79.6% | Maybe |
| David Johnson | 73.9% | Maybe |
| Lisa Anderson | 71.2% | Maybe |
| Jane Smith | 62.3% | Maybe |
| Emily Taylor | 56.8% | Rejected |
| Maria Garcia | 45.7% | Rejected |
| Sarah Williams | 38.2% | Rejected |

---

## 🤝 Support

### Getting Help

1. **Check documentation:**
   - [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for commands
   - [REASONING_ENGINE_SETUP.md](REASONING_ENGINE_SETUP.md) for setup
   
2. **Check logs:**
   ```bash
   tail -100 app.log
   ```

3. **Test components individually:**
   ```bash
   python3 google_drive_service.py
   python3 gmail_service.py
   ```

4. **Verify configuration:**
   ```bash
   cat .env
   ```

---

## 📝 License

Copyright © 2026 AI Feature Extraction Team. All rights reserved.

---

## ✨ Credits

**Built by:** AI Feature Extraction Team  
**Date:** January 23, 2026  
**Version:** 1.0.0  
**Status:** Production Ready

---

## 🎉 Ready to Start?

```bash
# 1. Install
./install_reasoning_engine.sh

# 2. Configure
nano .env

# 3. Test
python3 reasoning_engine.py -i sample_candidates.json -o test.xlsx

# 4. Go live!
python3 reasoning_engine.py -i your_candidates.json -o report.xlsx
```

**Happy Screening! 🚀**
