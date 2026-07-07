import argparse
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from .analyze import DEFAULT_DB_PATH, analyze_ao, load_profile
from .extract import extract_text
from .llm import DEFAULT_MODEL

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROFILE_PATH = PROJECT_ROOT / "config" / "company_profile.yaml"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "outputs"


def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Agent V0 de pré-qualification d'appels d'offres (AO) pour Soma Smart."
    )
    parser.add_argument("ao_path", type=Path, help="Chemin vers le cahier des charges (PDF, TXT ou MD)")
    parser.add_argument(
        "--profile", type=Path, default=DEFAULT_PROFILE_PATH, help="Chemin du profil entreprise (YAML)"
    )
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Modèle Claude à utiliser")
    parser.add_argument(
        "--output", type=Path, default=None, help="Chemin du fichier markdown de sortie"
    )
    parser.add_argument(
        "--db-path", type=Path, default=DEFAULT_DB_PATH, help="Chemin de la base Qdrant (RAG)"
    )
    args = parser.parse_args()

    ao_text = extract_text(args.ao_path)
    profile = load_profile(args.profile)
    note = analyze_ao(ao_text, profile, model=args.model, db_path=args.db_path)

    print(note)

    output_path = args.output
    if output_path is None:
        DEFAULT_OUTPUT_DIR.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        output_path = DEFAULT_OUTPUT_DIR / f"{args.ao_path.stem}-{timestamp}.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(note, encoding="utf-8")
    print(f"\n--\nNote sauvegardée : {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
