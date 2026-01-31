#!/usr/bin/env python3
"""
CLI tool to check JD–Resume similarity
Usage:
  python3 check_similarity.py <jd_vector_file> <resume_vector_file>
"""

import sys
import json
from vector_similarity_extractor import VectorSimilarityExtractor


def check_similarity(jd_path, resume_path):

    try:
        with open(jd_path, "r") as f:
            jd = json.load(f)
        with open(resume_path, "r") as f:
            resume = json.load(f)
    except Exception as e:
        print(f"Error loading files: {e}")
        return

    extractor = VectorSimilarityExtractor()
    similarity = extractor.compute_similarity(jd, resume)

    component_scores = similarity["component_scores"]
    final_score = similarity["final_score"]

    print("\n" + "=" * 70)
    print("JD-CENTRIC SIMILARITY REPORT")
    print("=" * 70)
    print(f"\nJD Experience Required : {jd.get('experience_years')} years")
    print(f"Resume Experience     : {resume.get('experience_years')} years")

    print("\n" + "-" * 70)
    print("FEATURE SCORES:")
    print("-" * 70)

    for feature, score in component_scores.items():
        bar_len = int(score / 2.5)
        bar = "█" * bar_len + "░" * (40 - bar_len)
        status = "✓ MEETS" if score >= 70 else "⚠ PARTIAL" if score >= 50 else "✗ BELOW"
        print(f"  {status:10s} {feature:20s}: {score:6.2f}% {bar}")

    print("-" * 70)
    print(f"  OVERALL MATCH: {final_score:6.2f}%")

    if final_score >= 80:
        decision = "EXCELLENT MATCH – Proceed to interview ✓"
    elif final_score >= 65:
        decision = "GOOD MATCH – Meets most requirements ✓"
    elif final_score >= 50:
        decision = "MODERATE MATCH – Review carefully ⚠"
    else:
        decision = "WEAK MATCH – Significant gaps ✗"

    print(f"  DECISION: {decision}")
    print("=" * 70)

    if component_scores.get("experience") == 100.0:
        print("\n✓ Experience meets/exceeds JD requirement")
    else:
        print("\n✗ Experience below JD requirement")

    print("=" * 70 + "\n")


if __name__ == "__main__":

    if len(sys.argv) != 3:
        print("\nUsage:")
        print("  python3 check_similarity.py <jd_vector_file> <resume_vector_file>\n")
        sys.exit(1)

    check_similarity(sys.argv[1], sys.argv[2])
