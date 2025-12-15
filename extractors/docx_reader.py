"""
Reads text content from a DOCX file using the `unstructured` library for robustness.
"""
import logging
from typing import Optional
from pathlib import Path

# Import partition from unstructured, with a fallback for import errors
try:
    from unstructured.partition.auto import partition
except ImportError:
    partition = None

logger = logging.getLogger(__name__)

def read_docx(file_path: str) -> str:
    """
    Extracts text from a DOCX file using the unstructured library.

    This approach is highly robust and can handle complex layouts, tables,
    and other elements that simpler libraries might miss.

    Args:
        file_path: The absolute path to the .docx file.

    Returns:
        The extracted text content as a single string.
        Returns an empty string if `unstructured` is not installed or an error occurs.
    """
    if not partition:
        logger.error(
            "The 'unstructured' library is not installed. "
            "Please install it with: pip install unstructured"
        )
        return ""

    try:
        logger.info(f"Extracting text from {file_path} using 'unstructured'.")
        elements = partition(filename=file_path)
        return "\n\n".join([str(el) for el in elements])
    except Exception as e:
        logger.error(f"An error occurred while reading {file_path} with unstructured: {e}")
        return ""
