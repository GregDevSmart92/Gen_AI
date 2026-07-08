import argparse
import sys
from datetime import datetime
from pathlib import Path

import requests
import yaml
from dotenv import load_dotenv

from ..analyze import DEFAULT_DB_PATH, analyze_ao, load_profile
from ..llm import DEFAULT_MODEL
from ..notify import get_webhook_url, notify_teams
from .boamp import record_id, record_to_ao_text, search_boamp
from .seen_store import load_seen, mark_seen

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_PROFILE_PATH = PROJECT_ROOT / "config" / "company_profile.yaml"
DEFAULT_VEILLE_PATH = PROJECT_ROOT / "config" / "veille.yaml"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "outputs"
DEFAULT_SEEN_PATH = PROJECT_ROOT / "state" / "boamp_seen.json"


def load_veille_config(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Surveille le BOAMP et analyse automatiquement les nouveaux AO pertinents."
    )
    parser.add_argument(
        "--profile", type=Path, default=DEFAULT_PROFILE_PATH, help="Chemin du profil entreprise (YAML)"
    )
    parser.add_argument(
        "--veille-config", type=Path, default=DEFAULT_VEILLE_PATH, help="Chemin de la config de veille (YAML)"
    )
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Modèle Claude à utiliser")
    parser.add_argument("--db-path", type=Path, default=DEFAULT_DB_PATH, help="Chemin de la base Qdrant (RAG)")
    parser.add_argument(
        "--seen-path", type=Path, default=DEFAULT_SEEN_PATH, help="Fichier de suivi des AO déjà traités"
    )
    parser.add_argument("--limit", type=int, default=20, help="Nombre max d'annonces à récupérer")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Liste les nouveaux AO trouvés sans les analyser (pour vérifier la connexion BOAMP)",
    )
    parser.add_argument("--verbose", action="store_true", help="Affiche les appels d'outils de l'agent")
    parser.add_argument(
        "--no-notify", action="store_true", help="Désactive la notification Teams même si configurée"
    )
    args = parser.parse_args()

    veille_config = load_veille_config(args.veille_config)
    keywords = veille_config.get("mots_cles", ["intelligence artificielle", "data"])

    print(f"Recherche BOAMP avec les mots-clés : {keywords}", file=sys.stderr)
    try:
        records = search_boamp(keywords, limit=args.limit)
    except requests.exceptions.RequestException as e:
        print(f"Erreur : impossible de contacter l'API BOAMP ({e}).", file=sys.stderr)
        sys.exit(1)
    print(f"{len(records)} annonce(s) trouvée(s) au total pour ces mots-clés", file=sys.stderr)

    seen = load_seen(args.seen_path)
    new_ids: set[str] = set()
    profile = load_profile(args.profile)
    DEFAULT_OUTPUT_DIR.mkdir(exist_ok=True)
    webhook_url = None if args.no_notify else get_webhook_url()

    analyzed = 0
    for record in records:
        rid = record_id(record)
        if rid in seen:
            continue
        new_ids.add(rid)

        ao_text = record_to_ao_text(record)

        if args.dry_run:
            first_line = ao_text.splitlines()[0]
            print(f"[nouveau] {rid} — {first_line}")
            continue

        note = analyze_ao(ao_text, profile, model=args.model, db_path=args.db_path, verbose=args.verbose)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        output_path = DEFAULT_OUTPUT_DIR / f"boamp-{rid}-{timestamp}.md"
        output_path.write_text(note, encoding="utf-8")
        print(f"Analysé : {rid} → {output_path}")
        analyzed += 1

        if webhook_url:
            notify_teams(webhook_url, f"AO BOAMP {rid}", note, output_path)

    if not new_ids:
        print("Aucune nouvelle annonce depuis la dernière exécution.")
    elif args.dry_run:
        print(f"\n{len(new_ids)} nouvelle(s) annonce(s) — relancez sans --dry-run pour les analyser.")
    else:
        mark_seen(args.seen_path, new_ids)
        print(f"\n{analyzed} annonce(s) analysée(s) et enregistrée(s) dans outputs/.")


if __name__ == "__main__":
    main()
