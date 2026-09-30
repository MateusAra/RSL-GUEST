from __future__ import annotations

import re


EXTRACTION_FIELD_IDS = frozenset(
    [f"Q-O{number}" for number in range(1, 19)]
    + [f"Q-{block}{number}" for block, count in (
        ("B", 7), ("C", 8), ("D", 4), ("E", 5), ("F", 5), ("G", 4), ("H", 4), ("I", 4)
    ) for number in range(1, count + 1)]
)


def is_substantive_field(field_id: str) -> bool:
    return bool(re.fullmatch(r"Q-[BCDEFGHI]\d+", field_id))