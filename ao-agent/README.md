# Agent de pré-qualification d'AO — V5

Agent IA qui prend un appel d'offres (PDF, TXT ou MD) et produit une note de synthèse markdown
(résumé, score de pertinence, red flags, références internes à mobiliser, ébauche de plan de
réponse) pour l'équipe business development de Soma Smart.

Depuis la V2, c'est un **vrai agent** : Claude dispose d'outils (recherche sémantique dans les
anciennes missions, vérification de budget) et décide lui-même quand et comment les utiliser dans
une boucle, plutôt que de recevoir des données pré-calculées par le code.

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
(modèle local `all-MiniLM-L6-v2`, via sentence-transformers/PyTorch) et les indexe dans une base
Qdrant locale (`qdrant_data/`, non versionnée). À relancer à chaque fois que vous ajoutez ou
modifiez une mission de référence — la commande réindexe tout depuis zéro à chaque exécution.

> **Premier lancement : accès réseau nécessaire.** Le modèle d'embedding (~90 Mo) est téléchargé
> une seule fois puis mis en cache localement. Si votre réseau bloque les téléchargements externes,
> cette étape échouera tant que ce n'est pas résolu — les analyses elles-mêmes (appel à Claude)
> n'ont pas ce problème puisqu'elles passent par HTTPS normal comme le reste de l'agent.
>
> **Choix technique (PyTorch plutôt que FastEmbed/onnxruntime) :** sur certains postes Windows
> verrouillés (pas de droits admin), `onnxruntime` échoue au chargement avec une erreur de DLL
> native (`DLL load failed... Le module spécifié est introuvable`) faute de pouvoir installer le
> Visual C++ Redistributable. PyTorch embarque son propre runtime dans son paquet et évite
> généralement ce problème. Contrepartie : installation plus lourde (~500 Mo-1 Go).

## Analyser un AO

```bash
ao-agent samples/exemple_ao.txt
```

Options :
- `--profile <chemin>` : utiliser un autre profil entreprise (YAML)
- `--model <id>` : changer de modèle Claude (par défaut `claude-opus-4-8`)
- `--output <chemin>` : chemin du fichier markdown de sortie (par défaut `outputs/<nom>-<date>.md`)
- `--db-path <chemin>` : chemin de la base Qdrant si vous en utilisez une autre que celle par défaut
- `--verbose` : affiche en direct les appels d'outils de l'agent (utile pour voir la boucle en action)

La note est affichée dans le terminal et sauvegardée dans `outputs/`.

## Comment fonctionne la boucle agent (V2)

1. Claude reçoit le texte de l'AO
2. Il décide d'appeler `chercher_references_internes` avec une requête ciblée (et peut la
   raffiner ou en essayer une autre s'il n'est pas satisfait des résultats)
3. Si un budget est mentionné, il appelle `verifier_budget` (calcul déterministe en code, pas
   un jugement du modèle)
4. Une fois qu'il a assez d'informations, il rédige la note finale et arrête d'appeler des outils
5. Une limite de 6 itérations protège contre une boucle qui ne se terminerait pas

Avec `--verbose`, vous voyez chaque appel d'outil s'afficher au fur et à mesure, par exemple :
```
[outil] chercher_references_internes({'requete': 'assistant RAG connecté à SharePoint'})
[outil] verifier_budget({'budget_eur': 50000})
```

## Veille automatique sur le BOAMP (V3)

```bash
ao-agent-collect --dry-run
```

Interroge l'API ouverte du BOAMP (Bulletin officiel des annonces de marchés publics, hébergée
par la DILA) avec les mots-clés définis dans `config/veille.yaml`, et liste les nouvelles
annonces trouvées sans les analyser (`--dry-run`). Relancez sans `--dry-run` pour analyser
automatiquement chaque nouvelle annonce (même pipeline que `ao-agent`, avec RAG et outils) et
sauvegarder une note par annonce dans `outputs/`. Les annonces déjà traitées sont mémorisées
(`state/boamp_seen.json`) pour ne pas les ré-analyser à la prochaine exécution.

> ⚠️ **Non vérifié en conditions réelles pendant le développement** — l'environnement de dev
> n'a pas accès au réseau externe nécessaire pour tester l'API BOAMP. Le code a été écrit de
> façon robuste (plusieurs noms de champs candidats essayés, texte brut de l'annonce conservé
> en repli si un champ attendu manque) et testé avec des réponses simulées, mais **testez
> `--dry-run` en premier chez vous** avant de compter dessus régulièrement. Si l'API renvoie un
> format différent de ce qui est attendu, `boamp.py` est le seul fichier à ajuster.

Options : `--limit <n>` (nombre max d'annonces récupérées), `--veille-config <chemin>`,
`--seen-path <chemin>`, `--profile`/`--model`/`--db-path`/`--verbose` (identiques à `ao-agent`).

## Notification Teams + validation humaine (V4)

### Configurer la notification Teams

Le format du message est défini par l'agent (pas imposé par Microsoft) — vous devez juste
créer un flux Teams qui l'accepte, une seule fois :

1. Dans le canal Teams où vous voulez recevoir les notifications, cliquez sur **···** (Plus
   d'options) → **Workflows**
2. Cherchez le modèle **"Publier dans un canal lorsqu'une requête webhook est reçue"** (ou
   équivalent en anglais : *"Post to a channel when a webhook request is received"*)
3. Quand on vous demande un exemple de contenu JSON pour définir le schéma, collez :
   ```json
   {"ao": "exemple_ao.txt", "resume": "...", "score": "5 - ...", "fichier": "outputs/exemple_ao-....md"}
   ```
4. Reliez les champs `ao`, `resume`, `score`, `fichier` au message posté dans le canal
5. Copiez l'URL de webhook générée dans `.env` :
   ```
   TEAMS_WEBHOOK_URL=https://...
   ```

> ⚠️ Microsoft a fait évoluer ce mécanisme récemment (les anciens "Connectors" webhook sont
> dépréciés au profit de l'app Workflows/Power Automate) — les noms exacts des menus peuvent
> varier légèrement selon votre version de Teams. Si `TEAMS_WEBHOOK_URL` n'est pas défini, les
> notifications sont simplement désactivées (rien ne bloque le reste de l'agent).

Une fois configuré, `ao-agent` et `ao-agent-collect` envoient automatiquement une notification
après chaque note générée (objet de l'AO, résumé, score, chemin du fichier). Désactivable avec
`--no-notify`.

### Enregistrer une décision humaine formalisée

```bash
ao-agent-validate outputs/exemple_ao-20260708.md --decision go --commentaire "Bon fit expertises" --auteur "Prénom Nom"
```

Enregistre la décision (`go` / `no-go` / `a-clarifier`) dans un journal horodaté et traçable
(`state/decisions.jsonl`, un JSON par ligne), au lieu d'une décision informelle non tracée.

## Observabilité (V5)

Chaque analyse (`ao-agent` ou `ao-agent-collect`) est désormais enregistrée automatiquement dans
`state/analysis_log.jsonl` : score donné par l'agent, modèle utilisé, outils appelés, tokens
consommés, durée. Pas de configuration nécessaire, ça marche dès l'installation.

```bash
ao-agent-report
```

Affiche des statistiques agrégées : nombre d'analyses, score moyen, tokens et durée totale/moyenne,
et surtout **le score moyen de l'agent par décision humaine** (en croisant avec
`state/decisions.jsonl` de la V4) — la vraie mesure de la V5 : *le score que donne l'agent
correspond-il à ce que les humains décident au final ?* Si le score moyen des AO validés "go" est
nettement supérieur à ceux en "no-go", le score fait son travail ; sinon, c'est un signal pour
revoir le prompt ou la grille de scoring.

## Structure

```
ao-agent/
├── config/
│   ├── company_profile.yaml   # profil entreprise (secteurs, budget, expertises, red flags)
│   └── veille.yaml             # mots-clés de veille BOAMP
├── references/                 # anciennes missions (corpus indexé par le RAG)
├── samples/
│   └── exemple_ao.txt         # AO fictif pour tester sans PDF
├── src/ao_agent/
│   ├── extract.py             # extraction de texte (PDF via PyMuPDF, TXT/MD brut)
│   ├── llm.py                 # appel à l'API Claude (avec ou sans outils)
│   ├── tools.py                # définition des outils + exécution (recherche, budget)
│   ├── analyze.py             # prompt système + boucle agentique
│   ├── cli.py                 # point d'entrée : analyse d'un AO
│   ├── notify.py               # notification Teams
│   ├── validation.py           # journal des décisions humaines
│   ├── validate_cli.py         # point d'entrée : ao-agent-validate
│   ├── observability.py        # journal des analyses (score, tokens, durée)
│   ├── report.py               # croisement analyses × décisions humaines
│   ├── report_cli.py           # point d'entrée : ao-agent-report
│   ├── rag/
│   │   ├── chunking.py        # découpage des documents en paragraphes
│   │   ├── embeddings.py      # génération d'embeddings (sentence-transformers)
│   │   ├── vectorstore.py     # client Qdrant (indexation + recherche)
│   │   └── ingest.py          # point d'entrée : indexation des références
│   └── collectors/
│       ├── boamp.py            # connecteur API BOAMP
│       ├── seen_store.py       # suivi des AO déjà traités
│       └── cli.py              # point d'entrée : veille + analyse automatique
├── qdrant_data/                 # base vectorielle locale (non versionné)
├── state/                       # suivi BOAMP, décisions, journal d'analyses (non versionné)
└── outputs/                    # notes générées (non versionné)
```

## Roadmap

- ~~**V1** : RAG sur d'anciennes missions/références (Qdrant) pour ancrer le score de pertinence~~ ✅
- ~~**V2** : transformer en véritable agent (boucle d'outils : recherche interne, scoring, génération)~~ ✅
- ~~**V3** : automatiser la collecte des AO (connecteur BOAMP)~~ ✅
- ~~**V4** : notification Teams + validation humaine formalisée~~ ✅
- ~~**V5** : logs/observabilité pour mesurer la pertinence du score dans le temps~~ ✅
