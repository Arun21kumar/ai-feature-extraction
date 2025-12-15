"""
Text cleaning and normalization utilities.
Prepares extracted text for LLM processing.
"""
import re
import unicodedata
from typing import List


def remove_duplicate_newlines(text: str) -> str:
    """
    Remove excessive newlines while preserving paragraph structure.

    Args:
        text: Input text with potential duplicate newlines

    Returns:
        Text with normalized newlines (max 2 consecutive)
    """
    # Replace 3+ newlines with 2
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text


def normalize_bullet_symbols(text: str) -> str:
    """
    Normalize various bullet point symbols to a standard dash.

    Args:
        text: Input text with various bullet symbols

    Returns:
        Text with normalized bullet points
    """
    # Common bullet symbols
    bullet_symbols = [
        '•', '●', '○', '◦', '▪', '▫', '■', '□',
        '◆', '◇', '★', '☆', '►', '▸', '⦿', '⦾',
        '➢', '➤', '→', '⇒', '✓', '✔', '–', '—'
    ]

    for symbol in bullet_symbols:
        # Replace bullet at start of line
        text = re.sub(f'^{re.escape(symbol)}\\s*', '- ', text, flags=re.MULTILINE)
        # Replace bullet after whitespace
        text = re.sub(f'\\s{re.escape(symbol)}\\s+', ' - ', text)

    return text


def join_broken_sentences(text: str) -> str:
    """
    Join sentences that were broken across lines inappropriately.

    Args:
        text: Input text with potentially broken sentences

    Returns:
        Text with sentences properly joined
    """
    # Join lines that don't end with sentence terminators
    lines = text.split('\n')
    joined_lines = []

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if not line:
            joined_lines.append('')
            i += 1
            continue

        # Check if line ends with sentence terminator or colon
        ends_with_terminator = line[-1] in '.!?:;' if line else False

        # If doesn't end with terminator and next line exists and doesn't start with bullet/dash
        if not ends_with_terminator and i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            if next_line and not next_line.startswith(('-', '•', '●', '○')):
                # Join with space
                joined_lines.append(line + ' ' + next_line)
                i += 2
                continue

        joined_lines.append(line)
        i += 1

    return '\n'.join(joined_lines)


def flatten_table_text(text: str) -> str:
    """
    Flatten table-like text structures for better readability.

    Args:
        text: Input text that may contain table structures

    Returns:
        Flattened text
    """
    # Replace tab characters with spaces
    text = text.replace('\t', ' ')

    # Replace multiple spaces with single space (but preserve line breaks)
    lines = text.split('\n')
    cleaned_lines = [re.sub(r' {2,}', ' ', line) for line in lines]

    return '\n'.join(cleaned_lines)


def strip_weird_unicode(text: str) -> str:
    """
    Remove or normalize problematic unicode characters.

    Args:
        text: Input text with potential unicode issues

    Returns:
        Text with normalized unicode characters
    """
    # Normalize unicode to composed form (NFC)
    text = unicodedata.normalize('NFC', text)

    # Replace common problematic characters
    replacements = {
        '\u200b': '',  # Zero-width space
        '\u200c': '',  # Zero-width non-joiner
        '\u200d': '',  # Zero-width joiner
        '\ufeff': '',  # Zero-width no-break space (BOM)
        '\xa0': ' ',   # Non-breaking space
        '\u2019': "'",  # Right single quotation mark
        '\u2018': "'",  # Left single quotation mark
        '\u201c': '"',  # Left double quotation mark
        '\u201d': '"',  # Right double quotation mark
        '\u2013': '-',  # En dash
        '\u2014': '-',  # Em dash
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Remove any remaining control characters except newlines and tabs
    text = ''.join(char for char in text if unicodedata.category(char)[0] != 'C' or char in '\n\t\r')

    return text


def clean_text(text: str) -> str:
    """
    Apply all cleaning operations to prepare text for LLM processing.

    This is the main entry point for text normalization.

    Args:
        text: Raw extracted text from document

    Returns:
        Cleaned and normalized text ready for LLM processing
    """
    # Apply all cleaning steps in sequence
    text = strip_weird_unicode(text)
    text = normalize_bullet_symbols(text)
    text = flatten_table_text(text)
    text = join_broken_sentences(text)
    text = remove_duplicate_newlines(text)

    # Final cleanup: strip excessive whitespace
    text = text.strip()

    return text

