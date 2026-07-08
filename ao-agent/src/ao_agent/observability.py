import json
import re
from datetime import datetime
from pathlib import Path

from .analyze import AnalysisResult

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LOG_PATH = PROJECT_ROOT / "state" / "analysis_log.jsonl"


def extract_score(note: str) -> int | None:
    """Extrait le score (1-5) donné par l'agent depuis la note markdown générée."""
    match = re.search(r"## Score de pertinence \(1-5\)\s*\n\s*(\d)", note)
    return int(match.group(1)) if match else None


def log_analysis(log_path: Path, source: str, note_path: Path, result: AnalysisResult) -> dict:
    """Enregistre une entrée de journal pour une analyse (une ligne JSON par analyse)."""
    entry = {
        "horodatage": datetime.now().isoformat(timespec="seconds"),
        "source": source,
        "note_path": str(note_path),
        "modele": result.modele,
        "score": extract_score(result.note),
        "iterations": result.iterations,
        "appels_outils": result.appels_outils,
        "tokens_entree": result.tokens_entree,
        "tokens_sortie": result.tokens_sortie,
        "duree_secondes": round(result.duree_secondes, 2),
    }
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def read_log(log_path: Path) -> list[dict]:
    if not log_path.exists():
        return []
    with open(log_path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]
