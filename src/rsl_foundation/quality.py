from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any

from sklearn.metrics import cohen_kappa_score


QA_CATEGORIES = {
    "Q1": "reporting",
    "Q2": "reporting",
    "Q3": "reporting",
    "Q4": "rigor",
    "Q5": "rigor",
    "Q6": "rigor",
    "Q7": "rigor",
    "Q8": "credibility",
    "Q9": "relevance",
    "Q10": "relevance",
}
ALLOWED_NOT_APPLICABLE = {"Q6", "Q7", "Q9"}


def calculate_weighted_kappa(first: Sequence[float], second: Sequence[float]) -> float | None:
    if len(first) != len(second):
        raise ValueError("rating vectors must have the same length")
    if not first:
        return None
    if any(value not in {0, 0.5, 1} for value in (*first, *second)):
        raise ValueError("quality ratings must be 0, 0.5 or 1")
    encoded_first = [int(value * 2) for value in first]
    encoded_second = [int(value * 2) for value in second]
    result = float(cohen_kappa_score(encoded_first, encoded_second, weights="linear"))
    return None if math.isnan(result) else result


def calculate_quality_scores(scores: dict[str, float | None]) -> dict[str, Any]:
    expected = set(QA_CATEGORIES)
    if set(scores) != expected:
        raise ValueError("exactly the ten configured QA criteria are required")
    for criterion_id, score in scores.items():
        if score is not None and score not in {0, 0.5, 1}:
            raise ValueError(f"{criterion_id} score must be 0, 0.5, 1 or N/A")
        if score is None and criterion_id not in ALLOWED_NOT_APPLICABLE:
            raise ValueError(f"{criterion_id} is not eligible for N/A")

    applicable = [score for score in scores.values() if score is not None]
    if len(applicable) < 7:
        raise ValueError("at least seven applicable QA criteria are required")

    category_scores: dict[str, float] = {}
    for category in {"reporting", "rigor", "credibility", "relevance"}:
        category_values = [
            score for criterion_id, score in scores.items()
            if QA_CATEGORIES[criterion_id] == category and score is not None
        ]
        category_scores[category] = (
            round(sum(category_values) / len(category_values) * 10, 4)
            if category_values
            else 0.0
        )

    total_score = round(sum(applicable) / len(applicable) * 10, 4)
    classification = "alta" if total_score >= 7 else "moderada" if total_score >= 4 else "baixa"
    return {
        "score": total_score,
        "category_scores": category_scores,
        "classification": classification,
        "applicable_count": len(applicable),
        "not_applicable_count": 10 - len(applicable),
    }