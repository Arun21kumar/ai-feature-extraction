"""Extractors package for document reading and text processing."""
from .docx_reader import read_docx
from .text_cleaning import clean_text

__all__ = ["read_docx", "clean_text"]

