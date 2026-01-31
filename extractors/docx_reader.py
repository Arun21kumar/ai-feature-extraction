"""
Reads text content from a DOCX file with robust fallbacks.
Order of attempt:
  1) unstructured.partition.auto (best for complex layouts)
  2) python-docx (reliable plain text)
  3) docx2python (last resort)
"""
import logging
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# Optional imports
try:
    from unstructured.partition.auto import partition as _unstructured_partition  # type: ignore
except Exception:
    _unstructured_partition = None

try:
    import docx as _python_docx  # python-docx
except Exception:
    _python_docx = None

try:
    from docx2python import docx2python as _docx2python  # type: ignore
except Exception:
    _docx2python = None


def _read_with_unstructured(file_path: str) -> Optional[str]:
    if not _unstructured_partition:
        return None
    try:
        logger.info(f"Extracting text from {file_path} using 'unstructured'.")
        elements = _unstructured_partition(filename=file_path)
        return "\n\n".join([str(el) for el in elements])
    except Exception as e:
        logger.warning(f"unstructured extraction failed: {e}")
        return None


def _read_with_python_docx(file_path: str) -> Optional[str]:
    if not _python_docx:
        return None
    try:
        logger.info(f"Extracting text from {file_path} using 'python-docx'.")
        doc = _python_docx.Document(file_path)
        paras = [p.text for p in doc.paragraphs if p.text and p.text.strip()]
        return "\n".join(paras)
    except Exception as e:
        logger.warning(f"python-docx extraction failed: {e}")
        return None


def _read_with_docx2python(file_path: str) -> Optional[str]:
    if not _docx2python:
        return None
    try:
        logger.info(f"Extracting text from {file_path} using 'docx2python'.")
        result = _docx2python(file_path)
        # Flatten nested structure to lines
        parts = []
        for doc in result.body:  # type: ignore[attr-defined]
            if isinstance(doc, list):
                for row in doc:
                    if isinstance(row, list):
                        for cell in row:
                            if isinstance(cell, list):
                                for para in cell:
                                    if isinstance(para, str) and para.strip():
                                        parts.append(para.strip())
                            elif isinstance(cell, str) and cell.strip():
                                parts.append(cell.strip())
                    elif isinstance(row, str) and row.strip():
                        parts.append(row.strip())
            elif isinstance(doc, str) and doc.strip():
                parts.append(doc.strip())
        # Fallback to text property if available
        if not parts and hasattr(result, "text"):
            return str(getattr(result, "text"))
        return "\n".join(parts)
    except Exception as e:
        logger.warning(f"docx2python extraction failed: {e}")
        return None


def read_docx(file_path: str) -> str:
    """
    Extract text from a DOCX file using robust fallbacks.

    Args:
        file_path: Absolute or relative path to a .docx file.

    Returns:
        Extracted plain text. Returns empty string if all methods fail.
    """
    p = Path(file_path)
    if not p.exists():
        logger.error(f"DOCX file not found: {file_path}")
        return ""

    # 1) unstructured
    text = _read_with_unstructured(file_path)
    if text:
        return text

    # 2) python-docx
    text = _read_with_python_docx(file_path)
    if text:
        return text

    # 3) docx2python
    text = _read_with_docx2python(file_path)
    if text:
        return text

    logger.error("Failed to extract text using all available methods.")
    return ""
