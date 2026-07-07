# Agent de pré-qualification d'AO — V1

Agent IA qui prend un appel d'offres (PDF, TXT ou MD), l'analyse avec Claude à partir du profil
de Soma Smart **et** des anciennes missions pertinentes retrouvées automatiquement (RAG), et
produit une note de synthèse markdown (résumé, score de pertinence, red flags, références
internes à mobiliser, ébauche de plan de réponse).

Depuis la V1, le score de pertinence et les références citées s'appuient sur une vraie recherche
sémantique dans un corpus d'anciennes missions (`references/`), indexé dans une base vectorielle
Qdrant — plus une simple liste statique dans un fichier de config.

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

- `config/company_profile.yaml` : profil entreprise (secteurs cibles, fourchette de budget,
  expertises clés, red flags).
- `references/*.md` : vos anciennes missions/références, un fichier par mission (objet, client,
  réalisation, résultat, expertises mobilisées). Trois exemples fictifs sont fournis — remplacez-les
  par vos vraies missions.

## Indexer les références (RAG) — à faire avant la première analyse

```bash
ao-agent-ingest
```

Cette commande découpe chaque fichier de `references/` en paragraphes, calcule leurs embeddings
(modèle local, via FastEmbed) et les indexe dans une base Qdrant locale (`qdrant_data/`, non
versionnée). À relancer à chaque fois que vous ajoutez ou modifiez une mission de référence — la
commande réindexe tout depuis zéro à chaque exécution.

> **Premier lancement : accès réseau nécessaire.** Le modèle d'embedding (~80 Mo) est téléchargé
> une seule fois puis mis en cache localement. Si votre réseau bloque les téléchargements externes
> (cf. les soucis de DNS/proxy déjà rencontrés), cette étape échouera tant que ce n'est pas résolu —
> les analyses elles-mêmes (appel à Claude) n'ont pas ce problème puisqu'elles passent par HTTPS
> normal comme le reste de l'agent.

## Analyser un AO

```bash
ao-agent samples/exemple_ao.txt
```

Options :
- `--profile <chemin>` : utiliser un autre profil entreprise (YAML)
- `--model <id>` : changer de modèle Claude (par défaut `claude-opus-4-8`)
- `--output <chemin>` : chemin du fichier markdown de sortie (par défaut `outputs/<nom>-<date>.md`)
- `--db-path <chemin>` : chemin de la base Qdrant si vous en utilisez une autre que celle par défaut

La note est affichée dans le terminal et sauvegardée dans `outputs/`.

## Structure

```
ao-agent/
├── config/
│   └── company_profile.yaml   # profil entreprise (secteurs, budget, expertises, red flags)
├── references/                 # anciennes missions (corpus indexé par le RAG)
├── samples/
│   └── exemple_ao.txt         # AO fictif pour tester sans PDF
├── src/ao_agent/
│   ├── extract.py             # extraction de texte (PDF via PyMuPDF, TXT/MD brut)
│   ├── llm.py                 # appel à l'API Claude
│   ├── analyze.py             # prompt + recherche RAG + orchestration
│   ├── cli.py                 # point d'entrée : analyse d'un AO
│   └── rag/
│       ├── chunking.py        # découpage des documents en paragraphes
│       ├── vectorstore.py     # client Qdrant (indexation + recherche)
│       └── ingest.py          # point d'entrée : indexation des références
├── qdrant_data/                 # base vectorielle locale (non versionné)
└── outputs/                    # notes générées (non versionné)
```

## Roadmap (prochaines versions)

- ~~**V1** : RAG sur d'anciennes missions/références (Qdrant) pour ancrer le score de pertinence~~ ✅
- **V2** : transformer en véritable agent (boucle d'outils : recherche interne, scoring, génération)
- **V3** : automatiser la collecte des AO (connecteur mail ou scraper de plateforme)
- **V4** : notification Slack/Teams + validation humaine formalisée
- **V5** : logs/observabilité pour mesurer la pertinence du score dans le temps
