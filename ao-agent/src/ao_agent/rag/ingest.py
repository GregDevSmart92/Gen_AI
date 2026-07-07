import argparse
from pathlib import Path

from .chunking import chunk_text
from .vectorstore import get_client, index_chunks, reset_collection

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_REFERENCES_DIR = PROJECT_ROOT / "references"
DEFAULT_DB_PATH = PROJECT_ROOT / "qdrant_data"


def ingest_references(references_dir: Path, db_path: Path) -> int:
    """Indexe tous les fichiers .md d'un dossier de références dans Qdrant.

    Réinitialise la collection à chaque appel : simple et suffisant tant que le
    corpus tient en quelques dizaines de documents.
    """
    client = get_client(db_path)
    reset_collection(client)

    chunks = []
    for file_path in sorted(references_dir.glob("*.md")):
        text = file_path.read_text(encoding="utf-8")
        for paragraph in chunk_text(text):
            chunks.append({"text": paragraph, "source": file_path.stem})

    if chunks:
        index_chunks(client, chunks)

    return len(chunks)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Indexe les références internes (anciennes missions) dans Qdrant."
    )
    parser.add_argument(
        "--references-dir", type=Path, default=DEFAULT_REFERENCES_DIR, help="Dossier des fichiers .md"
    )
    parser.add_argument("--db-path", type=Path, default=DEFAULT_DB_PATH, help="Dossier de la base Qdrant")
    args = parser.parse_args()

    count = ingest_references(args.references_dir, args.db_path)
    print(f"{count} chunks indexés depuis {args.references_dir} vers {args.db_path}")


if __name__ == "__main__":
    main()
