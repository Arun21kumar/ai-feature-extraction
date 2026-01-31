"""
Local LLM-based feature extraction using Ollama.
Communicates with locally running Ollama models for semantic feature extraction.
"""
import json
import logging
import time
import re
from typing import Optional, Dict, Any
import requests

from models.schema import ExtractedFeatures


logger = logging.getLogger(__name__)


# A single, more intelligent, universal prompt
EXTRACTION_PROMPT_TEMPLATE = """You are an expert HR analyst and document parser. Your primary goal is to perform a comprehensive and context-aware analysis of the provided document text and extract its key features into a structured JSON format.

**Instructions:**

1.  **Holistic Analysis:** First, read the **entire document** to understand its purpose, structure, and context. Determine if it is a job description (JD) or a resume.
2.  **Context-Aware Extraction:** Based on your analysis, extract the following features with high accuracy. Pay close attention to the specific guidelines for JDs vs. resumes.
3.  **Strict JSON Output:** Return ONLY a single, valid JSON object adhering to the schema below. Do not include any explanatory text.

**JSON Schema:**
```json
{{
  "document_type": "jd | resume",
  "summary": "A detailed, verbatim summary of the role or professional profile.",
  "experience_years": null,
  "skills": [],
  "certifications": [],
  "responsibilities": []
}}
```

**Feature Extraction Guidelines:**

*   **`document_type`**: (string) Accurately label the document as either `"jd"` or `"resume"`.
*   **`summary`**: (string)
    *   For a **JD**: Extract the **entire, verbatim job summary or role overview section**. This should be the full paragraph that introduces the role.
    *   For a **Resume**: Extract the **entire, verbatim professional summary or objective section**.
*   **`experience_years`**: (float) This is critical.
    *   For a **JD**: Find the most relevant years of experience. If both a minimum and a preferred number are mentioned (e.g., "5+ years required, 8+ years preferred"), **you must use the preferred number (`8.0`)**. If only one number is mentioned, use that.
    *   For a **Resume**: Find the candidate's **total years of experience**, which is often mentioned in their summary.
*   **`skills`**: (list of strings)
    *   Thoroughly scan the entire document for all technical skills, tools, programming languages, and methodologies. Look under any relevant heading ("Skills," "Requirements," "Qualifications," etc.). Be comprehensive.
*   **`certifications`**: (list of strings)
    *   Extract all professional certifications mentioned (e.g., "CCNP," "AWS Certified," "PMP").
*   **`responsibilities`**: (list of strings)
    *   This is the most important field. You must be comprehensive.
    *   Scan the **entire document** from top to bottom.
    *   Extract **every** phrase that describes a job duty, task, or an expectation of what the person in the role will do.
    *   Look for action verbs. Examples: "design," "develop," "manage," "collaborate," "implement," "troubleshoot," "analyze," "lead," "maintain."
    *   Pay close attention to bulleted lists under any heading, including but not limited to: "Responsibilities," "What you'll do," "Day-to-day," "Tasks," "Requirements," or "Qualifications."
    *   If a phrase describes an action or a duty, you **must** include it, even if it's in the summary or a qualifications section.

**Document to Analyze:**
<<<TEXT_START>>>
{document_text}
<<<TEXT_END>>>

**Output (JSON only):**
"""

# JSON correction prompt for malformed outputs
JSON_CORRECTION_PROMPT = """The following text should be valid JSON but is malformed.
Fix it to be valid JSON. Output ONLY the corrected valid JSON.

Malformed JSON:
<<<JSON_START>>>
{malformed_json}
<<<JSON_END>>>

Output ONLY the corrected valid JSON."""


class OllamaExtractor:
    """
    Local LLM-based feature extractor using Ollama.

    Attributes:
        model: Name of the Ollama model to use
        base_url: Base URL for Ollama API
        timeout: Request timeout in seconds
        max_retries: Maximum number of retry attempts
    """

    def __init__(
        self,
        model: str = "llama3.1:8b",
        base_url: str = "http://localhost:11434",
        timeout: int = 120,
        max_retries: int = 3
    ):
        """
        Initialize the Ollama extractor.

        Args:
            model: Ollama model name (llama3.1:8b, mistral:7b-instruct, qwen2.5:7b)
            base_url: Ollama API base URL
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts for failed extractions
        """
        self.model = model
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.generate_url = f"{self.base_url}/api/generate"

    def check_connection(self) -> bool:
        """
        Check if Ollama is running and accessible.

        Returns:
            True if Ollama is accessible, False otherwise
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Cannot connect to Ollama at {self.base_url}: {e}")
            return False

    def _call_ollama(self, prompt: str, temperature: float = 0.1) -> Optional[str]:
        """
        Make a generation request to Ollama API.

        Args:
            prompt: The prompt to send to the model
            temperature: Sampling temperature (lower = more deterministic)

        Returns:
            Generated text or None if request fails
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "top_p": 0.9,
                "top_k": 40
            }
        }

        try:
            response = requests.post(
                self.generate_url,
                json=payload,
                timeout=self.timeout
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                return None

        except requests.exceptions.Timeout:
            logger.error(f"Ollama request timed out after {self.timeout} seconds")
            return None
        except Exception as e:
            logger.error(f"Error calling Ollama API: {e}")
            return None

    def _parse_json_response(self, response: str) -> Optional[Dict[str, Any]]:
        """
        Parse JSON from LLM response, handling common formatting issues.

        Args:
            response: Raw response from LLM

        Returns:
            Parsed JSON dict or None if parsing fails
        """
        # Try to extract JSON from markdown code blocks if present
        if "```json" in response:
            try:
                json_start = response.index("```json") + 7
                json_end = response.index("```", json_start)
                response = response[json_start:json_end].strip()
            except ValueError:
                pass
        elif "```" in response:
            try:
                json_start = response.index("```") + 3
                json_end = response.index("```", json_start)
                response = response[json_start:json_end].strip()
            except ValueError:
                pass

        # Clean common issues
        response = response.strip()

        # Try to parse
        try:
            data = json.loads(response)
            return data
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parsing failed: {e}")
            return None

    def _correct_json(self, malformed_json: str) -> Optional[Dict[str, Any]]:
        """
        Attempt to correct malformed JSON using the LLM.

        Args:
            malformed_json: Malformed JSON string

        Returns:
            Corrected JSON dict or None if correction fails
        """
        logger.info("Attempting to correct malformed JSON")

        correction_prompt = JSON_CORRECTION_PROMPT.format(malformed_json=malformed_json)
        response = self._call_ollama(correction_prompt, temperature=0.0)

        if response:
            return self._parse_json_response(response)

        return None

    @staticmethod
    def _extract_years_from_text(text: str) -> Optional[float]:
        """Best-effort numeric extraction of years from arbitrary text, e.g., '11yrs', '10+ years'."""
        if not text:
            return None
        # common patterns
        patterns = [
            r"(\d+\.?\d*)\s*\+?\s*(years|yrs|yr|y)",
            r"(\d+\.?\d*)\s*\+?\s*(?:years)?\s*experience",
            r"experience\s*(?:of|over|~|approx\.?|around)?\s*(\d+\.?\d*)"
        ]
        for pat in patterns:
            m = re.search(pat, text, flags=re.IGNORECASE)
            if m:
                try:
                    return float(m.group(1))
                except Exception:
                    continue
        # bare numbers followed by y/yrs
        m = re.search(r"(\d+\.?\d*)\s*(y|yrs)\b", text, flags=re.IGNORECASE)
        if m:
            try:
                return float(m.group(1))
            except Exception:
                pass
        return None

    @staticmethod
    def _detect_doc_type(document_text: str) -> str:
        """Heuristically detect if the document is a job description (jd) or a resume."""
        text = (document_text or "").lower()
        jd_signals = [
            "responsibilities", "requirements", "preferred qualifications",
            "job description", "job summary", "role", "position"
        ]
        resume_signals = [
            "experience", "work history", "summary", "education",
            "projects", "skills"  # common in resumes
        ]
        jd_score = sum(1 for s in jd_signals if s in text)
        resume_score = sum(1 for s in resume_signals if s in text)
        return "jd" if jd_score >= resume_score else "resume"

    @staticmethod
    def _extract_required_years(document_text: str) -> Optional[float]:
        """Extract explicit required years from JD text.
        Priority: Preferred Qualifications > other qualification sections > global text.
        Returns the minimal positive requirement to reflect 'minimum N+' requirement.
        """
        if not document_text:
            return None
        text = document_text

        def find_candidates(src: str) -> list[float]:
            vals: list[float] = []
            patterns = [
                r"(\d+\.?\d*)\s*\+\s*years\s+of\s+experience",
                r"(\d+\.?\d*)\s*\+?\s*years\s+of\s+experience",
                r"(\d+\.?\d*)\s*\+?\s*years\s+experience",
                r"(\d+\.?\d*)\s*\+?\s*yrs\s+experience",
                r"minimum\s+of\s+(\d+\.?\d*)\s*years",
                r"at\s+least\s+(\d+\.?\d*)\s*years",
                r"(\d+\.?\d*)\s*\+?\s*years\b"
            ]
            lower = src.lower()
            for pat in patterns:
                for m in re.finditer(pat, lower, flags=re.IGNORECASE):
                    try:
                        v = float(m.group(1))
                        if v > 0:
                            vals.append(v)
                    except Exception:
                        continue
            return vals

        # Prefer "Preferred Qualifications" section
        preferred_idx = text.lower().find("preferred qualifications")
        if preferred_idx != -1:
            preferred_chunk = text[preferred_idx: preferred_idx + 1200]
            cand = find_candidates(preferred_chunk)
            if cand:
                return min(cand)

        # Then search common qualification sections
        for header in ["Requirements", "Qualifications", "Must Have", "Basic Qualifications", "Job Requirements"]:
            idx = text.lower().find(header.lower())
            if idx != -1:
                chunk = text[idx: idx + 1200]
                cand = find_candidates(chunk)
                if cand:
                    return min(cand)

        # Fallback: search entire text
        global_cand = find_candidates(text)
        if global_cand:
            return min(global_cand)
        return None

    @staticmethod
    def _parse_stringified_dicts(items: list[str]) -> list[str]:
        """If experience items look like stringified dicts, keep a concise summary."""
        parsed = []
        for it in items:
            s = str(it).strip()
            if s.startswith("{") and "'}" in s or s.startswith("{'"):
                # Try to extract title/company fields for brevity
                title = re.search(r"'title':\s*'([^']+)'", s)
                company = re.search(r"'company':\s*'([^']+)'", s)
                if title or company:
                    summary = ", ".join([p for p in [
                        title.group(1) if title else None,
                        company.group(1) if company else None
                    ] if p])
                    parsed.append(summary or s)
                    continue
            parsed.append(s)
        return parsed

    def _to_string_item(self, item: Any) -> Optional[str]:
        """Convert arbitrary item to a concise string; handle dicts by compact json or key summary."""
        try:
            if item is None:
                return None
            if isinstance(item, str):
                s = item.strip()
                return s if s else None
            if isinstance(item, (int, float)):
                return str(item)
            if isinstance(item, dict):
                # try common keys
                keys = ["title", "company", "employer", "location", "name"]
                parts = []
                for k in keys:
                    v = item.get(k)
                    if isinstance(v, str) and v.strip():
                        parts.append(v.strip())
                if parts:
                    return ", ".join(parts)
                # fallback to compact json
                return json.dumps(item, separators=(",", ":"))
            # lists/tuples: join strings
            if isinstance(item, (list, tuple)):
                strs = [self._to_string_item(x) for x in item]
                strs = [s for s in strs if s]
                return "; ".join(strs) if strs else None
            # fallback
            s = str(item).strip()
            return s if s else None
        except Exception:
            return None

    def _validate_and_clean_data(self, data: Dict[str, Any], *, document_text: str) -> ExtractedFeatures:
        """
        Validate and clean extracted data to match the simplified schema.
        Also applies JD-specific fallback for preferred experience detection
        from raw document text when missing or ambiguous.
        """
        # Ensure all required fields exist with correct types
        cleaned: Dict[str, Any] = {
            "document_type": str(data.get("document_type", "")).strip(),
            "summary": str(data.get("summary", "")).strip(),
            "experience_years": None,
            "skills": [],
            "certifications": [],
            "responsibilities": []
        }

        # Fallback detection if model fails to set document_type
        if not cleaned["document_type"]:
            cleaned["document_type"] = self._detect_doc_type(document_text)

        # Handle experience_years
        exp_years = data.get("experience_years")
        if isinstance(exp_years, (int, float)):
            cleaned["experience_years"] = float(exp_years)
        elif isinstance(exp_years, str):
            # Use the robust numeric parsing for strings
            cleaned["experience_years"] = self._extract_years_from_text(exp_years)

        # JD-specific preferred years fallback from text if missing/low
        if cleaned["document_type"] == "jd":
            preferred = self._extract_required_years(document_text)
            if preferred:
                if cleaned["experience_years"] is None or cleaned["experience_years"] < preferred:
                    cleaned["experience_years"] = preferred

        # Clean and deduplicate list fields
        for field in ["skills", "certifications", "responsibilities"]:
            items = data.get(field, [])
            if isinstance(items, list):
                # Use a set for deduplication while preserving order
                seen = set()
                deduped_list = []
                for item in items:
                    s_item = str(item).strip()
                    if s_item and s_item.lower() not in seen:
                        seen.add(s_item.lower())
                        deduped_list.append(s_item)
                cleaned[field] = deduped_list

        return ExtractedFeatures.from_dict(cleaned)

    def extract_features(self, document_text: str) -> ExtractedFeatures:
        """
        Extracts structured features using a single, powerful, context-aware prompt.
        """
        if not self.check_connection():
            raise ConnectionError(
                f"Cannot connect to Ollama at {self.base_url}. "
                "Please ensure Ollama is running (e.g., 'ollama serve')"
            )

        # Use the single, universal prompt for extraction
        prompt = EXTRACTION_PROMPT_TEMPLATE.format(document_text=document_text)

        # Retry loop for the single extraction pass
        for attempt in range(1, self.max_retries + 1):
            logger.info(f"Extraction attempt {attempt}/{self.max_retries}")

            response = self._call_ollama(prompt)

            if not response:
                logger.warning(f"No response from LLM on attempt {attempt}")
                time.sleep(1)
                continue

            # Try to parse JSON
            data = self._parse_json_response(response)

            # If parsing failed, try to correct it
            if data is None and attempt < self.max_retries:
                logger.warning("JSON parsing failed, attempting correction.")
                data = self._correct_json(response)

            # If we have valid data, validate and return
            if data is not None:
                try:
                    features = self._validate_and_clean_data(data, document_text=document_text)
                    logger.info("Successfully extracted and validated features.")
                    return features
                except Exception as e:
                    logger.error(f"Data validation failed: {e}")
                    # Continue to retry if validation fails

            if attempt < self.max_retries:
                time.sleep(2)

        # All retries failed
        raise ValueError(
            f"Failed to extract valid features after {self.max_retries} attempts."
        )


def extract_features_from_text(
    text: str,
    model: str = "llama3.1:8b",
    ollama_url: str = "http://localhost:11434"
) -> ExtractedFeatures:
    """
    Convenience function to extract features from text.

    Args:
        text: Cleaned document text
        model: Ollama model name
        ollama_url: Ollama API URL

    Returns:
        ExtractedFeatures object
    """
    extractor = OllamaExtractor(model=model, base_url=ollama_url)
    return extractor.extract_features(text)
