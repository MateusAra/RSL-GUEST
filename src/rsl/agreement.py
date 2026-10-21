"""Inter-coder agreement for dual coding, computed with validated libraries (sklearn, krippendorff)."""

from __future__ import annotations

import math
import warnings
from typing import Any

import krippendorff
import numpy as np
from sklearn.exceptions import UndefinedMetricWarning
from sklearn.metrics import cohen_kappa_score

AGREEMENT_THRESHOLD = 0.6


def _finite(value: float) -> float | None:
    return None if value is None or math.isnan(value) else float(value)


def cohen_kappa(first: list[int], second: list[int]) -> float | None:
    """Cohen's kappa for one exclusive code per unit."""
    if len(first) != len(second):
        raise ValueError("both coders must rate the same units")
    if not first:
        return None
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", (UndefinedMetricWarning, RuntimeWarning))
        return _finite(cohen_kappa_score(first, second))


def krippendorff_alpha(first: list[int], second: list[int]) -> float | None:
    """Nominal Krippendorff's alpha for two coders over the same units."""
    if len(first) != len(second):
        raise ValueError("both coders must rate the same units")
    if not first or len(set(first) | set(second)) < 2:
        return None
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        return _finite(krippendorff.alpha(reliability_data=np.array([first, second], dtype=float),
                                          level_of_measurement="nominal"))


def coding_agreement(first: dict[int, set[int]], second: dict[int, set[int]], codes: list[int]) -> dict[str, Any]:
    """Agreement between two coders on the same segments.

    Alpha is computed on code presence/absence per segment × code, so it also covers segments with several codes.
    Kappa is reported only when every segment received exactly one code from each coder.
    """
    segments = sorted(set(first) | set(second))
    presence_first = [int(code in first.get(segment, set())) for segment in segments for code in codes]
    presence_second = [int(code in second.get(segment, set())) for segment in segments for code in codes]
    exclusive = bool(segments) and all(len(first.get(s, set())) == 1 and len(second.get(s, set())) == 1 for s in segments)
    kappa = (
        cohen_kappa([next(iter(first[s])) for s in segments], [next(iter(second[s])) for s in segments])
        if exclusive else None
    )
    alpha = krippendorff_alpha(presence_first, presence_second)
    metric, value = ("kappa", kappa) if exclusive else ("alpha", alpha)
    return {
        "segments": len(segments),
        "agreed_segments": sum(first.get(s, set()) == second.get(s, set()) for s in segments),
        "alpha": alpha,
        "kappa": kappa,
        "metric": metric,
        "value": value,
        "threshold": AGREEMENT_THRESHOLD,
        "below_threshold": value is not None and value < AGREEMENT_THRESHOLD,
    }
