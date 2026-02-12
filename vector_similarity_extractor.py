import json
import numpy as np
from numpy.linalg import norm


class VectorSimilarityExtractor:
    def compute_similarity(self, vector1, vector2):
        print("Computing similarity between passed vectors.")

        # Parse JSON if passed as string
        if isinstance(vector1, str):
            vector1 = json.loads(vector1)
        if isinstance(vector2, str):
            vector2 = json.loads(vector2)

        emb1 = vector1.get("embeddings", {})
        emb2 = vector2.get("embeddings", {})

        similarity_report = {}
        weighted_score = 0.0
        weights = {
            "summary": 0.25,
            "skills": 0.25,
            "responsibilities": 0.25,
            "certifications": 0.15,
            "experience": 0.10,
        }

        for key in ["summary", "skills", "responsibilities", "certifications"]:
            v1 = emb1.get(key, [])
            v2 = emb2.get(key, [])

            if not v1 or not v2:
                similarity_report[key] = 0.0
                continue

            # ======================
            # SUMMARY (single vector)
            # ======================
            if key == "summary":
                vec1 = np.array(v1)
                vec2 = np.array(v2)
                # Flatten or squeeze to 1D if needed
                vec1 = np.squeeze(vec1)
                vec2 = np.squeeze(vec2)
                similarity = float(
                    np.dot(vec1, vec2) / (norm(vec1) * norm(vec2) + 1e-8)
                ) * 100
                similarity_report[key] = similarity
            else:
                # ====================================
                # LIST FIELDS (coverage-aware cosine)
                # ====================================
                sims = []

                for vec1_item in v1:
                    vec1_item = np.array(vec1_item)
                    vec1_item = np.squeeze(vec1_item)
                    # Best semantic match for each JD item
                    max_sim = max(
                        float(
                            np.dot(vec1_item, np.squeeze(np.array(vec2_item))) / (norm(vec1_item) * norm(np.squeeze(np.array(vec2_item))) + 1e-8)
                        )
                        for vec2_item in v2
                    )
                    sims.append(max_sim)

                # IMPORTANT CHANGE:
                # Mean of best matches instead of mean of all comparisons
                similarity = float(np.mean(sims)) * 100
                similarity_report[key] = similarity

        # Experience rule-based logic
        exp_jd = vector1.get("experience_years", None)
        exp_resume = vector2.get("experience_years", None)
        exp_score = 0.0
        if exp_jd is not None and exp_resume is not None:
            try:
                exp_jd = float(exp_jd)
                exp_resume = float(exp_resume)
                if exp_resume >= exp_jd:
                    exp_score = 100.0
                else:
                    exp_score = max(0.0, (exp_resume / exp_jd) * 100)
            except Exception:
                exp_score = 0.0
        similarity_report["experience"] = exp_score

        # Weighted score breakdown
        weighted_score = sum(similarity_report[k] * weights.get(k, 0) for k in similarity_report)
        similarity_report["weighted_score"] = weighted_score

        print(
            "Cosine similarity report (coverage-aware, percent):",
            json.dumps(similarity_report, indent=2)
        )

        # Diagnostic assertions
        if similarity_report["summary"] < 65.0:
            print("WARNING: Summary similarity < 0.65 for aligned roles. Possible anomaly.")
        if exp_score >= 100.0 and weighted_score < 70.0:
            print("WARNING: Experience matches but final score < 70. Logic error suspected.")

        return similarity_report

