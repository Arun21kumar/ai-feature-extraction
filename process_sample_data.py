"""
Process DOCX files in sample-data/ using the feature extraction pipeline.
- JD file: any filename containing 'Sr Network Engineer'
- Resume file: any filename starting with 'Rajesh Kummara'

Outputs JSON files to output/:
- output/jd_Sr_Network_Engineer.json
- output/resume_Rajesh_Kummara.json
"""
import sys
import json
import logging
from pathlib import Path
from typing import Optional, Tuple

from main import FeatureExtractionPipeline

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SAMPLE_DIR = Path('sample-data')
OUTPUT_DIR = Path('output')


def find_files() -> Tuple[Optional[Path], Optional[Path]]:
    """Find JD and Resume files in sample-data by filename patterns."""
    if not SAMPLE_DIR.exists():
        raise FileNotFoundError(f"Sample directory not found: {SAMPLE_DIR}")

    jd_file: Optional[Path] = None
    resume_file: Optional[Path] = None

    for path in SAMPLE_DIR.glob('*.docx*'):
        name = path.name.lower()
        # JD: contains 'Sr Network Engineer'
        if 'sr network engineer' in name:
            jd_file = path
        # Resume: starts with 'Rajesh Kummara'
        if name.startswith('rajesh kummara'):
            resume_file = path

    return jd_file, resume_file


def process_and_save(pipeline: FeatureExtractionPipeline, file_path: Path, kind: str) -> Path:
    """Process a file and save JSON under output/. Returns output path."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = 'Sr_Network_Engineer' if kind == 'jd' else 'Rajesh_Kummara'
    output_path = OUTPUT_DIR / f"{kind}_{safe_name}.json"

    logger.info(f"Processing {kind.upper()} file: {file_path}")
    result = pipeline.process_file_to_json(str(file_path), str(output_path))
    logger.info(f"Saved {kind} results to: {output_path}")
    return output_path


def main():
    # Optional model override via env MODEL
    import os
    model = os.environ.get('MODEL', 'llama3.1:8b')
    pipeline = FeatureExtractionPipeline(model=model, verbose=True)

    jd_file, resume_file = find_files()

    if not jd_file:
        print("✗ JD file not found in sample-data (looking for name containing 'Sr Network Engineer')")
    if not resume_file:
        print("✗ Resume file not found in sample-data (looking for name starting with 'Rajesh Kummara')")

    processed = []
    try:
        if jd_file:
            processed.append(process_and_save(pipeline, jd_file, 'jd'))
        if resume_file:
            processed.append(process_and_save(pipeline, resume_file, 'resume'))
    except ConnectionError as e:
        print(f"\nError: {e}")
        print("\nPlease ensure Ollama is running:")
        print("  ollama serve")
        print(f"\nAnd that the model is available:")
        print(f"  ollama pull {model}")
        sys.exit(1)
    except Exception as e:
        logger.exception("An error occurred during processing")
        print(f"\nError: {e}")
        sys.exit(1)

    if processed:
        print("\n✓ Processing complete. Outputs:")
        for p in processed:
            print(f"  - {p}")
    else:
        print("\n⚠ Nothing processed. Ensure files exist and match patterns.")


if __name__ == '__main__':
    main()

