from __future__ import annotations

# Protocolo v4.0 §5.3.3: D e E vão à reunião de consenso; persistindo, o terceiro revisor arbitra.
CONFLICT_LETTERS = frozenset({"D", "E"})
CONSENSUS_DECISIONS = frozenset({"incluir", "excluir", "sem_consenso"})
ARBITRATION_DECISIONS = frozenset({"incluir", "excluir"})
_FINAL_RESULT = {"incluir": "included", "excluir": "excluded"}


def resolve_conflict(positions: list[str], arbitration: str | None) -> tuple[str, str | None]:
    """Status and final result of a D/E conflict (spec 004, RF26 / CA-07).

    Each of R1 and R2 records a post-meeting position. Equal positions close the
    conflict by consensus; different positions, or "sem_consenso", escalate it to
    the third reviewer, whose arbitration is final.
    """
    if arbitration is not None:
        return "resolved_by_arbitration", _FINAL_RESULT[arbitration]
    if len(positions) < 2:
        return "awaiting_consensus", None
    if positions[0] == positions[1] and positions[0] != "sem_consenso":
        return "resolved_by_consensus", _FINAL_RESULT[positions[0]]
    return "escalated", None


def classify_triage_pair(first_vote: str, second_vote: str) -> tuple[str, str]:
    valid_votes = {"incluir", "excluir", "incerto"}
    if first_vote not in valid_votes or second_vote not in valid_votes:
        raise ValueError("triage votes must be incluir, excluir or incerto")
    outcomes = {
        frozenset(("incluir", "incluir")): ("A", "included"),
        frozenset(("incluir", "incerto")): ("B", "advances"),
        frozenset(("incerto", "incerto")): ("C", "advances"),
        frozenset(("incluir", "excluir")): ("D", "consensus_required"),
        frozenset(("incerto", "excluir")): ("E", "consensus_required"),
        frozenset(("excluir", "excluir")): ("F", "excluded"),
    }
    return outcomes[frozenset((first_vote, second_vote))]
