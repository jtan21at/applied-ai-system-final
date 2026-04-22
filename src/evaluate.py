"""
Evaluation harness for VibeFinder.

Runs a predefined set of test cases through the recommender and prints a
pass/fail summary along with average confidence scores.

Run with:
    PYTHONPATH=src python -m src.evaluate
"""

import logging
import sys
from typing import Dict, List

from recommender import load_songs, recommend_songs, validate_user_prefs

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stderr,
)

# ---------------------------------------------------------------------------
# Test cases
# Each case specifies user preferences and one or more assertions:
#   expect_top_genre  – the genre the #1 result must match
#   min_confidence    – the minimum confidence score for the #1 result
# ---------------------------------------------------------------------------
TEST_CASES: List[Dict] = [
    {
        "name": "High-Energy Pop",
        "prefs": {"genre": "pop", "mood": "happy", "energy": 0.85, "likes_acoustic": False},
        "expect_top_genre": "pop",
        "min_confidence": 0.70,
    },
    {
        "name": "Chill Lofi Acoustic",
        "prefs": {"genre": "lofi", "mood": "chill", "energy": 0.35, "likes_acoustic": True},
        "expect_top_genre": "lofi",
        "min_confidence": 0.85,
    },
    {
        "name": "Deep Intense Rock",
        "prefs": {"genre": "rock", "mood": "intense", "energy": 0.92, "likes_acoustic": False},
        "expect_top_genre": "rock",
        "min_confidence": 0.75,
    },
    {
        "name": "Ambient Low Energy",
        "prefs": {"genre": "ambient", "mood": "chill", "energy": 0.25, "likes_acoustic": True},
        "expect_top_genre": "ambient",
        "min_confidence": 0.60,
    },
    {
        "name": "Jazz Relaxed",
        "prefs": {"genre": "jazz", "mood": "relaxed", "energy": 0.40, "likes_acoustic": False},
        "expect_top_genre": "jazz",
        "min_confidence": 0.60,
    },
    {
        "name": "Edge Case – Conflicting Prefs (pop + sad + high energy)",
        "prefs": {"genre": "pop", "mood": "sad", "energy": 0.90, "likes_acoustic": False},
        # No sad pop songs exist; genre match still dominates → top result is pop
        "expect_top_genre": "pop",
        "min_confidence": 0.50,
    },
    {
        "name": "Guardrail – Invalid Energy (out of range)",
        "prefs": {"genre": "pop", "mood": "happy", "energy": 1.5, "likes_acoustic": False},
        "expect_validation_error": True,
    },
    {
        "name": "Guardrail – Empty Genre",
        "prefs": {"genre": "", "mood": "happy", "energy": 0.8, "likes_acoustic": False},
        "expect_validation_error": True,
    },
]


def run_evaluation(catalog_path: str = "data/songs.csv") -> None:
    songs = load_songs(catalog_path)

    passed = 0
    failed = 0
    confidence_values: List[float] = []

    print("=" * 70)
    print("  VibeFinder Evaluation Harness")
    print("=" * 70)

    for case in TEST_CASES:
        name = case["name"]
        prefs = case["prefs"]
        expect_error = case.get("expect_validation_error", False)

        # ── Guardrail tests ─────────────────────────────────────────────────
        if expect_error:
            try:
                validate_user_prefs(prefs)
                status = "FAIL"
                note = "expected ValueError but none was raised"
                failed += 1
            except ValueError as exc:
                status = "PASS"
                note = f"raised ValueError as expected ({exc})"
                passed += 1
            print(f"  [{status}] {name}")
            print(f"         {note}")
            continue

        # ── Normal recommendation tests ──────────────────────────────────────
        results = recommend_songs(prefs, songs, k=5)
        top_song, top_score, _explanation, top_confidence = results[0]
        confidence_values.append(top_confidence)

        failures = []
        if case.get("expect_top_genre") and top_song["genre"] != case["expect_top_genre"]:
            failures.append(
                f"top genre '{top_song['genre']}' ≠ expected '{case['expect_top_genre']}'"
            )
        if top_confidence < case.get("min_confidence", 0.0):
            failures.append(
                f"confidence {top_confidence:.2f} < minimum {case['min_confidence']:.2f}"
            )

        if failures:
            status = "FAIL"
            failed += 1
        else:
            status = "PASS"
            passed += 1

        print(f"  [{status}] {name}")
        print(
            f"         top='{top_song['title']}' ({top_song['genre']})"
            f"  score={top_score:.2f}  confidence={top_confidence:.0%}"
        )
        for reason in failures:
            print(f"         ✗ {reason}")

    # ── Summary ─────────────────────────────────────────────────────────────
    print("=" * 70)
    total = passed + failed
    avg_conf = sum(confidence_values) / len(confidence_values) if confidence_values else 0.0
    print(f"  Results  : {passed}/{total} tests passed")
    print(f"  Avg confidence (recommendation tests only): {avg_conf:.2f}")
    print("=" * 70)


if __name__ == "__main__":
    run_evaluation()
