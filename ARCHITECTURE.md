# Project Structure

```
jd-feature-extraction/
│
├── README.md                   # Comprehensive project documentation
├── requirements.txt            # Python dependencies
├── .gitignore                 # Git ignore rules
├── setup.sh                   # Setup and installation script
│
├── main.py                    # Main entry point and CLI
├── example_usage.py           # Usage examples and demonstrations
├── test_pipeline.py           # Test suite
│
├── models/                    # Data models and schemas
│   ├── __init__.py
│   └── schema.py              # Pydantic models for extracted features
│
├── extractors/                # Document extraction and text processing
│   ├── __init__.py
│   ├── docx_reader.py         # DOCX text extraction (dual-method)
│   └── text_cleaning.py       # Text normalization utilities
│
└── llm/                       # LLM integration
    ├── __init__.py
    └── extractor.py           # Ollama-based feature extraction
```

## Module Overview

### `models/schema.py`
- **Purpose**: Define data structures for extracted features
- **Key Class**: `ExtractedFeatures` (Pydantic model)
- **Features**:
  - Type validation
  - JSON serialization/deserialization
  - Default value handling

### `extractors/docx_reader.py`
- **Purpose**: Extract text from DOCX files
- **Strategy**: Primary + fallback approach
  - Primary: `docx2python` (better structure preservation)
  - Fallback: `python-docx` (more reliable parsing)
- **Key Functions**:
  - `read_docx()` - Main entry point
  - `extract_text_with_docx2python()` - Primary method
  - `extract_text_with_python_docx()` - Fallback method

### `extractors/text_cleaning.py`
- **Purpose**: Normalize and clean extracted text
- **Operations**:
  - Remove duplicate newlines
  - Normalize bullet symbols (•, ●, ○ → -)
  - Join broken sentences
  - Flatten table text
  - Strip problematic unicode
- **Key Function**: `clean_text()` - Applies all cleaning operations

### `llm/extractor.py`
- **Purpose**: Extract structured features using local LLM
- **Key Class**: `OllamaExtractor`
- **Features**:
  - Communicates with Ollama API via HTTP
  - Enforces structured JSON output
  - Automatic retry with exponential backoff
  - JSON validation and correction
  - Semantic extraction (heading-independent)
- **Supported Models**:
  - LLaMA 3.1 8B (recommended)
  - Mistral 7B Instruct
  - Qwen 2.5 7B

### `main.py`
- **Purpose**: Main pipeline orchestration and CLI
- **Key Class**: `FeatureExtractionPipeline`
- **Pipeline Stages**:
  1. DOCX text extraction
  2. Text cleaning and normalization
  3. LLM-based feature extraction
  4. JSON validation and output
- **CLI Usage**:
  ```bash
  python main.py input.docx [output.json]
  ```

### `test_pipeline.py`
- **Purpose**: Comprehensive test suite
- **Test Coverage**:
  - Text cleaning functions
  - Schema validation
  - Ollama connection
  - JSON parsing and validation
  - Integration tests

### `example_usage.py`
- **Purpose**: Demonstrate various usage patterns
- **Examples**:
  - Basic usage
  - Save to JSON
  - Different models
  - Manual pipeline
  - Batch processing
  - Custom configuration
  - Data validation

## Data Flow

```
DOCX File
    ↓
[docx_reader.py]
    ↓
Raw Text
    ↓
[text_cleaning.py]
    ↓
Cleaned Text
    ↓
[llm/extractor.py] ← Ollama API
    ↓
Raw JSON Response
    ↓
[Validation & Cleaning]
    ↓
ExtractedFeatures (Pydantic)
    ↓
JSON Output
```

## Key Design Decisions

### 1. Dual DOCX Extraction
**Why**: Different libraries handle different DOCX formats better
- `docx2python`: Better for complex structures, tables
- `python-docx`: More reliable for simple documents
- Fallback ensures maximum compatibility

### 2. Comprehensive Text Cleaning
**Why**: LLMs perform better with clean, normalized text
- Removes extraction artifacts
- Normalizes formatting
- Preserves semantic structure

### 3. Local LLM via Ollama
**Why**: Zero-cost, privacy-preserving, production-ready
- No API costs
- Data stays local
- Production-grade inference
- Easy model switching

### 4. Structured Output Enforcement
**Why**: Ensures consistent, parseable results
- Prompt engineering for JSON
- Validation and retry logic
- Auto-correction for malformed JSON
- Pydantic for type safety

### 5. Semantic Extraction
**Why**: More robust than heading-based parsing
- Works with any document format
- Handles non-standard layouts
- Infers implicit information
- Language model understanding

## Error Handling Strategy

### 1. Connection Errors
- Check Ollama availability before processing
- Clear error messages with setup instructions
- Graceful degradation

### 2. Extraction Failures
- Retry logic (up to 3 attempts)
- JSON correction prompt
- Validation and cleaning
- Detailed logging

### 3. File Errors
- File existence validation
- Format verification (.docx)
- Clear error messages

## Performance Considerations

### Speed
- Small docs (1-2 pages): 10-30 seconds
- Medium docs (3-5 pages): 30-60 seconds
- Large docs (5+ pages): 60-120 seconds

### Optimization Opportunities
- Lower temperature for more deterministic output
- Batch processing for multiple documents
- Model selection based on speed/accuracy tradeoff
- GPU acceleration (if available)

### Memory Usage
- Model loaded once by Ollama
- Streaming not required for document processing
- Memory scales with document size

## Extension Points

### Adding New Document Formats
1. Create new reader in `extractors/`
2. Follow same interface as `docx_reader.py`
3. Add to pipeline in `main.py`

### Adding New Features
1. Update `models/schema.py`
2. Modify extraction prompt in `llm/extractor.py`
3. Update validation logic

### Using Different LLMs
1. Implement new extractor class
2. Follow `OllamaExtractor` interface
3. Swap in pipeline

### Custom Text Processing
1. Add functions to `extractors/text_cleaning.py`
2. Call in `clean_text()` pipeline
3. Unit test in `test_pipeline.py`

## Testing Strategy

### Unit Tests
- Individual component testing
- Mock data where appropriate
- No external dependencies required

### Integration Tests
- End-to-end pipeline testing
- Requires Ollama running
- Uses sample documents

### Validation Tests
- Schema validation
- JSON parsing
- Data cleaning

## Dependencies

### Required
- `docx2python>=2.0.0` - Primary DOCX extraction
- `python-docx>=0.8.11` - Fallback DOCX extraction
- `requests>=2.31.0` - HTTP client for Ollama API
- `pydantic>=2.0.0` - Data validation and schemas

### External
- **Ollama** - Local LLM server
  - Installation: https://ollama.com/download
  - Start: `ollama serve`
  - Models: `ollama pull llama3.1:8b`

## Configuration

### Environment Variables
- `MODEL` - Ollama model name (default: llama3.1:8b)

### Runtime Configuration
```python
pipeline = FeatureExtractionPipeline(
    model="llama3.1:8b",           # Model selection
    ollama_url="http://localhost:11434",  # Ollama URL
    verbose=True                    # Logging verbosity
)

# Extractor configuration
pipeline.extractor.timeout = 180    # Request timeout
pipeline.extractor.max_retries = 5  # Retry attempts
```

## Best Practices

### 1. Document Preparation
- Use well-formatted DOCX files
- Avoid scanned images (OCR not included)
- Clear structure helps (but not required)

### 2. Model Selection
- **LLaMA 3.1 8B**: Best balance
- **Mistral 7B**: Faster processing
- **Qwen 2.5 7B**: Better structured extraction

### 3. Error Handling
- Always check Ollama connection first
- Enable verbose logging for debugging
- Review extraction results for accuracy

### 4. Performance
- Batch process multiple documents
- Use appropriate timeout values
- Consider GPU acceleration

## Troubleshooting

### Common Issues

**"Cannot connect to Ollama"**
- Start Ollama: `ollama serve`
- Check URL: `http://localhost:11434`

**"Model not found"**
- Pull model: `ollama pull llama3.1:8b`
- List models: `ollama list`

**"Extraction timeout"**
- Increase timeout: `pipeline.extractor.timeout = 300`
- Check document size
- Try faster model

**"Poor extraction quality"**
- Try different model (Qwen 2.5 for structured data)
- Check text cleaning output
- Verify document quality

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

### Potential Improvements
1. PDF support with `pdfplumber` or `pypdf`
2. OCR for scanned documents with `tesseract`
3. Multi-document comparison features
4. Custom field extraction
5. Export to multiple formats (CSV, XML)
6. Web interface with FastAPI
7. Asynchronous processing
8. Result caching

### Community Contributions
- Additional text cleaning utilities
- Support for more LLM backends (llama.cpp, vLLM)
- Enhanced validation rules
- Performance optimizations
- More comprehensive test coverage

## License

MIT License - Free for personal and commercial use.

## Support

For issues and questions:
1. Check README.md
2. Review example_usage.py
3. Run test_pipeline.py for diagnostics
4. Check Ollama documentation

