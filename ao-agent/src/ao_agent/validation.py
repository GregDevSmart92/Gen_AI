import json
from datetime import datetime
from pathlib import Path

VALID_DECISIONS = {"go", "no-go", "a-clarifier"}


def record_decision(
    decisions_path: Path,
    note_path: Path,
    decision: str,
    commentaire: str = "",
    auteur: str = "",
) -> dict:
    """Enregistre une décision humaine formalisée sur une note d'analyse d'AO, en
    ajoutant une ligne à un journal JSONL (append-only, traçable et horodaté)."""
    if decision not in VALID_DECISIONS:
        raise ValueError(f"Décision invalide : '{decision}'. Valeurs autorisées : {sorted(VALID_DECISIONS)}.")

    entry = {
        "horodatage": datetime.now().isoformat(timespec="seconds"),
        "note": str(note_path),
        "decision": decision,
        "commentaire": commentaire,
        "auteur": auteur,
    }

    decisions_path.parent.mkdir(parents=True, exist_ok=True)
    with open(decisions_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    return entry


def read_decisions(decisions_path: Path) -> list[dict]:
    if not decisions_path.exists():
        return []
    with open(decisions_path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]
