from pathlib import Path

import yaml

from .llm import DEFAULT_MODEL, ask
from .rag.vectorstore import get_client, search

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB_PATH = PROJECT_ROOT / "qdrant_data"

SYSTEM_PROMPT_TEMPLATE = """Tu es l'assistant de pré-qualification des appels d'offres (AO) de {nom_entreprise}, \
une entreprise de conseil spécialisée en Data et IA.

Ton rôle : lire le cahier des charges d'un AO et produire une note de synthèse structurée pour \
l'équipe business development. Tu ne rédiges jamais de réponse définitive à l'AO, tu prépares le \
travail humain qui décidera du go/no-go.

Profil de l'entreprise, à utiliser pour évaluer la pertinence :
- Secteurs cibles : {secteurs}
- Budget cible : {budget_min} € - {budget_max} €
- Expertises clés : {expertises}
- Points de vigilance (red flags) à signaler si présents : {red_flags}

Le message de l'utilisateur contient, en plus du cahier des charges de l'AO, une section \
"Références internes pertinentes" : des passages d'anciennes missions retrouvés automatiquement \
par recherche sémantique dans la base de missions passées. Utilise-les comme SEULE source pour \
la section "Références internes à mobiliser" ci-dessous — ne cite jamais une référence qui n'y \
figure pas, et ne mobilise que celles réellement pertinentes pour cet AO. Si la section est vide \
ou indique qu'aucune référence n'a été trouvée, écris-le explicitement plutôt que d'inventer.

Réponds TOUJOURS en markdown avec exactement les sections suivantes, dans cet ordre :

## Résumé
(3-5 phrases : objet de l'AO, client, contexte)

## Score de pertinence (1-5)
Score + justification en 2-3 phrases, en te basant explicitement sur le profil ci-dessus et sur \
la présence ou non de références internes pertinentes.

## Compétences et expertises demandées
Liste à puces.

## Budget et échéances
Budget annoncé (ou "non communiqué"), deadline de réponse, durée de mission.

## Red flags
Liste à puces des points d'attention ou de risque. Écris "Aucun identifié" si rien à signaler.

## Références internes à mobiliser
Parmi les passages fournis dans "Références internes pertinentes", lesquels citer dans la \
réponse à l'AO (avec le nom du fichier source et une justification courte).

## Ébauche de plan de réponse
Un plan en 4-6 points pour la note de réponse à l'AO.

Ne fais aucune supposition non fondée : si une information n'est pas dans le texte fourni, écris \
"non précisé".
"""


def load_profile(profile_path: Path) -> dict:
    with open(profile_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_system_prompt(profile: dict) -> str:
    return SYSTEM_PROMPT_TEMPLATE.format(
        nom_entreprise=profile.get("nom_entreprise", "l'entreprise"),
        secteurs=", ".join(profile.get("secteurs_cibles", [])) or "non précisé",
        budget_min=profile.get("budget_min_eur", "non précisé"),
        budget_max=profile.get("budget_max_eur", "non précisé"),
        expertises=", ".join(profile.get("expertises_cles", [])) or "non précisé",
        red_flags=", ".join(profile.get("red_flags", [])) or "aucun critère spécifique",
    )


def retrieve_references(ao_text: str, top_k: int = 5, db_path: Path = DEFAULT_DB_PATH) -> list[dict]:
    client = get_client(db_path)
    return search(client, ao_text, top_k=top_k)


def format_references_block(matches: list[dict]) -> str:
    if not matches:
        return (
            "Aucune référence interne trouvée (base de missions vide ou non indexée — "
            "lancez `ao-agent-ingest` après avoir ajouté des fichiers dans `references/`)."
        )
    return "\n".join(
        f'- [{m["source"]}] (similarité {m["score"]:.2f}) : "{m["text"]}"' for m in matches
    )


def analyze_ao(
    ao_text: str,
    profile: dict,
    model: str = DEFAULT_MODEL,
    db_path: Path = DEFAULT_DB_PATH,
) -> str:
    system_prompt = build_system_prompt(profile)
    matches = retrieve_references(ao_text, db_path=db_path)
    references_block = format_references_block(matches)

    user_message = (
        "## Références internes pertinentes (retrouvées automatiquement par recherche sémantique)\n"
        f"{references_block}\n\n"
        "## Cahier des charges de l'AO à analyser\n"
        f"{ao_text}"
    )
    return ask(system=system_prompt, user=user_message, model=model)
