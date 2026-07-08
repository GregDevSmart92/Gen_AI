import argparse
from pathlib import Path

from .validation import VALID_DECISIONS, record_decision

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DECISIONS_PATH = PROJECT_ROOT / "state" / "decisions.jsonl"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Enregistre une décision humaine formalisée (go/no-go) sur une note d'AO."
    )
    parser.add_argument("note_path", type=Path, help="Chemin du fichier de note (dans outputs/)")
    parser.add_argument(
        "--decision", required=True, choices=sorted(VALID_DECISIONS), help="Décision à enregistrer"
    )
    parser.add_argument("--commentaire", default="", help="Justification ou contexte de la décision")
    parser.add_argument("--auteur", default="", help="Nom de la personne qui valide")
    parser.add_argument(
        "--decisions-path", type=Path, default=DEFAULT_DECISIONS_PATH, help="Journal des décisions (JSONL)"
    )
    args = parser.parse_args()

    entry = record_decision(
        args.decisions_path, args.note_path, args.decision, args.commentaire, args.auteur
    )
    print(f"Décision enregistrée : {entry['decision']} pour {entry['note']}")
    print(f"Journal : {args.decisions_path}")


if __name__ == "__main__":
    main()
