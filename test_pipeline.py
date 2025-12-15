"""
Test suite for the feature extraction pipeline.
Tests individual components and the complete pipeline.
"""
import sys
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_text_cleaning():
    """Test text cleaning utilities."""
    print("\n" + "="*60)
    print("TEST 1: Text Cleaning")
    print("="*60)

    from extractors.text_cleaning import (
        remove_duplicate_newlines,
        normalize_bullet_symbols,
        strip_weird_unicode,
        clean_text
    )

    # Test duplicate newlines
    text = "Hello\n\n\n\nWorld"
    result = remove_duplicate_newlines(text)
    assert "\n\n\n" not in result
    print("✓ remove_duplicate_newlines works")

    # Test bullet normalization
    text = "• Item 1\n● Item 2\n○ Item 3"
    result = normalize_bullet_symbols(text)
    assert result.count("-") >= 3
    print("✓ normalize_bullet_symbols works")

    # Test unicode cleaning
    text = "Hello\u200bWorld\xa0Test"
    result = strip_weird_unicode(text)
    assert "\u200b" not in result
    print("✓ strip_weird_unicode works")

    # Test complete cleaning
    text = "• Test\n\n\n\nBullet\u200bPoint"
    result = clean_text(text)
    assert len(result) > 0
    print("✓ clean_text works")

    print("\n✅ All text cleaning tests passed!")
    return True


def test_schema():
    """Test data schema and validation."""
    print("\n" + "="*60)
    print("TEST 2: Schema Validation")
    print("="*60)

    from models.schema import ExtractedFeatures

    # Create instance
    features = ExtractedFeatures(
        summary="Test summary",
        years_of_experience=10.5,
        experience=["Experience 1", "Experience 2"],
        responsibilities=["Responsibility 1"],
        skills=["Python", "Java", "Go"],
        certifications=["AWS Cert"]
    )

    assert features.summary == "Test summary"
    assert features.years_of_experience == 10.5
    assert len(features.skills) == 3
    print("✓ Schema creation works")

    # Test to_dict
    data = features.to_dict()
    assert isinstance(data, dict)
    assert "skills" in data
    assert data["years_of_experience"] == 10.5
    print("✓ to_dict works")

    # Test from_dict
    reconstructed = ExtractedFeatures.from_dict(data)
    assert reconstructed.summary == features.summary
    assert reconstructed.years_of_experience == features.years_of_experience
    assert len(reconstructed.skills) == len(features.skills)
    print("✓ from_dict works")

    print("\n✅ All schema tests passed!")
    return True


def test_ollama_connection():
    """Test connection to Ollama."""
    print("\n" + "="*60)
    print("TEST 3: Ollama Connection")
    print("="*60)

    from llm.extractor import OllamaExtractor

    extractor = OllamaExtractor()

    if extractor.check_connection():
        print("✓ Ollama is running and accessible")
        print(f"  URL: {extractor.base_url}")
        print(f"  Model: {extractor.model}")
        print("\n✅ Ollama connection test passed!")
        return True
    else:
        print("✗ Cannot connect to Ollama")
        print("\n⚠️  Ollama is not running. To start:")
        print("  1. Install: https://ollama.com/download")
        print("  2. Start: ollama serve")
        print("  3. Pull model: ollama pull llama3.1:8b")
        return False


def test_json_validation():
    """Test JSON parsing and validation."""
    print("\n" + "="*60)
    print("TEST 4: JSON Validation")
    print("="*60)

    from llm.extractor import OllamaExtractor
    import json

    extractor = OllamaExtractor()

    # Test valid JSON
    valid_json = json.dumps({
        "summary": "Test",
        "years_of_experience": 7,
        "experience": ["Exp 1"],
        "responsibilities": ["Resp 1"],
        "skills": ["Skill 1"],
        "certifications": []
    })

    result = extractor._parse_json_response(valid_json)
    assert result is not None
    print("✓ Valid JSON parsing works")

    # Test JSON in markdown
    markdown_json = f"```json\n{valid_json}\n```"
    result = extractor._parse_json_response(markdown_json)
    assert result is not None
    print("✓ Markdown JSON extraction works")

    # Test validation and cleaning
    data = {
        "summary": "Test",
        "years_of_experience": "10+ years",
        "experience": "Single experience",  # Wrong type
        "skills": ["", "Python", "", "Java"],  # Empty strings
        "certifications": None
    }

    features = extractor._validate_and_clean_data(data)
    assert features.years_of_experience is not None and features.years_of_experience >= 10
    assert len(features.experience) == 1  # Converted string to list
    assert len(features.skills) == 2  # Removed empty strings
    assert len(features.certifications) == 0  # Handled None
    print("✓ Data validation and cleaning works")

    print("\n✅ All JSON validation tests passed!")
    return True


def test_integration():
    """Test complete integration pipeline."""
    print("\n" + "="*60)
    print("TEST 5: Integration Test")
    print("="*60)

    from main import FeatureExtractionPipeline

    # Test pipeline initialization
    pipeline = FeatureExtractionPipeline(verbose=False)

    assert pipeline.model == "llama3.1:8b"
    assert pipeline.ollama_url == "http://localhost:11434"
    print("✓ Pipeline initialization works")

    print("\n✅ Integration test passed!")
    return True


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*70)
    print(" "*20 + "FEATURE EXTRACTION TEST SUITE")
    print("="*70)

    tests = [
        ("Text Cleaning", test_text_cleaning),
        ("Schema Validation", test_schema),
        ("Ollama Connection", test_ollama_connection),
        ("JSON Validation", test_json_validation),
        ("Integration", test_integration),
    ]

    passed = 0
    failed = 0
    skipped = 0

    for name, test_func in tests:
        try:
            result = test_func()
            if result is False:
                skipped += 1
            else:
                passed += 1
        except AssertionError as e:
            print(f"\n✗ Test failed: {e}")
            failed += 1
        except Exception as e:
            print(f"\n✗ Test error: {e}")
            failed += 1

    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"✅ Passed:  {passed}")
    print(f"⚠️  Skipped: {skipped}")
    print(f"✗ Failed:  {failed}")
    print("="*70)

    if failed > 0:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        return False
    elif skipped > 0:
        print("\n⚠️  Some tests were skipped (Ollama not running).")
        print("To run all tests:")
        print("  1. Start Ollama: ollama serve")
        print("  2. Pull a model: ollama pull llama3.1:8b")
        print("  3. Run tests again: python test_pipeline.py")
        return True
    else:
        print("\n🎉 All tests passed!")
        return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
