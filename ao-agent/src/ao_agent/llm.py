import anthropic

DEFAULT_MODEL = "claude-opus-4-8"


def ask(system: str, user: str, model: str = DEFAULT_MODEL) -> str:
    """Envoie un prompt structuré à Claude et retourne le texte de la réponse."""
    client = anthropic.Anthropic()
    response = client.messages.create(
        model=model,
        max_tokens=4096,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return "".join(block.text for block in response.content if block.type == "text")
