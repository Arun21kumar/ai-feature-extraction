# DOCX Feature Extraction System

A complete, cost-free, local, high-accuracy feature extraction system for DOCX resumes and job descriptions using local LLMs via Ollama.

## Features

- **100% Free & Local**: No paid APIs, all processing happens locally
- **Semantic Extraction**: Extracts features based on meaning, not section headings
- **High Accuracy**: Uses state-of-the-art local LLMs (LLaMA 3.1, Mistral, Qwen)
- **Robust DOCX Parsing**: Multi-layered extraction with fallback mechanisms
- **Structured JSON Output**: Validated, deterministic JSON schema
- **Production Ready**: Complete error handling, logging, and retry logic

### Extracted Features

- **Summary**: Professional overview or summary
- **Experience**: Work experience entries or company background
- **Responsibilities**: Key duties, responsibilities, or job requirements
- **Skills**: Technical and soft skills (explicitly or implicitly mentioned)
- **Certifications**: Professional certifications, licenses, qualifications

## Architecture

```
├── extractors/
│   ├── docx_reader.py      # DOCX text extraction (docx2python + python-docx)
│   └── text_cleaning.py    # Text normalization utilities
├── llm/
│   └── extractor.py        # Local LLM integration via Ollama
├── models/
│   └── schema.py           # Pydantic data models
├── main.py                 # Main pipeline orchestration
└── requirements.txt        # Dependencies
```

## Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Ollama

**macOS/Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Or visit**: https://ollama.com/download

### 3. Start Ollama Server

```bash
ollama serve
```

### 4. Pull a Local Model

Choose one of these free local models:

```bash
# LLaMA 3.1 8B (recommended - best balance)
ollama pull llama3.1:8b

# Mistral 7B Instruct (faster, good quality)
ollama pull mistral:7b-instruct

# Qwen 2.5 7B (excellent for structured extraction)
ollama pull qwen2.5:7b
```

## Usage

### Command Line

**Basic usage (prints to console):**
```bash
python main.py input_resume.docx
```

**Save to JSON file:**
```bash
python main.py input_resume.docx output.json
```

**Use different model:**
```bash
MODEL=mistral:7b-instruct python main.py resume.docx output.json
```

### Python API

```python
from main import FeatureExtractionPipeline

# Initialize pipeline
pipeline = FeatureExtractionPipeline(
    model="llama3.1:8b",
    ollama_url="http://localhost:11434",
    verbose=True
)

# Extract features from DOCX
features = pipeline.process_file("resume.docx")

# Access extracted data
print(f"Summary: {features.summary}")
print(f"Skills: {features.skills}")
print(f"Experience: {features.experience}")

# Save as JSON
result_dict = pipeline.process_file_to_json(
    "resume.docx",
    output_path="output.json"
)
```

### Advanced Usage

```python
from extractors.docx_reader import read_docx
from extractors.text_cleaning import clean_text
from llm.extractor import OllamaExtractor

# Step-by-step processing
raw_text = read_docx("document.docx")
cleaned_text = clean_text(raw_text)

extractor = OllamaExtractor(
    model="qwen2.5:7b",
    timeout=180,
    max_retries=3
)

features = extractor.extract_features(cleaned_text)
```

## Output Format

The system produces validated JSON with this exact schema:

```json
{
  "summary": "Professional summary or overview of the candidate/position",
  "experience": [
    "Software Engineer at Google, 2020-2023",
    "Data Analyst at Microsoft, 2018-2020"
  ],
  "responsibilities": [
    "Designed and implemented scalable microservices",
    "Led team of 5 engineers",
    "Reduced system latency by 40%"
  ],
  "skills": [
    "Python",
    "Machine Learning",
    "AWS",
    "Docker",
    "Team Leadership"
  ],
  "certifications": [
    "AWS Certified Solutions Architect",
    "PMP Certification"
  ]
}
```

## How It Works

### 1. DOCX Extraction
- Primary: `docx2python` (preserves structure, handles tables)
- Fallback: `python-docx` (reliable extraction)
- Handles complex formatting, tables, headers/footers

### 2. Text Normalization
- Removes duplicate newlines
- Normalizes bullet symbols (•, ●, ○, ▪, etc. → -)
- Joins broken sentences
- Flattens table text
- Strips problematic unicode characters
- Preserves semantic structure

### 3. LLM Extraction
- Sends cleaned text to local Ollama model
- Uses carefully crafted prompt for structured output
- Enforces JSON schema compliance
- Handles semantic detection (ignores headings)
- Extracts implicit information

### 4. Validation & Retry
- Validates JSON structure
- Auto-corrects malformed JSON
- Retries on failure (up to 3 attempts)
- Ensures all fields match schema
- Cleans and normalizes list items

## Models Comparison

| Model | Size | Speed | Accuracy | Best For |
|-------|------|-------|----------|----------|
| **llama3.1:8b** | 4.7GB | Medium | Excellent | General purpose (recommended) |
| **mistral:7b-instruct** | 4.1GB | Fast | Very Good | Speed-critical applications |
| **qwen2.5:7b** | 4.4GB | Medium | Excellent | Structured data extraction |

## Troubleshooting

### "Cannot connect to Ollama"
```bash
# Ensure Ollama is running
ollama serve

# Check if it's accessible
curl http://localhost:11434/api/tags
```

### "Model not found"
```bash
# Pull the model first
ollama pull llama3.1:8b
```

### "Extraction timeout"
```python
# Increase timeout for large documents
pipeline = FeatureExtractionPipeline(model="llama3.1:8b")
pipeline.extractor.timeout = 300  # 5 minutes
```

### Poor extraction quality
- Try a different model (Qwen 2.5 is excellent for structured extraction)
- Check if document text is properly extracted (enable verbose mode)
- Ensure document is well-formatted

## Performance

- **Small documents (1-2 pages)**: 10-30 seconds
- **Medium documents (3-5 pages)**: 30-60 seconds
- **Large documents (5+ pages)**: 60-120 seconds

*Times vary by model and hardware. GPU acceleration significantly improves speed.*

## Requirements

- Python 3.10+
- Ollama (local LLM server)
- 8GB+ RAM (16GB recommended for larger models)
- 5GB+ disk space (for models)

## License

MIT License - Free for personal and commercial use.

## Contributing

This is a production-ready system. Contributions welcome for:
- Additional text cleaning utilities
- Support for more document formats (PDF, TXT)
- Enhanced error handling
- Performance optimizations
- Additional validation rules

## Support

For issues:
1. Check Ollama is running: `ollama serve`
2. Verify model is available: `ollama list`
3. Enable verbose logging for debugging
4. Check document is valid DOCX format

