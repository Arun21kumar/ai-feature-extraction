# Reasoning Engine Quick Reference

## 🚀 One-Command Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your credentials

# Run
python reasoning_engine.py -i sample_candidates.json -o report.xlsx
```

---

## 📊 Decision Matrix

| Score Range | Decision | Action |
|------------|----------|---------|
| **≥ 69%** | ✅ Shortlisted | Schedule interview |
| **50-68%** | ⚠️ Maybe | Further review |
| **< 50%** | ❌ Rejected | Not suitable |

---

## ⚙️ Environment Variables (.env)

```bash
# Required
GOOGLE_CREDENTIALS_PATH=/path/to/service-account.json
GMAIL_SENDER_EMAIL=sender@company.com
HR_EMAIL_RECIPIENT=hr@company.com
DRIVE_FOLDER_ID=1ABcD2EfGh3IjKlMnOpQrStUv

# Optional (defaults shown)
SHORTLIST_THRESHOLD=69
REJECT_THRESHOLD=50
```

---

## 📁 Required Files

### Input JSON (`candidates.json`)
```json
[
  {
    "candidate_name": "John Doe",
    "email": "john@email.com",
    "phone": "+1-555-0101",
    "experience_years": 5,
    "skills": ["Python", "ML"],
    "education": "BS CS",
    "similarity_score": 85.5,
    "resume_file_path": "./resumes/john.pdf"
  }
]
```

### Output Excel (`report.xlsx`)
Auto-generated with:
- Contact info
- Similarity scores
- Decisions (color-coded)
- Reasoning
- Resume links

---

## 🔧 Commands

### Run Screening
```bash
python reasoning_engine.py --input candidates.json --output report.xlsx
```

### Test Components
```bash
# Test Drive
python google_drive_service.py

# Test Gmail
python gmail_service.py

# Preview Email
python email_template.py
open sample_email.html
```

### Help
```bash
python reasoning_engine.py --help
```

---

## 🐛 Troubleshooting

### ❌ "Credentials file not found"
```bash
# Use absolute path in .env
GOOGLE_CREDENTIALS_PATH=/Users/you/project/credentials.json
```

### ❌ "Domain-wide delegation required"
1. Enable in service account settings
2. Add scopes in Google Workspace Admin:
   - `https://www.googleapis.com/auth/gmail.send`
   - `https://www.googleapis.com/auth/drive.file`

### ❌ "Resume upload failed"
1. Share Drive folder with service account email
2. Grant "Editor" permissions
3. Verify DRIVE_FOLDER_ID is correct

### ❌ Import errors
```bash
pip install -r requirements.txt
```

---

## 📋 Google API Setup Checklist

- [ ] Create Google Cloud Project
- [ ] Enable Gmail API
- [ ] Enable Drive API
- [ ] Create Service Account
- [ ] Download JSON credentials
- [ ] Enable domain-wide delegation
- [ ] Add OAuth scopes in Workspace Admin
- [ ] Create Drive folder
- [ ] Share folder with service account
- [ ] Copy folder ID
- [ ] Configure .env file
- [ ] Test with `python google_drive_service.py`
- [ ] Test with `python gmail_service.py`

---

## 📊 Output Structure

```
.
├── report.xlsx              # Excel report (auto-generated)
├── app.log                  # Operation logs
└── resumes uploaded to Google Drive with shareable links
```

---

## 🔐 Security Checklist

- [ ] `.env` added to `.gitignore`
- [ ] Credentials file permissions: `chmod 600`
- [ ] Never commit `.env` or credentials
- [ ] Rotate service account keys regularly
- [ ] Monitor API usage in Cloud Console

---

## 📧 Email Preview

**Subject:** Candidate Screening Report - January 23, 2026

**Content:**
- Professional HTML template
- Summary: X Shortlisted, Y Maybe, Z Rejected
- Statistics table
- Excel attachment
- Next steps guidance

---

## 🎯 Key Features

✅ Automated decision-making
✅ Google Drive resume storage
✅ Professional Excel reports
✅ HTML email notifications
✅ Color-coded formatting
✅ Comprehensive logging
✅ Error handling
✅ Batch processing

---

## 📞 Support

1. Check `app.log` for errors
2. See [REASONING_ENGINE_SETUP.md](REASONING_ENGINE_SETUP.md) for detailed guide
3. Review troubleshooting section above
4. Test individual components

---

## 🔄 Typical Workflow

```
1. Prepare JSON with candidate data
   ↓
2. Configure .env file
   ↓
3. Run: python reasoning_engine.py -i candidates.json -o report.xlsx
   ↓
4. Engine processes candidates:
   - Evaluates similarity scores
   - Determines decisions
   - Uploads resumes to Drive
   - Generates Excel report
   ↓
5. Email sent to HR with report attached
   ↓
6. Review report and schedule interviews
```

---

## 💡 Pro Tips

- Use `sample_candidates.json` for testing
- Check `app.log` for detailed progress
- Preview email template before sending
- Test with small batches first
- Keep credentials secure
- Monitor Google API quotas

---

**For complete documentation, see [REASONING_ENGINE_SETUP.md](REASONING_ENGINE_SETUP.md)**
