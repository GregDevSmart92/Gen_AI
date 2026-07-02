# Kit Jenius — comprendre et raconter l'expérience Jenius

Ce kit donne de quoi **comprendre Jenius** (la plateforme agentique de SOMA) et **préparer le récit** d'expérience agentique pour la qualif. À lire avec `formation-acculturation.md` (le vocabulaire commun) et l'AO.

---

## 1. La vraie histoire (2 temps)

**Jenius 2025 — le produit.** Plateforme d'assistants/agents IA d'entreprise à sources personnalisées, **agnostique du modèle** (n'importe quel fournisseur LLM via API) et **agnostique de l'infra** (conteneurisée, portable cloud public/privé/on-prem).

**Les 4 axes de différenciation (l'innovation produit 2025)** — Jenius était, à notre connaissance, la première plateforme d'agents d'entreprise à combiner les 4 simultanément :

- **Marketplace d'agents privée** — scopée à l'organisation (vs marketplaces publiques).
- **Workflows multi-agents en clic-bouton, sans code** — vs concurrents qui exigent du code.
- **Gouvernance fine** — rôles, quotas, traçabilité (vs simple contrôle d'accès).
- **Portabilité totale** — cloud public / privé / on-prem, sans modif de code.

Sur ces bases, Jenius a accumulé des **briques techniques et des principes portables** (détaillés en §3-4).

**Mission 2026** — SOMA **reprend les principes portables et les briques acquis avec Jenius** (RAG/Qdrant, agents, marketplace, gouvernance, connecteurs, observabilité/évaluation) **et en développe d'autres** pour les **ré-assembler/intégrer en socle agentique — le *harness* — chez le client**. Plusieurs formes selon le client (principes **portables**, briques **agnostiques**) : socle **sur Mistral AI**, ou **framework maison basé sur LangChain**.

---

## 2. Les 2 formes d'agentique (vision à porter)

À savoir présenter — montrer qu'on **prend de la hauteur** sur l'agentique (cohérent avec la curiosité et la veille continue attendues par l'AO ; l'AO ne demande pas littéralement une « vision ») et structurer son discours :

1. **Agentique « workflow métier »** — l'agentique s'articule autour d'un **workflow métier complexe** qu'on rend plus **fluide** : **ingestion** des données, **monitoring continu**, **intervention** automatique en cas d'anomalie/défaillance, **rédaction de rapports** de suivi et finaux, intervention de l'humain pour validation/ajustement. L'agent prend en charge des étapes d'un processus défini.
   → _**C'est là où en est principalement le datalab** — le terrain concret de la mission._
2. **Assistant agentique « généraliste » maîtrisé** — intervient dans le **SI du collaborateur** ; les **workflows se construisent au fil de l'usage** (auto-apprentissage) et de l'**amélioration apportée par l'IA engineer**. Copilote transverse qui s'enrichit en continu.
   → _**Ce qu'il faut faire miroiter** — la cible désirable, la vision où on emmène le client._

---

## 3. Architecture & briques de Jenius 2025

| Couche              | Techno                                                                                                                                                                                                                                                                                             |
| ------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Framework backend   | **FrameFox** (maison, sur **FastAPI**), MVC : controllers / repositories / entities                                                                                                                                                                                                                |
| Couche agent        | **Pydantic AI** (Jenius 2025) → framework choisi par le client (Mistral Studio, LangChain)                                                                                                                                                                                                         |
| Grounding / RAG     | **Qdrant** · embeddings **HuggingFace** · chunking → 1 collection/doc + registre `jenius_registry` · **reranking** (LlamaIndex). **Flux** : `upload → MinIO → extraction (PyMuPDF) → chunking → embeddings → Qdrant → recherche sémantique → reranking → contexte injecté au LLM → réponse ancrée` |
| Protocole outils    | **MCP**  : agent consommant des **serveurs MCP locaux (stdio)**                                                                                                                                                                                                                                    |
| Stockage            | **PostgreSQL** (entités métier) · **MinIO** (fichiers, compatible S3)                                                                                                                                                                                                                              |
| Fournisseurs LLM    | **Agnostique via API** : Mistral, OpenAI, Anthropic, Groq, Gemini — catalogue configurable ; **Llama-Guard** pour garde-fous                                                                                                                                                                       |
| Connecteurs sources | BigQuery, PostgreSQL, e-mails, API, web scrapper, bibliothèque de fichiers (pdf, docx, excel, md)                                                                                                                                                                                                  |
| Fonctionnel         | Dashboard · Conversations · Workflows multi-agents · Marketplace · Sources (fichiers/web/API/DB) · **Gouvernance** (rôles, quotas, traçabilité)                                                                                                                                                    |
| Observabilité       | remontée de **métriques de gouvernance et de suivi** (usage, coûts, latence, qualité)                                                                                                                                                                                                              |
| Déploiement         | **Docker** (Python 3.13) + **Helm/Kubernetes** → portable multi-infra                                                                                                                                                                                                                              |
| CI/CD               | branches `main`/`prod` · tests black/isort/flake8 · déploiement auto sur push `prod`                                                                                                                                                                                                               |

---

## 4. Les principes portables (ce qui se transpose chez tout client)

- **Agnosticité AI framework** : couche d'abstraction multi-providers → on branche/bascule Mistral, OpenAI, Anthropic, etc. sans réécrire.
- **Agnosticité infra** : FrameFox + conteneurs → cloud public/privé/on-prem, sans modif de code.
- **Typage/signature des agents** : sorties d'agents **typées et validées** (principe qui avait conduit au choix de Pydantic AI ; réappliqué quel que soit le framework).
- **Briques réutilisables** : grounding/Graph/RAG, marketplace, workflows multi-agents, connecteurs, MCP.
- **Gouvernance** : rôles, quotas, traçabilité — un cadre de pilotage réutilisable chez tout client.
- **Observabilité** : remontée de métriques (usage, coûts, latence, qualité) pour évaluer / monitorer / améliorer en continu.
- **Souveraineté** : MCP en **stdio local** (pas de transit par une API tierce non maîtrisée) + déploiement on-prem.

---

## 5. Du 2025 au 2026 (ce qui a été appris → retranscrit dans le harness)

| Jenius 2025 (appris)           | Harness 2026 (retranscrit)                                                                                   |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------ |
| RAG vectoriel + reranking      | Grounding avancé → **mémoire en graphe** (serveur MCP **`brain`**, brique 2026 dédiée au contexte en graphe) |
| Couche agent Pydantic AI       | Framework du client : **Mistral Studio** ou **framework maison LangChain** (principe de typage conservé)     |
| Marketplace + gouvernance fine | Socle de **gouvernance + observabilité** du client, marketplace de skills et d'agent                         |
| Portabilité FrameFox           | **Principe portable**, briques agnostiques instanciées par client                                            |
| MCP (stdio local)              | **Branchement outils standardisé** du harness (CLI / MCP)                                                    |

---

## 6. Le harness 2026 — 4 piliers + observabilité (vocabulaire SOMA)

Le *harness* = tout ce qu'on assemble autour du modèle pour le rendre opérationnel et maîtrisable. **4 piliers** et une couche transverse (cf. `formation-acculturation.md`, ch.6) :

1. **Grounding** — mémoire + contexte métier (RAG/Qdrant, et **mémoire en graphe** via un serveur MCP).
2. **Outils** — ce que l'agent peut faire (connecteurs SI, workflows, sous-agents ; branchés via **CLI / MCP**).
3. **Environnement d'exécution** — où il tourne/agit (ici **Mistral AI Studio** côté CA).
4. **Interface** — par où on lui parle (chat, IDE, CLI…).
5. **Couche transverse — Observabilité** : évaluer, monitorer, améliorer en continu (traces d'appels d'agents, coûts, qualité, dérives).

---

## 7. Réservoir d'anecdotes + exercices (à choisir / compléter)

> ⚠️ Ce sont des **exemples** — tu peux en proposer d'autres issus de ton vécu.
> **Ton « expérience harness » à raconter = la/les anecdote(s) que tu choisis et expérimentes** (« reprendre les briques » est la démarche générale du cabinet ; ta mission concrète, c'est ton anecdote).

Chaque anecdote est couplée à un **exercice hands-on** sur **Mistral AI Studio** et/ou **LangChain**. Principe : **choisis** ce qui résonne avec ton expérience réelle et que tu **te sens de défendre**, puis **fais l'exercice** pour pouvoir en parler pour de vrai.

| #   | Anecdote | Exercice associé (Mistral Studio / LangChain) | Axe |
| --- | -------- | --------------------------------------------- | --- |
| A1 | **Refonte FrameFox** : Jenius installable sur n'importe quelle infra **sans modif de code** (config par env, Docker/K8s) | Conteneuriser un mini-agent (Docker) + config par variables d'env ; le faire tourner en local | Portabilité/CI-CD, AgentOps |
| A2 | **Retrieval par index « simple »** : un **index Markdown** (définitions, catalogue) chargé directement dans le contexte du modèle — souvent plus pertinent et traçable qu'un RAG vectoriel sur un corpus structuré/maîtrisé | **Mistral Studio / LangChain** : charger un index md dans le contexte d'un agent doté d'un outil pour lire les fichiers en question | Grounding, contexte ingénierie |
| A3 | **RAG vectoriel → mémoire en graphe** → gain sur questions multi-étapes | **LangChain** : mini knowledge-graph + retrieval (GraphRAG) vs RAG vectoriel _(le graphe n'est **pas natif dans Mistral Studio** → côté code/LangChain ; Mistral reste le modèle)_ | Grounding avancé, contexte ingénierie |
| A4 | **Agent sur base structurée + couche sémantique** : chatbot interrogeant **Redshift** via une **couche sémantique dbt/MetricFlow**, approche **non-text-to-SQL** (le LLM *route* vers un catalogue de requêtes pré-validées, pas de SQL libre) → fiable et auditable _(ex. mission Keobiz)_ | Exposer 2-3 *tools* à un agent (ex. `query_metric`, `run_catalog_query`) au-dessus d'une base + un mini-catalogue de définitions ; l'agent route la question vers le bon tool | Grounding/base structurée, contexte ingénierie |
| A5 | **Connexion d'outils (CLI ou MCP)** : donner à l'agent des outils à appeler — en **CLI** ou via **MCP** (stdio local, souverain). Ex. réel : `company-tools` (boond, ms, coffre…), outils CLI internes qu'un agent peut piloter | Brancher un outil à un agent — soit une **commande CLI**, soit un **serveur MCP local** — et le faire appeler dans une boucle | Agentique/outils |
| A6 | **Couche multi-providers** : bascule des modèles **sans réécriture** | **Mistral Studio** playground : même prompt sur 2 modèles, comparer coût/latence/performance ; **savoir expliquer ce qui est commun (API, prompt, tools) vs spécifique (format, params, garde-fous)** | Agentique |
| A7 | **Module de gouvernance** : dashboard usage (volume/latence/**coûts par provider**), quotas, traçabilité | Logger les appels d'un agent et construire un mini-tableau de suivi ; savoir expliquer les métriques, i.e. la définition mais aussi la pertinence pour le métier et l'admin | Gouvernance/obs |
| A8 | **Observabilité à partir des traces** : transformer des traces d'agents **nombreuses/« spaghetti »** en **observations de valeur** (dérives, goulots, erreurs récurrentes) pour surveiller et améliorer ; + **LLM-as-judge calé humain** pour détecter une dérive après changement de modèle | Exploiter un jeu de traces pour en tirer 2-3 indicateurs actionnables ; LLM-as-judge simple (LangChain) sur un jeu de réponses ; **savoir décrire les défis de l'éval** (pas de vérité unique, juge LLM bruité, dérive, coût) | Observabilité/éval |
| A9 | **Workflows multi-agents no-code** : canvas, `WorkflowConfig` JSON, moteur multi-agent | Chaîner 2-3 agents (recherche → extraction → rédaction) en **LangGraph** _ou_ Mistral Agents ; **typer les sorties de chaque agent** (reproduire l'avantage Pydantic AI : sorties validées entre étapes) | Outillage/workflow |

