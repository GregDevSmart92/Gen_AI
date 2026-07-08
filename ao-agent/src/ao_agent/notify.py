"""Notification vers un webhook Microsoft Teams (via l'app "Workflows" — voir README
pour la configuration côté Teams).

Le format du payload JSON est défini ici (pas imposé par une API tierce) : voir
`build_teams_payload`. Une notification qui échoue (Teams injoignable, webhook mal
configuré) n'interrompt jamais le pipeline — elle est simplement signalée en avertissement.
"""

import os
import re
import sys
from pathlib import Path

import requests


def extract_section(note: str, section_title: str) -> str:
    """Extrait le contenu d'une section markdown '## Titre' jusqu'à la section suivante."""
    pattern = rf"## {re.escape(section_title)}\s*\n(.*?)(?=\n## |\Z)"
    match = re.search(pattern, note, re.DOTALL)
    return match.group(1).strip() if match else ""


def build_teams_payload(ao_label: str, note: str, output_path: Path) -> dict:
    return {
        "ao": ao_label,
        "resume": extract_section(note, "Résumé") or "(résumé non trouvé)",
        "score": extract_section(note, "Score de pertinence (1-5)") or "(score non trouvé)",
        "fichier": str(output_path),
    }


def get_webhook_url() -> str | None:
    return os.environ.get("TEAMS_WEBHOOK_URL") or None


def notify_teams(webhook_url: str, ao_label: str, note: str, output_path: Path) -> bool:
    payload = build_teams_payload(ao_label, note, output_path)
    try:
        response = requests.post(webhook_url, json=payload, timeout=15)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Avertissement : notification Teams échouée ({e}).", file=sys.stderr)
        return False
