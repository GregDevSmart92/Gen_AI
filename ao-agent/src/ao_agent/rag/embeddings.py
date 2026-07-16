"""Génération d'embeddings via sentence-transformers (PyTorch).

Choisi à la place de FastEmbed/onnxruntime : PyTorch embarque son propre runtime dans
son paquet, ce qui évite le bug de DLL native rencontré avec onnxruntime sur certains
postes Windows verrouillés (pas de droits admin pour installer le Visual C++
Redistributable). Toujours 100% local — aucune donnée envoyée à un service externe pour
cette étape, aucune clé API supplémentaire.
"""

from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"

_model: SentenceTransformer | None = None


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def embed_texts(texts: list[str]) -> list[list[float]]:
    model = get_model()
    return model.encode(texts, normalize_embeddings=True).tolist()


def embed_query(text: str) -> list[float]:
    return embed_texts([text])[0]
