"""Connecteur vers l'API ouverte du BOAMP (Bulletin officiel des annonces de marchés
publics), hébergée par la DILA sur une plateforme Opendatasoft.

⚠️ Le schéma exact de l'API (noms de champs) n'a pas pu être vérifié en conditions
réelles pendant le développement (réseau bloqué dans l'environnement de dev). En
conséquence :
- `record_to_ao_text` tente plusieurs noms de champs courants pour chaque information,
  et ajoute systématiquement l'annonce brute en bas du texte en repli, pour ne perdre
  aucune information même si un nom de champ attendu est incorrect.
- Testez avec `ao-agent-collect --dry-run` avant tout usage régulier, pour vérifier que
  la connexion fonctionne et que le texte généré est exploitable.
"""

import hashlib

import requests

BOAMP_API_URL = "https://boamp-datadila.opendatasoft.com/api/v2/catalog/datasets/boamp/records"

_FIELD_CANDIDATES = {
    "objet": ["objet", "objet_complet", "titre", "title"],
    "acheteur": ["acheteur_public", "nomacheteur", "nom_acheteur", "acheteur"],
    "lieu": ["lieu_execution", "lieu"],
    "deadline": ["dateremiseoffres", "date_limite_remise_offres", "datefin", "datelimitereponse"],
    "url": ["url_avis", "url", "lien"],
    "description": ["resume", "description"],
}


def search_boamp(keywords: list[str], limit: int = 20) -> list[dict]:
    """Interroge l'API du BOAMP avec une recherche plein texte sur les mots-clés fournis.

    Retourne une liste de dictionnaires (une annonce = un dictionnaire de champs).
    Lève `requests.exceptions.RequestException` en cas de problème réseau/HTTP.
    """
    params = {"q": " ".join(keywords), "limit": limit}
    response = requests.get(BOAMP_API_URL, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()
    return data.get("results", data.get("records", []))


def _first_present(record: dict, candidates: list[str]) -> str | None:
    for key in candidates:
        value = record.get(key)
        if value:
            return str(value)
    return None


def record_id(record: dict) -> str:
    """Identifiant stable d'une annonce, utilisé pour éviter de la ré-analyser."""
    for key in ("id", "idweb", "recordid", "id_lot"):
        if record.get(key):
            return str(record[key])
    # Repli si aucun identifiant standard n'est trouvé : hash du contenu.
    return hashlib.sha256(str(sorted(record.items())).encode("utf-8")).hexdigest()[:16]


def record_to_ao_text(record: dict) -> str:
    """Convertit une annonce BOAMP en texte de type "cahier des charges", exploitable
    directement par `analyze_ao` comme n'importe quel autre AO."""
    objet = _first_present(record, _FIELD_CANDIDATES["objet"]) or "non précisé"
    acheteur = _first_present(record, _FIELD_CANDIDATES["acheteur"]) or "non précisé"
    lieu = _first_present(record, _FIELD_CANDIDATES["lieu"]) or "non précisé"
    deadline = _first_present(record, _FIELD_CANDIDATES["deadline"]) or "non précisé"
    url = _first_present(record, _FIELD_CANDIDATES["url"]) or "non précisé"
    description = _first_present(record, _FIELD_CANDIDATES["description"]) or ""

    return "\n".join(
        [
            f"Objet : {objet}",
            f"Acheteur : {acheteur}",
            f"Lieu d'exécution : {lieu}",
            f"Date limite de remise des offres : {deadline}",
            f"URL de l'avis : {url}",
            "",
            description,
            "",
            "Données brutes de l'annonce (filet de sécurité si un champ ci-dessus est manquant) :",
            str(record),
        ]
    )
