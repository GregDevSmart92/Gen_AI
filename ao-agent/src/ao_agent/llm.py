import anthropic

DEFAULT_MODEL = "claude-opus-4-8"


def create_message(
    system: str,
    messages: list[dict],
    model: str = DEFAULT_MODEL,
    tools: list[dict] | None = None,
    max_tokens: int = 4096,
):
    """Un seul appel à l'API Claude, avec ou sans outils. Retourne la réponse brute
    (pas seulement le texte) pour que l'appelant puisse inspecter stop_reason et les
    tool_use blocks — nécessaire pour piloter une boucle agentique."""
    client = anthropic.Anthropic()
    kwargs = {"model": model, "max_tokens": max_tokens, "system": system, "messages": messages}
    if tools:
        kwargs["tools"] = tools
    return client.messages.create(**kwargs)
