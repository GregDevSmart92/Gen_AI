def chunk_text(text: str, min_length: int = 40) -> list[str]:
    """Découpe un texte en paragraphes.

    Unité de chunk volontairement simple pour la V1 (un paragraphe = un chunk) :
    suffisant pour des documents de quelques pages, à affiner si les documents
    grossissent (découpage à taille fixe avec chevauchement, par exemple).
    """
    paragraphs = [p.strip() for p in text.split("\n\n")]
    return [p for p in paragraphs if len(p) >= min_length]
