from pathlib import Path
from statistics import mean

from .observability import read_log
from .validation import read_decisions


def build_report(log_path: Path, decisions_path: Path) -> dict:
    """Croise le journal des analyses (score, coût, durée) avec le journal des décisions
    humaines (go/no-go/à-clarifier), pour mesurer si le score de l'agent est cohérent avec
    ce que les humains décident au final."""
    log_entries = read_log(log_path)
    decisions = read_decisions(decisions_path)
    decisions_by_note = {d["note"]: d["decision"] for d in decisions}

    scores = [e["score"] for e in log_entries if e.get("score") is not None]

    score_by_decision: dict[str, list[int]] = {}
    for entry in log_entries:
        decision = decisions_by_note.get(entry.get("note_path"))
        if decision and entry.get("score") is not None:
            score_by_decision.setdefault(decision, []).append(entry["score"])

    return {
        "nombre_analyses": len(log_entries),
        "score_moyen": round(mean(scores), 2) if scores else None,
        "tokens_entree_total": sum(e["tokens_entree"] for e in log_entries),
        "tokens_sortie_total": sum(e["tokens_sortie"] for e in log_entries),
        "duree_moyenne_secondes": (
            round(mean(e["duree_secondes"] for e in log_entries), 2) if log_entries else None
        ),
        "score_moyen_par_decision": {
            decision: round(mean(scores_list), 2) for decision, scores_list in score_by_decision.items()
        },
        "nombre_decisions_liees": sum(len(v) for v in score_by_decision.values()),
    }
