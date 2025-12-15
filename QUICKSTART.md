# Quick Reference Guide

## Installation (60 seconds)

```bash
# 1. Clone/navigate to project
cd jd-feature-extraction

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Install Ollama (if not installed)
# macOS/Linux:
curl -fsSL https://ollama.com/install.sh | sh

# 4. Start Ollama
ollama serve  # Keep this running in a separate terminal

# 5. Pull a model (choose one)
ollama pull llama3.1:8b        # Recommended (4.7GB)
ollama pull mistral:7b-instruct # Faster (4.1GB)
ollama pull qwen2.5:7b         # Best for structured (4.4GB)
```

## Basic Usage

### Command Line

```bash
# Process a resume
python main.py resume.docx

# Save to JSON file
python main.py resume.docx output.json

# Use different model
MODEL=mistral:7b-instruct python main.py resume.docx
```

### Python API

```python
from main import FeatureExtractionPipeline

# Initialize
pipeline = FeatureExtractionPipeline()

# Extract features
features = pipeline.process_file("resume.docx")

# Access results
print(features.summary)
print(features.skills)
print(features.experience)

# Save as JSON
pipeline.process_file_to_json("resume.docx", "output.json")
```

## Common Patterns

### Batch Processing

```python
from main import FeatureExtractionPipeline
from pathlib import Path

pipeline = FeatureExtractionPipeline(verbose=False)

for docx_file in Path("resumes/").glob("*.docx"):
    output = f"output/{docx_file.stem}.json"
    try:
        pipeline.process_file_to_json(str(docx_file), output)
        print(f"✓ {docx_file.name}")
    except Exception as e:
        print(f"✗ {docx_file.name}: {e}")
```

### Custom Configuration

```python
from llm.extractor import OllamaExtractor
from extractors import read_docx, clean_text

# Custom extractor
extractor = OllamaExtractor(
    model="qwen2.5:7b",
    timeout=300,  # 5 minutes
    max_retries=5
)

# Process
text = clean_text(read_docx("document.docx"))
features = extractor.extract_features(text)
```

### Error Handling

```python
from main import FeatureExtractionPipeline

pipeline = FeatureExtractionPipeline()

try:
    features = pipeline.process_file("resume.docx")
except FileNotFoundError:
    print("File not found")
except ConnectionError:
    print("Ollama not running")
except ValueError as e:
    print(f"Extraction failed: {e}")
```

## Output Schema

```json
{
  "summary": "Professional summary or overview",
  "experience": [
    "Company Name, Position, Dates",
    "Another company, Role, Duration"
  ],
  "responsibilities": [
    "Key responsibility or achievement",
    "Another important duty"
  ],
  "skills": [
    "Python",
    "Machine Learning",
    "Leadership"
  ],
  "certifications": [
    "AWS Certified Solutions Architect",
    "PMP Certification"
  ]
}
```

## Model Comparison

| Model | Size | Speed | Accuracy | Best For |
|-------|------|-------|----------|----------|
| llama3.1:8b | 4.7GB | Medium | ★★★★★ | General use (default) |
| mistral:7b-instruct | 4.1GB | Fast | ★★★★☆ | Speed-critical |
| qwen2.5:7b | 4.4GB | Medium | ★★★★★ | Structured extraction |

## Command Cheat Sheet

```bash
# Ollama Management
ollama serve                    # Start Ollama server
ollama list                     # List installed models
ollama pull llama3.1:8b        # Download model
ollama rm llama3.1:8b          # Remove model

# Project Commands
python main.py resume.docx              # Extract features
python test_pipeline.py                 # Run tests
python example_usage.py                 # View examples
bash setup.sh                           # Run setup script

# Environment Variables
export MODEL=mistral:7b-instruct        # Set model
export OLLAMA_HOST=http://localhost:11434  # Set Ollama URL
```

## Troubleshooting Quick Fixes

### "Cannot connect to Ollama"
```bash
# Start Ollama
ollama serve
```

### "Model not found"
```bash
# Pull the model
ollama pull llama3.1:8b
```

### "Request timeout"
```python
# Increase timeout
pipeline.extractor.timeout = 300
```

### "Poor extraction quality"
```python
# Try Qwen model
pipeline = FeatureExtractionPipeline(model="qwen2.5:7b")
```

### Check Ollama Status
```bash
curl http://localhost:11434/api/tags
```

## Testing

```bash
# Run all tests
python test_pipeline.py

# Test specific component
python -c "from extractors import clean_text; print(clean_text('test'))"

# Check imports
python -c "from main import FeatureExtractionPipeline; print('OK')"
```

## File Locations

```
Input:  Any .docx file
Output: Specified JSON file or console
Logs:   Console output (adjust with logging module)
Models: ~/.ollama/models/ (Ollama managed)
```

## Performance Tips

1. **Use GPU**: Ollama automatically uses GPU if available
2. **Batch Process**: Process multiple files in sequence
3. **Lower Temperature**: More deterministic results
4. **Choose Right Model**: Speed vs accuracy tradeoff
5. **Text Length**: Shorter text = faster processing

## Development

```bash
# Install dev dependencies
pip install -r requirements.txt

# Run tests
python test_pipeline.py

# Check code
python -m py_compile main.py

# Format code (if using black)
black .
```

## Integration Examples

### FastAPI Server
```python
from fastapi import FastAPI, UploadFile
from main import FeatureExtractionPipeline

app = FastAPI()
pipeline = FeatureExtractionPipeline()

@app.post("/extract")
async def extract(file: UploadFile):
    with open(f"/tmp/{file.filename}", "wb") as f:
        f.write(await file.read())
    features = pipeline.process_file(f"/tmp/{file.filename}")
    return features.to_dict()
```

### Flask Server
```python
from flask import Flask, request, jsonify
from main import FeatureExtractionPipeline

app = Flask(__name__)
pipeline = FeatureExtractionPipeline()

@app.route('/extract', methods=['POST'])
def extract():
    file = request.files['file']
    path = f"/tmp/{file.filename}"
    file.save(path)
    features = pipeline.process_file(path)
    return jsonify(features.to_dict())
```

### Celery Task
```python
from celery import Celery
from main import FeatureExtractionPipeline

app = Celery('tasks')
pipeline = FeatureExtractionPipeline()

@app.task
def extract_features(file_path):
    features = pipeline.process_file(file_path)
    return features.to_dict()
```

## Resources

- **Ollama**: https://ollama.com
- **Models**: https://ollama.com/library
- **Documentation**: See README.md and ARCHITECTURE.md
- **Examples**: See example_usage.py

## Support

1. Check README.md for detailed documentation
2. Run test_pipeline.py for diagnostics
3. Review example_usage.py for patterns
4. Check ARCHITECTURE.md for technical details

## Quick Debug

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Test Ollama connection
from llm.extractor import OllamaExtractor
extractor = OllamaExtractor()
print("Connected:", extractor.check_connection())

# Test text extraction
from extractors import read_docx, clean_text
text = read_docx("test.docx")
print(f"Extracted {len(text)} chars")
cleaned = clean_text(text)
print(f"Cleaned to {len(cleaned)} chars")
```

## Version Info

- Python: 3.10+
- Ollama: Latest stable
- Core libraries: See requirements.txt

---

**Need help?** Check the full documentation in README.md and ARCHITECTURE.md

