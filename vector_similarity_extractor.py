import json
import numpy as np
from numpy.linalg import norm


class VectorSimilarityExtractor:
    def compute_similarity(self, vector1, vector2):
        print("Computing similarity between:", vector1, "and", vector2)

        # Parse JSON if passed as string
        if isinstance(vector1, str):
            vector1 = json.loads(vector1)
        if isinstance(vector2, str):
            vector2 = json.loads(vector2)

        emb1 = vector1.get("embeddings", {})
        emb2 = vector2.get("embeddings", {})

        similarity_report = {}

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
                similarity = (
                    np.dot(vec1, vec2) / (norm(vec1) * norm(vec2) + 1e-8)
                ) * 100
                similarity_report[key] = float(similarity)
                continue

            # ====================================
            # LIST FIELDS (coverage-aware cosine)
            # ====================================
            sims = []

            for vec1 in v1:
                vec1 = np.array(vec1)
                vec1 = np.squeeze(vec1)
                # Best semantic match for each JD item
                max_sim = max(
                    np.dot(vec1, np.squeeze(np.array(vec2))) / (norm(vec1) * norm(np.squeeze(np.array(vec2))) + 1e-8)
                    for vec2 in v2
                )
                sims.append(max_sim)

            # IMPORTANT CHANGE:
            # Mean of best matches instead of mean of all comparisons
            similarity = float(np.mean(sims)) * 100
            similarity_report[key] = similarity

        print(
            "Cosine similarity report (coverage-aware, percent):",
            json.dumps(similarity_report, indent=2)
        )
        return similarity_report
 