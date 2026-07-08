import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .llm import DEFAULT_MODEL, create_message
from .tools import DEFAULT_DB_PATH, TOOLS, execute_tool

MAX_ITERATIONS = 6


@dataclass
class AnalysisResult:
    note: str
    modele: str
    iterations: int
    appels_outils: dict[str, int] = field(default_factory=dict)
    tokens_entree: int = 0
    tokens_sortie: int = 0
    duree_secondes: float = 0.0

SYSTEM_PROMPT_TEMPLATE = """Tu es l'assistant de pré-qualification des appels d'offres (AO) de {nom_entreprise}, \
une entreprise de conseil spécialisée en Data et IA.

Ton rôle : lire le cahier des charges d'un AO et produire une note de synthèse structurée pour \
l'équipe business development. Tu ne rédiges jamais de réponse définitive à l'AO, tu prépares le \
travail humain qui décidera du go/no-go.

Profil de l'entreprise, à utiliser pour évaluer la pertinence :
- Secteurs cibles : {secteurs}
- Expertises clés : {expertises}
- Points de vigilance (red flags) à signaler si présents : {red_flags}

Tu disposes de deux outils :
- `chercher_references_internes` : recherche sémantique dans une base d'anciennes missions. \
Utilise-le au moins une fois, avec une requête ciblée (le type de besoin ou d'expertise de l'AO, \
pas tout le texte), avant de conclure. Tu peux l'appeler plusieurs fois avec des requêtes \
différentes si les premiers résultats ne sont pas convaincants.
- `verifier_budget` : vérifie mécaniquement si un budget annoncé est dans la fourchette cible de \
l'entreprise. Utilise-le dès que l'AO mentionne un montant.

Ne cite JAMAIS une référence interne qui ne provient pas d'un résultat de \
`chercher_references_internes` — si aucun résultat pertinent n'est trouvé, dis-le explicitement.

Une fois que tu as toutes les informations nécessaires (recherche de références faite, budget \
vérifié si un montant était mentionné), réponds en markdown avec exactement les sections \
suivantes, dans cet ordre, et n'appelle plus aucun outil à ce moment-là :

## Résumé
(3-5 phrases : objet de l'AO, client, contexte)

## Score de pertinence (1-5)
Score + justification en 2-3 phrases, en te basant explicitement sur le profil, le résultat de \
`verifier_budget` si utilisé, et la présence ou non de références internes pertinentes.

## Compétences et expertises demandées
Liste à puces.

## Budget et échéances
Budget annoncé (ou "non communiqué") et verdict de `verifier_budget` si utilisé, deadline de \
réponse, durée de mission.

## Red flags
Liste à puces des points d'attention ou de risque. Écris "Aucun identifié" si rien à signaler.

## Références internes à mobiliser
Parmi les résultats de `chercher_references_internes`, lesquels citer dans la réponse à l'AO \
(avec le nom du fichier source et une justification courte).

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
        expertises=", ".join(profile.get("expertises_cles", [])) or "non précisé",
        red_flags=", ".join(profile.get("red_flags", [])) or "aucun critère spécifique",
    )


def analyze_ao(
    ao_text: str,
    profile: dict,
    model: str = DEFAULT_MODEL,
    db_path: Path = DEFAULT_DB_PATH,
    verbose: bool = False,
) -> AnalysisResult:
    """Boucle agentique : Claude reçoit l'AO, choisit d'appeler des outils (recherche de
    références, vérification de budget) autant de fois que nécessaire, puis rédige la
    note finale. S'arrête quand Claude ne demande plus d'outil, ou après MAX_ITERATIONS
    par sécurité. Retourne aussi les métriques de la boucle (itérations, outils appelés,
    tokens, durée) pour l'observabilité (V5)."""
    system_prompt = build_system_prompt(profile)
    messages = [{"role": "user", "content": f"## Cahier des charges de l'AO à analyser\n{ao_text}"}]

    appels_outils: dict[str, int] = {}
    tokens_entree = 0
    tokens_sortie = 0
    start = time.monotonic()

    for iteration in range(1, MAX_ITERATIONS + 1):
        response = create_message(system=system_prompt, messages=messages, model=model, tools=TOOLS)
        tokens_entree += response.usage.input_tokens
        tokens_sortie += response.usage.output_tokens
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason != "tool_use":
            note = "".join(block.text for block in response.content if block.type == "text")
            return AnalysisResult(
                note=note,
                modele=model,
                iterations=iteration,
                appels_outils=appels_outils,
                tokens_entree=tokens_entree,
                tokens_sortie=tokens_sortie,
                duree_secondes=time.monotonic() - start,
            )

        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                appels_outils[block.name] = appels_outils.get(block.name, 0) + 1
                if verbose:
                    print(f"[outil] {block.name}({block.input})", file=sys.stderr)
                result_text = execute_tool(block.name, block.input, profile=profile, db_path=db_path)
                tool_results.append(
                    {"type": "tool_result", "tool_use_id": block.id, "content": result_text}
                )
        messages.append({"role": "user", "content": tool_results})

    return AnalysisResult(
        note="⚠️ Nombre maximum d'itérations atteint sans réponse finale de l'agent.",
        modele=model,
        iterations=MAX_ITERATIONS,
        appels_outils=appels_outils,
        tokens_entree=tokens_entree,
        tokens_sortie=tokens_sortie,
        duree_secondes=time.monotonic() - start,
    )
