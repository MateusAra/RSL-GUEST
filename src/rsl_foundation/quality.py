from __future__ import annotations

import math
import warnings
from collections.abc import Sequence
from typing import Any

from sklearn.exceptions import UndefinedMetricWarning
from sklearn.metrics import cohen_kappa_score


QA_CATEGORY_NAMES = ("reporting", "rigor", "credibility", "relevance")

# Protocolo v4.0 §7 (spec 005, seção 9b): carga inicial do instrumento.
QA_V4_INSTRUMENT: dict[str, Any] = {
    "criteria": [
        {"id": "Q1", "category": "reporting", "na_eligible": False,
         "text": "O objetivo e a questão de pesquisa estão claramente definidos?"},
        {"id": "Q2", "category": "reporting", "na_eligible": False,
         "text": "As conclusões são suportadas pelos dados e respondem às questões de pesquisa?"},
        {"id": "Q3", "category": "reporting", "na_eligible": False,
         "text": "As ameaças à validade são identificadas e discutidas?"},
        {"id": "Q4", "category": "rigor", "na_eligible": False,
         "text": "O design do estudo é adequado ao objetivo?"},
        {"id": "Q5", "category": "rigor", "na_eligible": False,
         "text": "O método de coleta de dados é descrito e justificado?"},
        {"id": "Q6", "category": "rigor", "na_eligible": True,
         "text": "O MAS é caracterizado (tipo de agente, número, interações, arquitetura)?"},
        {"id": "Q7", "category": "rigor", "na_eligible": True,
         "text": "A abordagem de XAI está vinculada à arquitetura do MAS?"},
        {"id": "Q8", "category": "credibility", "na_eligible": False,
         "text": "Os requisitos de XAI/RAI/Trust são definidos ou operacionalizados?"},
        {"id": "Q9", "category": "relevance", "na_eligible": True,
         "text": "O papel dos stakeholders na explicabilidade é discutido?"},
        {"id": "Q10", "category": "relevance", "na_eligible": False,
         "text": "O estudo identifica lacunas ou direções futuras em XAI para MAS?"},
    ],
    "min_applicable": 7,
}

QA_CATEGORIES = {criterion["id"]: criterion["category"] for criterion in QA_V4_INSTRUMENT["criteria"]}
ALLOWED_NOT_APPLICABLE = {criterion["id"] for criterion in QA_V4_INSTRUMENT["criteria"] if criterion["na_eligible"]}

# Spec 005 RF31 / CA-05: faixas de corte do §7.3 e o desfecho de cada uma.
QUALITY_OUTCOMES = {"alta": "aprovado", "moderada": "ressalva", "baixa": "excluido_qualidade"}


def validate_instrument(instrument: dict[str, Any]) -> list[str]:
    """Validate an instrument and return the protocol deviations it introduces."""
    criteria = instrument.get("criteria")
    if not isinstance(criteria, list) or not criteria:
        raise ValueError("QA instrument requires a list of criteria")
    seen: set[str] = set()
    for criterion in criteria:
        criterion_id = str(criterion.get("id", "")).strip()
        if not criterion_id or criterion_id in seen:
            raise ValueError("QA criteria require unique ids")
        seen.add(criterion_id)
        if criterion.get("category") not in QA_CATEGORY_NAMES:
            raise ValueError(f"{criterion_id} category must be one of {', '.join(QA_CATEGORY_NAMES)}")
        if not str(criterion.get("text", "")).strip():
            raise ValueError(f"{criterion_id} requires the criterion text")
    min_applicable = instrument.get("min_applicable", 7)
    if not isinstance(min_applicable, int) or not 1 <= min_applicable <= len(criteria):
        raise ValueError("min_applicable must be between 1 and the number of criteria")

    deviations = []
    if len(criteria) != 10:
        deviations.append(f"instrument has {len(criteria)} criteria instead of 10")
    categories = {criterion["category"] for criterion in criteria}
    if categories != set(QA_CATEGORY_NAMES):
        deviations.append("instrument does not cover the four protocol categories")
    return deviations


def calculate_weighted_kappa(first: Sequence[float], second: Sequence[float]) -> float | None:
    if len(first) != len(second):
        raise ValueError("rating vectors must have the same length")
    if not first:
        return None
    if any(value not in {0, 0.5, 1} for value in (*first, *second)):
        raise ValueError("quality ratings must be 0, 0.5 or 1")
    encoded_first = [int(value * 2) for value in first]
    encoded_second = [int(value * 2) for value in second]
    with warnings.catch_warnings():
        # A single shared label leaves kappa undefined; that case is reported as None below.
        warnings.simplefilter("ignore", UndefinedMetricWarning)
        result = float(cohen_kappa_score(encoded_first, encoded_second, weights="linear", labels=[0, 1, 2]))
    return None if math.isnan(result) else result


def classify_quality_score(score: float) -> str:
    return "alta" if score >= 7 else "moderada" if score >= 4 else "baixa"


def _aggregate(scores: dict[str, float | None], categories: dict[str, str]) -> dict[str, Any]:
    applicable = [score for score in scores.values() if score is not None]
    category_scores: dict[str, float | None] = {}
    for category in QA_CATEGORY_NAMES:
        category_values = [
            score for criterion_id, score in scores.items()
            if categories[criterion_id] == category and score is not None
        ]
        category_scores[category] = (
            round(sum(category_values) / len(category_values) * 10, 4) if category_values else None
        )
    total_score = round(sum(applicable) / len(applicable) * 10, 4)
    classification = classify_quality_score(total_score)
    return {
        "score": total_score,
        "category_scores": category_scores,
        "classification": classification,
        "outcome": QUALITY_OUTCOMES[classification],
        "applicable_count": len(applicable),
        "not_applicable_count": len(scores) - len(applicable),
    }


def calculate_quality_scores(
    scores: dict[str, float | None],
    instrument: dict[str, Any] | None = None,
) -> dict[str, Any]:
    instrument = instrument or QA_V4_INSTRUMENT
    categories = {criterion["id"]: criterion["category"] for criterion in instrument["criteria"]}
    na_eligible = {criterion["id"] for criterion in instrument["criteria"] if criterion.get("na_eligible")}
    if set(scores) != set(categories):
        raise ValueError(f"exactly the {len(categories)} configured QA criteria are required")
    for criterion_id, score in scores.items():
        if score is not None and score not in {0, 0.5, 1}:
            raise ValueError(f"{criterion_id} score must be 0, 0.5, 1 or N/A")
        if score is None and criterion_id not in na_eligible:
            raise ValueError(f"{criterion_id} is not eligible for N/A")

    min_applicable = instrument.get("min_applicable", 7)
    if sum(score is not None for score in scores.values()) < min_applicable:
        raise ValueError(f"at least {min_applicable} applicable QA criteria are required")
    return _aggregate(scores, categories)


def resolve_quality_consensus(
    first: dict[str, float | None],
    second: dict[str, float | None],
    arbitrations: dict[str, float | None],
    instrument: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Combine two confirmed assessments item by item (spec 005, rules 4 and 5).

    Items differing by at most 0.5 are averaged; larger differences, and items
    where only one reviewer marked N/A, go to the third reviewer, whose score
    prevails for that item.
    """
    instrument = instrument or QA_V4_INSTRUMENT
    categories = {criterion["id"]: criterion["category"] for criterion in instrument["criteria"]}
    items: dict[str, float | None] = {}
    disputed: list[str] = []
    pending: list[str] = []
    for criterion_id in categories:
        first_score, second_score = first.get(criterion_id), second.get(criterion_id)
        if first_score is None and second_score is None:
            items[criterion_id] = None
            continue
        if first_score is not None and second_score is not None and abs(first_score - second_score) <= 0.5:
            items[criterion_id] = (first_score + second_score) / 2
            continue
        disputed.append(criterion_id)
        if criterion_id in arbitrations:
            items[criterion_id] = arbitrations[criterion_id]
        else:
            pending.append(criterion_id)

    result: dict[str, Any] = {
        "items": items,
        "disputed_criteria": disputed,
        "pending_arbitration": pending,
        "status": "awaiting_arbitration" if pending else "final",
    }
    if pending:
        return result
    if not any(score is not None for score in items.values()):
        result["status"] = "insufficient_applicable"
        return result
    result.update(_aggregate(items, categories))
    if result["applicable_count"] < instrument.get("min_applicable", 7):
        result["status"] = "insufficient_applicable"
    return result
