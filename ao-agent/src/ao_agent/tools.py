from pathlib import Path

from .rag.vectorstore import get_client, search

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB_PATH = PROJECT_ROOT / "qdrant_data"

TOOLS = [
    {
        "name": "chercher_references_internes",
        "description": (
            "Recherche sémantique dans la base des anciennes missions/références de l'entreprise. "
            "Utilise une requête ciblée décrivant le type de besoin ou d'expertise recherché "
            "(pas tout le texte de l'AO). À utiliser au moins une fois avant de conclure "
            "l'analyse d'un AO ; peut être rappelé avec une requête différente si les premiers "
            "résultats ne sont pas convaincants."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "requete": {
                    "type": "string",
                    "description": "Requête décrivant le besoin ou l'expertise à rechercher.",
                },
                "nombre_resultats": {
                    "type": "integer",
                    "description": "Nombre de résultats à retourner (par défaut 5).",
                },
            },
            "required": ["requete"],
        },
    },
    {
        "name": "verifier_budget",
        "description": (
            "Vérifie mécaniquement si un budget annoncé (en euros) est dans la fourchette cible "
            "de l'entreprise. Utilise cet outil dès qu'un montant est mentionné dans l'AO."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "budget_eur": {
                    "type": "number",
                    "description": "Montant du budget annoncé, en euros.",
                },
            },
            "required": ["budget_eur"],
        },
    },
]


def _format_references_block(matches: list[dict]) -> str:
    if not matches:
        return "Aucune référence interne trouvée pour cette requête."
    return "\n".join(
        f'- [{m["source"]}] (similarité {m["score"]:.2f}) : "{m["text"]}"' for m in matches
    )


def _chercher_references_internes(tool_input: dict, db_path: Path) -> str:
    requete = tool_input["requete"]
    top_k = tool_input.get("nombre_resultats", 5)
    client = get_client(db_path)
    matches = search(client, requete, top_k=top_k)
    return _format_references_block(matches)


def _verifier_budget(tool_input: dict, profile: dict) -> str:
    budget = tool_input["budget_eur"]
    budget_min = profile.get("budget_min_eur")
    budget_max = profile.get("budget_max_eur")
    fourchette = f"{budget_min} € - {budget_max} €"

    if budget_min is not None and budget < budget_min:
        verdict = f"en dessous de la fourchette cible ({fourchette})"
    elif budget_max is not None and budget > budget_max:
        verdict = f"au-dessus de la fourchette cible ({fourchette})"
    else:
        verdict = f"dans la fourchette cible ({fourchette})"

    return f"Budget annoncé : {budget} €. Verdict : {verdict}."


def execute_tool(name: str, tool_input: dict, profile: dict, db_path: Path) -> str:
    if name == "chercher_references_internes":
        return _chercher_references_internes(tool_input, db_path)
    if name == "verifier_budget":
        return _verifier_budget(tool_input, profile)
    return f"Erreur : outil inconnu '{name}'."
