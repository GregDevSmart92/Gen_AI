from pathlib import Path


def extract_text(path: Path) -> str:
    """Extrait le texte d'un cahier des charges (PDF, TXT ou MD)."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {path}")

    if path.suffix.lower() == ".pdf":
        import fitz  # PyMuPDF

        doc = fitz.open(path)
        try:
            return "\n".join(page.get_text() for page in doc)
        finally:
            doc.close()

    return path.read_text(encoding="utf-8")
