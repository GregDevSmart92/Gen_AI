import json
from pathlib import Path


def load_seen(path: Path) -> set[str]:
    """Identifiants des annonces déjà analysées lors d'une exécution précédente."""
    if not path.exists():
        return set()
    return set(json.loads(path.read_text(encoding="utf-8")))


def mark_seen(path: Path, ids: set[str]) -> None:
    existing = load_seen(path)
    existing |= ids
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(sorted(existing), ensure_ascii=False, indent=2), encoding="utf-8")
