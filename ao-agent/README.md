# Agent de pré-qualification d'AO — V0

Premier agent IA (version 0) : prend un appel d'offres (PDF, TXT ou MD), l'analyse avec Claude
à partir du profil de Soma Smart, et produit une note de synthèse markdown (résumé, score de
pertinence, red flags, références internes à mobiliser, ébauche de plan de réponse).

Ce n'est **pas encore un agent** au sens strict (pas de boucle d'outils, pas de RAG) : c'est le
socle V0 — un seul appel structuré au LLM — sur lequel les prochaines versions vont s'appuyer
(RAG sur les anciennes missions, veille automatisée, notification Slack, etc.).

## Installation

```bash
cd ao-agent
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Puis éditer .env et renseigner ANTHROPIC_API_KEY
```

## Configuration

Éditez `config/company_profile.yaml` pour refléter le vrai profil de Soma Smart (secteurs
cibles, fourchette de budget, expertises clés, références internes, red flags).

## Utilisation

```bash
python -m ao_agent.cli samples/exemple_ao.txt
```

Options :
- `--profile <chemin>` : utiliser un autre profil entreprise (YAML)
- `--model <id>` : changer de modèle Claude (par défaut `claude-opus-4-8`)
- `--output <chemin>` : chemin du fichier markdown de sortie (par défaut `outputs/<nom>-<date>.md`)

La note est affichée dans le terminal et sauvegardée dans `outputs/`.

## Structure

```
ao-agent/
├── config/
│   └── company_profile.yaml   # grille de scoring / profil entreprise
├── samples/
│   └── exemple_ao.txt         # AO fictif pour tester sans PDF
├── src/ao_agent/
│   ├── extract.py             # extraction de texte (PDF via PyMuPDF, TXT/MD brut)
│   ├── llm.py                 # appel à l'API Claude
│   ├── analyze.py             # construction du prompt + orchestration
│   └── cli.py                 # point d'entrée en ligne de commande
└── outputs/                    # notes générées (non versionné)
```

## Roadmap (prochaines versions)

- **V1** : RAG sur d'anciennes missions/références (Qdrant) pour ancrer le score de pertinence
- **V2** : transformer en véritable agent (boucle d'outils : recherche interne, scoring, génération)
- **V3** : automatiser la collecte des AO (connecteur mail ou scraper de plateforme)
- **V4** : notification Slack/Teams + validation humaine formalisée
- **V5** : logs/observabilité pour mesurer la pertinence du score dans le temps
