"""
Example usage demonstrations for the DOCX feature extraction system.
"""
import json
from main import FeatureExtractionPipeline
from models.schema import ExtractedFeatures


def example_1_basic_usage():
    """Example 1: Basic usage - process a single file."""
    print("="*60)
    print("EXAMPLE 1: Basic Usage")
    print("="*60)

    # Initialize pipeline with default model (llama3.1:8b)
    pipeline = FeatureExtractionPipeline()

    # Process a resume
    try:
        features = pipeline.process_file("sample_resume.docx")

        print("\n✓ Extraction successful!")
        print(f"\nSummary: {features.summary}")
        print(f"\nTotal Experience (years): {features.years_of_experience}")
        print(f"\nSkills ({len(features.skills)}):")
        for skill in features.skills[:5]:  # Show first 5
            print(f"  - {skill}")

        print(f"\nExperience entries (showing up to 1): {len(features.experience)}")
        for exp in features.experience[:1]:  # Show first 1 per design
            print(f"  - {exp}")

    except FileNotFoundError:
        print("\n⚠ sample_resume.docx not found (this is just an example)")
    except ConnectionError:
        print("\n⚠ Ollama not running. Start it with: ollama serve")


def example_2_save_to_json():
    """Example 2: Process and save results to JSON file."""
    print("\n" + "="*60)
    print("EXAMPLE 2: Save to JSON")
    print("="*60)

    pipeline = FeatureExtractionPipeline(verbose=False)

    try:
        # Process and save to JSON
        result = pipeline.process_file_to_json(
            "job_description.docx",
            output_path="output/jd_features.json"
        )

        print("\n✓ Results saved to output/jd_features.json")
        print(f"\nYears of Experience: {result.get('years_of_experience')}")
        print(f"Extracted {len(result['skills'])} skills")
        print(f"Extracted {len(result['responsibilities'])} responsibilities")

    except FileNotFoundError:
        print("\n⚠ job_description.docx not found (this is just an example)")
    except ConnectionError:
        print("\n⚠ Ollama not running. Start it with: ollama serve")


def example_3_different_models():
    """Example 3: Try different LLM models."""
    print("\n" + "="*60)
    print("EXAMPLE 3: Different Models")
    print("="*60)

    models = [
        "llama3.1:8b",      # Balanced: accuracy + speed
        "mistral:7b-instruct",  # Fast
        "qwen2.5:7b"        # Excellent for structured data
    ]

    for model in models:
        print(f"\nUsing model: {model}")
        pipeline = FeatureExtractionPipeline(model=model, verbose=False)

        try:
            features = pipeline.process_file("sample_resume.docx")
            print(f"  ✓ Years of Experience: {features.years_of_experience}")
            print(f"  ✓ Extracted {len(features.skills)} skills")
        except FileNotFoundError:
            print("  ⚠ sample_resume.docx not found (this is just an example)")
            break
        except ConnectionError:
            print(f"  ⚠ Model {model} not available. Pull it with: ollama pull {model}")


def example_4_manual_pipeline():
    """Example 4: Manual step-by-step processing."""
    print("\n" + "="*60)
    print("EXAMPLE 4: Manual Pipeline")
    print("="*60)

    from extractors.docx_reader import read_docx
    from extractors.text_cleaning import clean_text
    from llm.extractor import OllamaExtractor

    try:
        # Step 1: Extract text
        print("\nStep 1: Extracting text from DOCX...")
        raw_text = read_docx("sample_resume.docx")
        print(f"  Extracted {len(raw_text)} characters")

        # Step 2: Clean text
        print("\nStep 2: Cleaning text...")
        cleaned_text = clean_text(raw_text)
        print(f"  Cleaned to {len(cleaned_text)} characters")

        # Step 3: Extract features
        print("\nStep 3: Extracting features with LLM...")
        extractor = OllamaExtractor(
            model="llama3.1:8b",
            timeout=120,
            max_retries=3
        )
        features = extractor.extract_features(cleaned_text)
        print(f"  ✓ Extracted features successfully")

        # Display results
        print("\nResults:")
        print(f"  Summary length: {len(features.summary)} characters")
        print(f"  Years of Experience: {features.years_of_experience}")
        print(f"  Skills: {len(features.skills)}")
        print(f"  Experience entries (<=1): {len(features.experience)}")
        print(f"  Responsibilities: {len(features.responsibilities)}")
        print(f"  Certifications: {len(features.certifications)}")

    except FileNotFoundError:
        print("\n⚠ sample_resume.docx not found (this is just an example)")
    except ConnectionError:
        print("\n⚠ Ollama not running. Start it with: ollama serve")


def example_5_batch_processing():
    """Example 5: Batch process multiple documents."""
    print("\n" + "="*60)
    print("EXAMPLE 5: Batch Processing")
    print("="*60)

    from pathlib import Path

    # List of documents to process
    documents = [
        "resume_1.docx",
        "resume_2.docx",
        "jd_senior_engineer.docx",
        "jd_data_scientist.docx"
    ]

    pipeline = FeatureExtractionPipeline(verbose=False)

    results = {}
    for doc in documents:
        print(f"\nProcessing: {doc}")
        try:
            features = pipeline.process_file(doc)
            results[doc] = features.to_dict()
            print(f"  ✓ Years of Experience: {features.years_of_experience}")
            print(f"  ✓ Success - {len(features.skills)} skills extracted")
        except FileNotFoundError:
            print(f"  ⚠ File not found (this is just an example)")
        except Exception as e:
            print(f"  ✗ Error: {e}")

    # Save batch results
    if results:
        output_path = Path("output/batch_results.json")
        output_path.parent.mkdir(exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n✓ Batch results saved to {output_path}")


def example_6_custom_configuration():
    """Example 6: Custom configuration and error handling."""
    print("\n" + "="*60)
    print("EXAMPLE 6: Custom Configuration")
    print("="*60)

    from llm.extractor import OllamaExtractor

    # Create extractor with custom settings
    extractor = OllamaExtractor(
        model="llama3.1:8b",
        base_url="http://localhost:11434",
        timeout=300,  # 5 minutes for large documents
        max_retries=5  # More retries for reliability
    )

    # Check connection first
    if extractor.check_connection():
        print("✓ Ollama is running and accessible")
    else:
        print("✗ Cannot connect to Ollama")
        print("  Start it with: ollama serve")
        return

    try:
        # Process with custom configuration
        from extractors.docx_reader import read_docx
        from extractors.text_cleaning import clean_text

        text = clean_text(read_docx("large_document.docx"))
        features = extractor.extract_features(text)

        print(f"\n✓ Successfully processed large document")
        print(f"  Extracted {sum(len(getattr(features, field)) for field in ['experience', 'responsibilities', 'skills', 'certifications'])} total items")

    except FileNotFoundError:
        print("\n⚠ large_document.docx not found (this is just an example)")
    except Exception as e:
        print(f"\n✗ Error: {e}")


def example_7_validation_demo():
    """Example 7: Demonstrate data validation and schema."""
    print("\n" + "="*60)
    print("EXAMPLE 7: Data Validation")
    print("="*60)

    # Create features manually
    features = ExtractedFeatures(
        summary="Senior Software Engineer with 10+ years experience",
        experience=[
            "Google, Senior Engineer, 2018-2023",
            "Microsoft, Software Engineer, 2013-2018"
        ],
        responsibilities=[
            "Led development of microservices architecture",
            "Mentored junior developers",
            "Designed scalable systems"
        ],
        skills=[
            "Python", "Go", "Kubernetes", "AWS",
            "System Design", "Leadership"
        ],
        certifications=[
            "AWS Certified Solutions Architect",
            "Kubernetes Administrator (CKA)"
        ]
    )

    print("\n✓ Created validated ExtractedFeatures object")

    # Convert to dict
    data_dict = features.to_dict()
    print("\nAs dictionary:")
    print(json.dumps(data_dict, indent=2))

    # Reconstruct from dict
    reconstructed = ExtractedFeatures.from_dict(data_dict)
    print("\n✓ Successfully reconstructed from dictionary")
    print(f"  Skills count: {len(reconstructed.skills)}")


def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("DOCX FEATURE EXTRACTION - EXAMPLE USAGE")
    print("="*60)
    print("\nThis script demonstrates various usage patterns.")
    print("Note: Most examples use sample files that may not exist.")
    print("They are meant to show the API usage patterns.\n")

    # Run examples
    example_1_basic_usage()
    example_2_save_to_json()
    example_3_different_models()
    example_4_manual_pipeline()
    example_5_batch_processing()
    example_6_custom_configuration()
    example_7_validation_demo()

    print("\n" + "="*60)
    print("All examples completed!")
    print("="*60)
    print("\nQuick Start:")
    print("  1. Start Ollama: ollama serve")
    print("  2. Pull a model: ollama pull llama3.1:8b")
    print("  3. Run: python main.py your_resume.docx")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
