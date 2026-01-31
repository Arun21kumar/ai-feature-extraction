import os
import json
import hashlib
import logging
from pathlib import Path
from typing import Iterable, Union, Dict, Any

from sentence_transformers import SentenceTransformer


logger = logging.getLogger(__name__)


class VectorEmbeddingConversionPipeline:

    def __init__(self, model_name: str = "Qwen/Qwen3-Embedding-0.6B") -> None:
        self.model_name = model_name
        self._model = None

    def _load_model(self) -> SentenceTransformer:
        if self._model is None:
            logger.info(f"Loading embedding model: {self.model_name}")
            self._model = SentenceTransformer(self.model_name)
        return self._model

    @staticmethod
    def _sha256_str(s: str) -> str:
        return hashlib.sha256(s.encode("utf-8")).hexdigest()

    def _vector_output_dir_for(self, first_input: Union[str, Path]) -> Path:
        first = Path(first_input)
        # Place vector_output at project root alongside output/
        return (first.parent / "../vector_output").resolve()

    @staticmethod
    def _ensure_schema_keys(data: Dict[str, Any]) -> Dict[str, Any]:
        # Normalize to expected keys with defaults
        return {
            "document_type": str(data.get("document_type", "")),
            "summary": data.get("summary") or "",
            "experience_years": data.get("experience_years", None),
            "skills": list(data.get("skills", []) or []),
            "certifications": list(data.get("certifications", []) or []),
            "responsibilities": list(data.get("responsibilities", []) or []),
        }

    def _should_skip(self, out_path: Path, source_hash: str) -> bool:
        if not out_path.exists():
            return False
        try:
            with open(out_path, "r", encoding="utf-8") as f:
                existing = json.load(f)
            if (
                isinstance(existing, dict)
                and existing.get("embedding_model") == self.model_name
                and existing.get("source_hash") == source_hash
            ):
                logger.info(f"Up-to-date, skipping: {out_path.name}")
                return True
        except Exception:
            return False
        return False

    def _embed_texts(self, texts: list[str]) -> list[list[float]]:
        model = self._load_model()
        if not texts:
            return []
        vectors = model.encode(texts)
        # Convert to nested lists
        return [vec.tolist() for vec in vectors]

    def _embed_string(self, text: str) -> list[float]:
        model = self._load_model()
        vec = model.encode(text)
        return vec.tolist()

    def _integrity_check(self) -> None:
        """Sanity-check model by embedding two similar texts and asserting cosine > 0.7."""
        import numpy as np
        from numpy.linalg import norm

        a = "Senior Network Engineer focusing on Cisco and Palo Alto firewalls"
        b = "Experienced Network Engineer with Cisco routers and Palo Alto firewall expertise"
        va = self._embed_string(a)
        vb = self._embed_string(b)
        va = np.array(va)
        vb = np.array(vb)
        sim = float(np.dot(va, vb) / (norm(va) * norm(vb) + 1e-8))
        if sim < 0.70:
            raise RuntimeError(
                f"Embedding sanity check failed (cosine={sim:.3f}). Check model '{self.model_name}'."
            )
        logger.info(f"Embedding sanity OK (cosine={sim:.3f})")

    def convertJsontoVector(self, file_path_list: Iterable[Union[str, Path]]) -> list[Path]:
        """
        Converts feature-extracted JSONs to vector embeddings with consistent schema.
        - Strings are embedded directly
        - Lists are embedded item-by-item
        - Numeric values (experience_years) are preserved
        - Adds metadata: embedding_model, source_hash
        - Idempotent: skips if output exists with same hash & model
        Returns the written vector file paths.
        """
        file_paths = [Path(p) for p in file_path_list]
        if not file_paths:
            logger.warning("No files provided for vector conversion.")
            return []

        out_dir = self._vector_output_dir_for(file_paths[0])
        out_dir.mkdir(parents=True, exist_ok=True)

        # Ensure model loads and is sane
        self._load_model()
        try:
            self._integrity_check()
        except Exception as e:
            logger.warning(f"Embedding integrity check warning: {e}")

        written: list[Path] = []

        for in_path in file_paths:
            if not in_path.exists():
                logger.warning(f"File not found: {in_path}")
                continue

            try:
                raw = in_path.read_text(encoding="utf-8")
                src_hash = self._sha256_str(raw + "|" + self.model_name)
                out_file = in_path.name + ".vector.json"
                out_path = out_dir / out_file

                if self._should_skip(out_path, src_hash):
                    written.append(out_path)
                    continue

                data = json.loads(raw)
                data = self._ensure_schema_keys(data)

                vector_json: Dict[str, Any] = {
                    "embedding_model": self.model_name,
                    "source_hash": src_hash,
                    "document_type": data["document_type"],
                    # Keep numeric for rule-based logic
                    "experience_years": data["experience_years"],
                }

                # summary: single vector
                summary_text = data.get("summary") or ""
                vector_json["summary"] = self._embed_string(summary_text) if summary_text else []

                # lists: skills, certifications, responsibilities
                for field in ("skills", "certifications", "responsibilities"):
                    items = [s for s in (data.get(field) or []) if isinstance(s, str) and s.strip()]
                    vector_json[field] = self._embed_texts(items)

                # Write output
                out_path.write_text(json.dumps(vector_json, indent=2, ensure_ascii=False), encoding="utf-8")
                logger.info(f"Vectorized: {out_path.name}")
                written.append(out_path)

            except Exception as e:
                logger.error(f"Failed to vectorize {in_path.name}: {e}")
                continue

        return written
