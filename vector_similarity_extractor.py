import os
import json
import numpy as np
from numpy.linalg import norm


class VectorSimilarityExtractor:
    """
    Production-grade JD-centric similarity scorer with diagnostics.
    Handles multi-chunk embeddings correctly and logs details for debugging.
    """

    # -------------------------------------------------
    # Vector utilities
    # -------------------------------------------------
    @staticmethod
    def normalize_vector(vec):
        """
        Normalizes embeddings into a single 1-D vector.

        Cases handled:
        - [float, float, ...]               -> unchanged
        - [[float...], [float...], ...]     -> mean pooled
        """
        arr = np.array(vec)

        if arr.ndim == 1:
            return arr

        if arr.ndim == 2:
            # Mean-pool multi-chunk embeddings
            return np.mean(arr, axis=0)

        raise ValueError("Invalid vector shape encountered")

    @staticmethod
    def cosine(a, b):
        return float(np.dot(a, b) / (norm(a) * norm(b) + 1e-8))

    @staticmethod
    def _shape(x):
        arr = np.array(x, dtype=float)
        return arr.shape

    @staticmethod
    def _similarity_matrix(A, B):
        # A: list of vectors, B: list of vectors (each can be item or list -> normalize)
        A_norm = [VectorSimilarityExtractor.normalize_vector(a) for a in A]
        B_norm = [VectorSimilarityExtractor.normalize_vector(b) for b in B]
        if not A_norm or not B_norm:
            return np.zeros((len(A_norm), len(B_norm)))
        A_mat = np.stack(A_norm, axis=0)
        B_mat = np.stack(B_norm, axis=0)
        # Normalize rows
        A_mat = A_mat / (np.linalg.norm(A_mat, axis=1, keepdims=True) + 1e-8)
        B_mat = B_mat / (np.linalg.norm(B_mat, axis=1, keepdims=True) + 1e-8)
        return A_mat @ B_mat.T

    @staticmethod
    def coverage_score(jd_list, res_list, floor=0.0):
        """
        For each JD vector, find best semantic match in resume vectors.
        Applies a floor to prevent over-penalizing senior candidates.
        """
        scores = []

        for jd_vec in jd_list:
            jd_vec = VectorSimilarityExtractor.normalize_vector(jd_vec)
            best = 0.0

            for res_vec in res_list:
                res_vec = VectorSimilarityExtractor.normalize_vector(res_vec)
                sim = VectorSimilarityExtractor.cosine(jd_vec, res_vec)
                best = max(best, sim)

            scores.append(max(best, floor))

        return float(np.mean(scores)) if scores else 0.0

    # -------------------------------------------------
    # Main similarity computation
    # -------------------------------------------------
    def compute_similarity(self, jd_vector, resume_vector):
        debug = bool(os.environ.get("DEBUG_SIM") or os.environ.get("SIM_DEBUG"))

        if isinstance(jd_vector, str):
            jd_vector = json.loads(jd_vector)
        if isinstance(resume_vector, str):
            resume_vector = json.loads(resume_vector)

        # Optional: enforce same embedding model
        jd_model = jd_vector.get("embedding_model")
        res_model = resume_vector.get("embedding_model")
        if jd_model and res_model and jd_model != res_model:
            # Mismatch warning; cosine may be meaningless
            if debug:
                print(f"[WARN] Embedding model mismatch: JD={jd_model} Resume={res_model}")

        component_scores = {}

        # -------------------------------------------------
        # EXPERIENCE (RULE-BASED)
        # -------------------------------------------------
        jd_exp = jd_vector.get("experience_years")
        res_exp = resume_vector.get("experience_years")

        if isinstance(jd_exp, (int, float)) and isinstance(res_exp, (int, float)):
            component_scores["experience"] = (
                1.0 if res_exp >= jd_exp else res_exp / jd_exp
            )
        else:
            component_scores["experience"] = 0.0

        # -------------------------------------------------
        # SUMMARY (MEAN-POOLED SEMANTIC MATCH)
        # -------------------------------------------------
        jd_sum = jd_vector.get("summary", [])
        res_sum = resume_vector.get("summary", [])

        if jd_sum and res_sum:
            jd_sum_vec = self.normalize_vector(jd_sum)
            res_sum_vec = self.normalize_vector(res_sum)
            component_scores["summary"] = self.cosine(jd_sum_vec, res_sum_vec)
            if debug:
                print(f"[DBG] summary shapes: JD={self._shape(jd_sum)} RES={self._shape(res_sum)}")
                print(f"[DBG] summary cosine: {component_scores['summary']:.4f}")
        else:
            component_scores["summary"] = 0.0
            if debug:
                print("[DBG] summary missing for one/both docs")

        # -------------------------------------------------
        # RESPONSIBILITIES (STRONG SIGNAL)
        # -------------------------------------------------
        jd_resp = jd_vector.get("responsibilities", [])
        res_resp = resume_vector.get("responsibilities", [])

        if jd_resp and res_resp:
            if debug:
                S = self._similarity_matrix(jd_resp, res_resp)
                top3 = []
                for i, row in enumerate(S):
                    # indices of top 3 matches
                    idx = np.argsort(-row)[:3]
                    top3.append([(int(j), float(row[j])) for j in idx])
                print(f"[DBG] responsibilities JD-items={len(jd_resp)} RES-items={len(res_resp)}")
                # Show first 5 jd items top-3
                for i, triples in enumerate(top3[:5]):
                    pretty = ", ".join([f"res#{j}:{s:.3f}" for j, s in triples])
                    print(f"  JD_RESP[{i}] top3 -> {pretty}")
            component_scores["responsibilities"] = (
                self.coverage_score(jd_resp, res_resp, floor=0.60)
            )
        else:
            component_scores["responsibilities"] = 0.0
            if debug:
                print("[DBG] responsibilities missing for one/both docs")

        # -------------------------------------------------
        # SKILLS (VENDOR-BIAS SAFE)
        # -------------------------------------------------
        jd_skills = jd_vector.get("skills", [])
        res_skills = resume_vector.get("skills", [])

        if jd_skills and res_skills:
            if debug:
                S = self._similarity_matrix(jd_skills, res_skills)
                top3 = []
                for i, row in enumerate(S):
                    idx = np.argsort(-row)[:3]
                    top3.append([(int(j), float(row[j])) for j in idx])
                print(f"[DBG] skills JD-items={len(jd_skills)} RES-items={len(res_skills)}")
                for i, triples in enumerate(top3[:5]):
                    pretty = ", ".join([f"res#{j}:{s:.3f}" for j, s in triples])
                    print(f"  JD_SKILL[{i}] top3 -> {pretty}")
            component_scores["skills"] = (
                self.coverage_score(jd_skills, res_skills, floor=0.55)
            )
        else:
            component_scores["skills"] = 0.0
            if debug:
                print("[DBG] skills missing for one/both docs")

        # -------------------------------------------------
        # CERTIFICATIONS (SOFT MATCH)
        # -------------------------------------------------
        jd_certs = jd_vector.get("certifications", [])
        res_certs = resume_vector.get("certifications", [])

        if jd_certs and res_certs:
            matched = 0
            for jd_vec in jd_certs:
                jd_vec = self.normalize_vector(jd_vec)
                if any(
                    self.cosine(jd_vec, self.normalize_vector(res_vec)) > 0.75
                    for res_vec in res_certs
                ):
                    matched += 1
            component_scores["certifications"] = matched / len(jd_certs)
        else:
            # Neutral: absence should not hard-penalize
            component_scores["certifications"] = 0.5

        # -------------------------------------------------
        # FINAL WEIGHTED SCORE (HIRING REALISM)
        # -------------------------------------------------
        final_score = (
            0.30 * component_scores["summary"] +
            0.30 * component_scores["skills"] +
            0.25 * component_scores["responsibilities"] +
            0.15 * component_scores["experience"]
        )

        if debug:
            print("[DBG] SCORE BREAKDOWN:")
            for k, v in component_scores.items():
                print(f"  {k:16s} -> {v*100:6.2f}%")
            print(f"  FINAL             -> {final_score*100:6.2f}%")

            # Anomaly flags
            if component_scores.get("experience", 0) >= 1.0 and final_score < 0.70:
                print("[FLAG] Experience meets/exceeds JD but overall score < 70: inspect skills/responsibilities")
            if component_scores.get("summary", 0) < 0.65 and (jd_model and res_model and jd_model == res_model):
                print("[FLAG] Low summary similarity; verify document parsing and section extraction")

        return {
            "component_scores": {
                k: round(v * 100, 2) for k, v in component_scores.items()
            },
            "final_score": round(final_score * 100, 2)
        }
