from pathlib import Path

from qdrant_client import QdrantClient, models

from .embeddings import embed_query, embed_texts

COLLECTION_NAME = "references_missions"
EMBEDDING_DIM = 384


def get_client(db_path: Path) -> QdrantClient:
    """Client Qdrant en mode local embarqué (un dossier sur disque, pas de serveur)."""
    return QdrantClient(path=str(db_path))


def reset_collection(client: QdrantClient) -> None:
    if client.collection_exists(COLLECTION_NAME):
        client.delete_collection(COLLECTION_NAME)
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(size=EMBEDDING_DIM, distance=models.Distance.COSINE),
    )


def index_chunks(client: QdrantClient, chunks: list[dict]) -> None:
    """chunks : [{"text": ..., "source": ...}, ...]

    Les embeddings sont générés localement par sentence-transformers (modèle téléchargé
    une seule fois, puis mis en cache) : aucune donnée n'est envoyée à un service externe
    pour cette étape.
    """
    vectors = embed_texts([c["text"] for c in chunks])
    points = [
        models.PointStruct(
            id=i,
            vector=vector,
            payload={"text": c["text"], "source": c["source"]},
        )
        for i, (c, vector) in enumerate(zip(chunks, vectors))
    ]
    client.upsert(collection_name=COLLECTION_NAME, points=points)


def search(client: QdrantClient, query_text: str, top_k: int = 5) -> list[dict]:
    if not client.collection_exists(COLLECTION_NAME):
        return []
    query_vector = embed_query(query_text)
    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k,
    ).points
    return [
        {
            "text": r.payload.get("text", ""),
            "source": r.payload.get("source", "inconnu"),
            "score": r.score,
        }
        for r in results
    ]
