"""
Main entry point for DOCX feature extraction pipeline.
Orchestrates the complete extraction process from DOCX to structured JSON.
"""
import logging
import sys
import json
from pathlib import Path
from typing import Optional, List
import nltk
import ssl
import os

from extractors.docx_reader import read_docx
from extractors.text_cleaning import clean_text
from llm.extractor import OllamaExtractor
from models.schema import ExtractedFeatures


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def ensure_nltk_data():
    """
    Checks for and downloads necessary NLTK data, handling SSL issues.
    This makes the script self-contained and robust.
    """
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context

    packages = ['punkt', 'averaged_perceptron_tagger']
    for package in packages:
        try:
            # Check if the package is available in the default download location
            nltk.data.find(f'tokenizers/{package}')
        except LookupError:
            logger.info(f"NLTK package '{package}' not found. Downloading...")
            nltk.download(package)
            logger.info(f"Finished downloading '{package}'.")


class FeatureExtractionPipeline:
    """
    Complete pipeline for extracting features from DOCX documents.
    """

    def __init__(
        self,
        model: str = "llama3.1:8b",
        ollama_url: str = "http://localhost:11434",
        verbose: bool = True
    ):
        """
        Initialize the extraction pipeline.

        Args:
            model: Ollama model to use.
            ollama_url: URL of the Ollama API.
            verbose: Whether to show detailed logs.
        """
        self.model = model
        self.ollama_url = ollama_url
        if not verbose:
            logging.getLogger().setLevel(logging.WARNING)

    def process_file(self, file_path: str) -> ExtractedFeatures:
        """
        Process a single DOCX file and extract features.
        A new extractor is created for each file to ensure statelessness.
        """
        logger.info(f"Processing file: {file_path}")

        # Create a new extractor for each file to prevent context leakage.
        extractor = OllamaExtractor(model=self.model, base_url=self.ollama_url)

        # Stage 1: Extract text from DOCX
        logger.info("Stage 1: Extracting text from DOCX")
        raw_text = read_docx(file_path)
        logger.info(f"Extracted {len(raw_text)} characters")

        # Stage 2: Clean and normalize text
        logger.info("Stage 2: Cleaning and normalizing text")
        cleaned_text = clean_text(raw_text)
        logger.info(f"Cleaned text: {len(cleaned_text)} characters")

        # Stage 3: Extract features using LLM
        logger.info(f"Stage 3: Extracting features using {self.model}")
        features = extractor.extract_features(cleaned_text)

        logger.info("Extraction complete!")
        return features

    def process_file_to_json(self, file_path: str, output_path: Optional[str] = None) -> dict:
        """
        Process a file and save/return results as JSON.

        Args:
            file_path: Path to input DOCX file
            output_path: Optional path to save JSON output

        Returns:
            Dictionary with extracted features
        """
        features = self.process_file(file_path)
        result = features.to_dict()

        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            logger.info(f"Results saved to: {output_path}")

        return result

    def process_directory(self, input_dir: str, output_dir: str) -> List[Path]:
        """Process all .docx files in a directory and save JSON outputs.

        Args:
            input_dir: Directory containing .docx files
            output_dir: Directory to write JSON outputs

        Returns:
            List of output file paths written
        """
        in_path = Path(input_dir)
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        if not in_path.exists() or not in_path.is_dir():
            raise FileNotFoundError(f"Input directory not found: {input_dir}")

        outputs: List[Path] = []
        # Ensure we only process valid, non-temporary docx files
        docx_files = [
            f for f in in_path.glob("*.docx")
            if f.is_file() and not f.name.startswith("~")
        ]

        if not docx_files:
            logger.warning(f"No valid .docx files found in {input_dir}")
            return outputs

        for doc in sorted(docx_files):
            try:
                stem = doc.stem.replace(" ", "_")
                # Create a friendly output name
                lower_name = stem.lower()
                if "jd" in lower_name or "job" in lower_name:
                    out_name = f"jd_{stem}.json"
                elif "resume" in lower_name or "cv" in lower_name:
                    out_name = f"resume_{stem}.json"
                else:
                    out_name = f"{stem}.json"

                out_file = out_path / out_name
                logger.info(f"\nProcessing: {doc} -> {out_file}")
                result = self.process_file_to_json(str(doc), str(out_file))
                outputs.append(out_file)

                # Print compact summary per file
                print("\n" + "="*60)
                print(f"EXTRACTION RESULTS - {doc.name}")
                print("="*60)
                print(json.dumps(result, indent=2, ensure_ascii=False))
                print("="*60)
            except Exception as e:
                logger.error(f"Failed to process file {doc.name}: {e}")
                # Continue to the next file
                continue

        return outputs


def main():
    """
    Command-line interface for the feature extraction pipeline.

    Usage:
        - No args: process all .docx files in sample-data and write outputs to output/
        - With args: python main.py <input_file.docx> [output_file.json]
    """
    # Ensure all necessary NLTK data is available before starting.
    ensure_nltk_data()

    import os
    model = os.environ.get("MODEL", "llama3.1:8b")

    try:
        pipeline = FeatureExtractionPipeline(model=model)
        output_dir = Path(__file__).parent / "output"

        if len(sys.argv) < 2:
            # Auto process all files from sample-data
            sample_dir = str(Path(__file__).parent / "sample-data")
            logger.info(f"No input arguments provided. Processing all .docx in: {sample_dir}")
            pipeline.process_directory(sample_dir, str(output_dir))
        else:
            # Process explicit file
            input_file = Path(sys.argv[1])

            # If output file is not specified, create one automatically in the output directory
            if len(sys.argv) > 2:
                output_file = Path(sys.argv[2])
            else:
                stem = input_file.stem.replace(" ", "_")
                output_file = output_dir / f"jd_{stem}.json"

            logger.info(f"\nProcessing: {input_file} -> {output_file}")
            result = pipeline.process_file_to_json(str(input_file), str(output_file))

            # Print results
            print("\n" + "="*60)
            print(f"EXTRACTION RESULTS - {input_file.name}")
            print("="*60)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            print("="*60)

    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except ConnectionError as e:
        print(f"Error: {e}")
        print("\nPlease ensure Ollama is running:")
        print("  ollama serve")
        print(f"\nAnd that the model is available:")
        print(f"  ollama pull {model}")
        sys.exit(1)
    except Exception as e:
        logger.exception("An error occurred during processing")
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
