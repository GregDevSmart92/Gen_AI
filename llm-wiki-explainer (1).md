# Le pattern *LLM Wiki* — une alternative au RAG vectoriel pour le grounding

*Document de formation — méthodes de grounding et de retrieval. Cas d'étude : un repo de veille technologique réel.*

---

## 1. Objet de ce document

Ce document explique une **méthode de grounding** (ancrage des réponses d'un LLM dans une connaissance fiable) qui ne repose **pas** sur le RAG vectoriel classique : le pattern *LLM Wiki* proposé par Andrej Karpathy en avril 2026.

Plutôt que de rester abstrait, il s'appuie sur un **cas réel décrit en détail** : un repo de veille technologique (IA, data, conformité, cybersécurité) construit exactement selon ce pattern. Le repo n'est pas exécuté ici — il sert d'**exemple tangible** pour montrer comment le retrieval y est pensé sans base vectorielle, ce que ça change, et quand l'approche gagne ou perd face au RAG.

À la fin, vous saurez : (1) pourquoi le RAG vectoriel plafonne sur certaines questions, (2) ce qu'est un *compounding artifact* et pourquoi c'est le cœur de l'idée, (3) comment un retrieval **symbolique/structuré** remplace les embeddings, (4) ce qu'on gagne et perd à se contenter d'un **simple index** plutôt que d'un wiki complet, et (5) à quelle échelle basculer vers du GraphRAG.

---

## 2. Le problème de fond : grounding et retrieval

Un LLM seul génère à partir de ses poids : connaissance figée à l'entraînement, non vérifiable, sujette à hallucination.

- **Grounding** = ancrer ses réponses dans une connaissance externe fiable et à jour.
- **Retrieval** = la mécanique qui va chercher la bonne connaissance, au bon moment, pour la fournir au modèle.

### La baseline : le RAG vectoriel

L'approche dominante est le **RAG** (Retrieval-Augmented Generation) :

```
documents bruts → découpage en chunks → embeddings (vecteurs) stockés en base
   ── puis, à CHAQUE question ──
question → embedding → recherche par similarité → top-k chunks → injectés dans le prompt → réponse
```

Ça marche, et c'est souvent le bon choix. Mais le RAG porte des limites structurelles qu'il faut connaître :

- **Aucune accumulation.** Le LLM *redécouvre* la connaissance à chaque question. Rien ne se construit dans le temps ; le même travail de recherche/synthèse est refait à chaque fois.
- **Chunks opaques et arbitraires.** Le découpage est *lossy* : un chunk peut couper une idée en deux, perdre le contexte de son paragraphe, ou mélanger deux sujets. La taille de chunk est un compromis bancal.
- **Similarité ≠ pertinence.** La recherche ramène ce qui *ressemble* à la question. Un passage sémantiquement proche peut être hors-sujet ; un passage vraiment pertinent mais formulé autrement peut être manqué.
- **Pas de multi-hop** (voir encadré ci-dessous) — la limite la plus importante.
- **Liens entre concepts non matérialisés.** Les relations entre documents sont reconstruites à la volée à chaque query, jamais écrites une bonne fois.
- **Contradictions non suivies.** Si une source récente contredit une ancienne, le RAG n'en sait rien : il ramène les deux chunks sans arbitrer.
- **Coût d'infrastructure.** Base vectorielle, pipeline d'embeddings, ré-indexation à chaque mise à jour des sources.
- **Faible auditabilité.** Les vecteurs sont opaques : difficile de voir *pourquoi* tel chunk a été retrouvé.

> **C'est quoi le multi-hop ?**
> Le **multi-hop** (raisonnement multi-sauts) désigne une question dont la réponse exige d'**enchaîner plusieurs faits dispersés** dans plusieurs documents. Exemple : *« Quel est le point commun entre l'outil cité dans l'article A et le cabinet mentionné dans l'article C ? »* — il faut trouver A → isoler l'outil → suivre un lien vers B → puis vers C, et seulement là conclure.
> Le RAG vectoriel récupère les passages *qui ressemblent à la question*. Or les **maillons intermédiaires** (B, le lien A→B) ne ressemblent pas à la question : ils sont donc **invisibles** pour la recherche par similarité. Le RAG échoue sur ce type de question.
> Un wiki où ces liens sont **déjà écrits noir sur blanc** résout le problème : le saut est matérialisé, il n'est plus à redécouvrir.

---

## 3. La réponse : le pattern *LLM Wiki* (Karpathy)

> *Idea file* original : **https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f**

Karpathy publie volontairement une **idée** (un *idea file* à copier-coller dans son propre agent), pas un repo de code. L'idée :

> Plutôt qu'un LLM qui **redécouvre** la connaissance à chaque query, un LLM qui **construit et maintient incrémentalement un wiki Markdown persistant** — une collection de fichiers structurés et interconnectés qui s'intercale entre vous et les sources brutes.

Quand on ajoute une source, le LLM ne se contente pas de l'indexer : il la **lit, en extrait l'essentiel, et l'intègre** au wiki existant — il met à jour les pages concernées, révise les synthèses, signale les contradictions avec d'anciennes affirmations. La connaissance est **compilée une fois, puis tenue à jour** — pas re-dérivée à chaque question.

### L'idée-clé : un artefact qui *compose dans le temps* (compounding)

> *« The wiki is a persistent, compounding artifact. The cross-references are already there. The contradictions have already been flagged. »*

C'est tout le renversement. Là où le RAG repart de zéro à chaque query, le wiki **s'enrichit** à chaque source ajoutée et à chaque question posée. Les cross-références sont **déjà faites**. La synthèse reflète déjà tout ce qui a été lu.

**Point central : le LLM construit son propre wiki pour mieux s'y retrouver ensuite.** Le travail d'organisation (résumer, relier, classer, tenir les renvois) est fait *au moment de l'ingestion*, par le LLM lui-même, dans un format qu'il saura re-naviguer. Le retrieval futur devient une simple lecture d'un texte déjà structuré — pas une fouille dans des fragments bruts. Karpathy résume le rapport de rôles ainsi : *« Obsidian is the IDE; the LLM is the programmer; the wiki is the codebase. »*

### Trois idées portantes

1. **« The schema is the product ».** Ce qui transforme un LLM générique en *travailleur de la connaissance discipliné*, ce n'est pas la techno de stockage — c'est le **document de conventions** (le *schema*) qui lui dit *comment* maintenir le wiki : structure des pages, format des entrées, workflows d'ingestion/réponse/maintenance. C'est le fichier de config central.
2. **Filiation avec le Memex (Vannevar Bush, 1945).** L'idée d'une station de connaissance personnelle, curatée, où *les liens entre documents valent autant que les documents*. Bush n'a jamais résolu une chose : **qui fait la maintenance des liens ?** Un humain s'épuise — *« Humans abandon wikis because the maintenance burden grows faster than the value. LLMs don't get bored. »* Le LLM fait cette corvée à coût ≈ 0, donc le wiki **reste à jour**.
3. **Partager une spec plutôt qu'un code.** À l'ère des agents, partager l'**idée** a plus de valeur que partager une implémentation : l'agent de chacun instancie la version qui colle à son besoin. Ce document, et le repo de veille décrit plus bas, sont précisément une de ces instanciations.

---

## 4. L'architecture en 3 couches

Le pattern impose une séparation stricte :

| Couche | Rôle | Qui écrit |
|---|---|---|
| **Raw sources** | Documents bruts, **immuables** (articles, PDFs, transcripts). La *source of truth*. Le LLM les lit, ne les modifie jamais. | l'humain (collecte) |
| **Le wiki** | Fichiers Markdown générés : résumés, pages d'entité, pages de concept, comparaisons, synthèses, interconnectés. | **le LLM** (entièrement) |
| **Le schema** | Le document de conventions (`CLAUDE.md`, `AGENTS.md`…) qui dit *comment* maintenir le wiki. | l'humain + le LLM (co-évolution) |

Deux fichiers de service complètent le dispositif :

- **`index.md`** — catalogue orienté contenu : chaque page listée avec un lien et un résumé d'une ligne. Le LLM le lit **en premier** pour router sa recherche. (Suffit jusqu'à ~100 sources d'après Karpathy ; au-delà on ajoute un vrai moteur de recherche, ex. l'outil open-source *qmd* : recherche hybride BM25 + vectorielle, on-device.)
- **`log.md`** — journal chronologique *append-only* : trace des ingestions, questions, passes de maintenance.

---

## 5. Étude de cas : un repo de veille construit sur ce pattern

### L'objectif du repo

C'est une **veille technologique et marché** (IA/LLM, data science, conformité réglementaire, cybersécurité IA, analyse concurrentielle). But affiché : **pas l'exhaustivité, mais la synthèse critique** — lecture argumentée d'articles, d'outils et d'acteurs jugés pertinents, avec marquage systématique des affirmations chiffrées et recadrage de la hype. La KB est privée et conçue pour être **auto-portante** : un humain ou un agent peut reprendre la veille après des mois sans briefing.

### L'arborescence

```
veille/
├── README.md           # index / point d'entrée  → joue le rôle de l'index.md du pattern
├── CLAUDE.md           # LE SCHEMA : conventions, format d'entrée, workflows, ton critique
├── log.md              # journal chronologique append-only
├── tags.md             # référentiel de tags typés (taxonomie)
│
├── ia-llm.md           # ┐
├── data-science.md     # │
├── concurrence.md      # │  LE WIKI : fichiers thématiques multi-entrées
├── cybersecurite-ia.md # │  (chaque entrée = une mini-page wiki)
├── conformite-ia.md    # ┘
├── outils.md           # glossaire des technos citées (fiches avec licence + provenance)
├── benchmarks.md       # suites d'évaluation
│
├── sources/            # LA COUCHE RAW : PDFs + textes capturés VERBATIM, immuables
└── artefacts/          # livrables dérivés de la KB (ce document en fait partie)
```

### La correspondance avec les 3 couches

- **Raw sources** → le dossier `sources/`. Chaque texte ingéré y est capturé **verbatim intégral** (jamais résumé à la capture), avec un en-tête de provenance (auteur, URL, date, méthode de capture).
- **Le wiki** → les fichiers thématiques (`ia-llm.md`, `concurrence.md`…). Différence assumée avec le wiki « pur » de Karpathy : ici une page n'est pas « une entité = un fichier », mais **un fichier thématique contenant N entrées**, chacune étant une mini-page. Choix adapté à une veille de taille humaine. Le plus gros fichier (`ia-llm.md`) est lui-même organisé en **7 clusters** thématiques avec un sommaire en tête.
- **Le schema** → `CLAUDE.md` (+ `tags.md` pour la taxonomie). C'est la couche *« schema is the product »*.

### Ce que contient le schema (`CLAUDE.md`), en substance

C'est le contrat qui rend la KB disciplinée. Il fixe notamment :

- **Un format canonique d'entrée** : titre = *concept* (pas le titre racoleur de l'article, pour pouvoir regrouper plusieurs sources sous une entrée évolutive) ; puis Source(s), Date de publication, Résumé hiérarchisé (thèse → développement → « à retenir » actionnable), cross-réfs internes, tags.
- **Un workflow d'ingestion** en étapes : capturer le raw verbatim → choisir le fichier cible → rédiger l'entrée → créer/mettre à jour la fiche de chaque outil cité → poser les tags (depuis le référentiel) → tisser les cross-références → logger → commit.
- **Un workflow de maintenance (*lint*)** : repérer tags orphelins, cross-réfs cassées, chiffres non sourcés, sources manquantes.
- **Un ton critique** : marquer toute affirmation chiffrée et sa source (« claim à vérifier » sinon), distinguer source primaire et secondaire, restituer les contre-arguments, **ne jamais inventer** un chiffre ou une citation non vus.
- **Une discipline de tags** : un référentiel unique, réutilisation par défaut, création en dernier recours.

L'intérêt : n'importe quel agent qui lit ce schema avant d'agir produit des entrées **cohérentes** avec les centaines déjà présentes. C'est ce qui fait *composer* la KB dans le temps.

---

## 6. Le cœur pédagogique : comment se fait le retrieval, concrètement

Le retrieval dans ce repo est **symbolique et structuré**, pas vectoriel. Quand on pose une question, le chemin est :

```
1. Lire l'index (README) ......... identifier la thématique
2. Ouvrir le fichier thématique ... (ex. ia-llm.md)
3. Lire le sommaire / les clusters . choisir le bon cluster
4. Lire l'entrée .................. suivre ses cross-réfs internes ("cf. notre entrée X")
5. Rebondir ....................... vers la fiche outil / la fiche acteur liée
```

Le **schema et les liens** font le travail que les embeddings font dans le RAG. La structure est *portée par le texte lui-même* (titres, clusters, tags, et surtout des cross-références **en prose qui expliquent pourquoi le lien existe**) — donc lisible et navigable par un humain comme par un agent. C'est exactement le point du §3 : le LLM a construit cette structure pour mieux s'y retrouver ensuite.

### Un troisième terme : le *simple index* (le juste milieu)

Entre le RAG vectoriel et le wiki complet, il existe une troisième voie, souvent suffisante : le LLM ne construit qu'un **index** des documents bruts — un catalogue où *un document = une ligne* (titre + résumé d'une phrase + métadonnées) — **sans rédiger de pages de synthèse**. À la question, le LLM lit l'index, repère les documents pertinents, **les ouvre en entier**, et répond à partir du texte brut.

C'est une **synthèse paresseuse** (faite au dernier moment) là où le wiki fait une **synthèse anticipée** (faite une fois, à l'ingestion). La bonne question pour les départager : **où paie-t-on le coût de synthèse ?**

- **RAG vectoriel** — à chaque query, sur des fragments opaques.
- **Index LLM** — à chaque query, sur des documents entiers (mais bien routés).
- **LLM Wiki** — **une seule fois**, à l'ingestion, et toutes les queries suivantes en profitent.

Ce que l'index simple gagne, et ce qu'il perd :

- **+ Ingestion quasi gratuite** : ajouter une source = ajouter une ligne. Pas de mise à jour de 10-15 pages ni de réconciliation de cross-réfs.
- **+ Plus de documents avant saturation du contexte** : une ligne par document pèse très peu, donc on peut cataloguer beaucoup plus de sources avant que l'index lui-même ne remplisse la fenêtre de contexte.
- **+ Zéro perte, zéro péremption** : on lit la source telle quelle au moment de répondre ; aucune synthèse intermédiaire ne peut devenir obsolète ou fausse.
- **− Pas de *compounding*** : l'index **route** mais ne **digère** pas. Liens, contradictions et synthèse ne sont pas pré-calculés ; le LLM doit re-lire les docs et re-synthétiser à chaque question — l'aide au retrieval n'est **pas permanente** (c'est le point faible que le wiki corrige).
- **− Coût reporté sur la query** : ouvrir plusieurs documents entiers consomme bien plus de contexte par question que lire quelques entrées déjà condensées. L'index échange une ingestion bon marché contre des **requêtes chères** ; le wiki fait l'inverse.
- **− Multi-hop non matérialisé** : l'index dit *quels* documents existent, pas *comment* ils se relient.

### Les trois approches, côte à côte

| Dimension | RAG vectoriel | Index LLM (simple) | LLM Wiki |
|---|---|---|---|
| Ce que le LLM construit | embeddings de chunks | catalogue (1 ligne/doc) | pages de synthèse interconnectées |
| Unité lue à la query | chunks similaires | documents bruts entiers | entrées condensées + liens |
| Quand a lieu la synthèse | à chaque query | à chaque query | **une fois, à l'ingestion** (compounding) |
| Routage | similarité cosinus | LLM lit l'index | LLM suit index → clusters → cross-réfs |
| Liens entre concepts | reconstruits à la volée | non matérialisés | **matérialisés** dans le texte |
| Multi-hop | échoue | possible mais re-fait à chaque fois | **natif** (sauts écrits) |
| Contradictions | non suivies | repérées si docs co-lus | **flaguées à l'ingestion** |
| Coût d'ingestion | moyen (pipeline embeddings) | **quasi nul** | élevé (maj de N pages) |
| Coût par query | faible | **élevé** (lit des docs entiers) | faible (lit des synthèses) |
| Docs avant saturation contexte | très élevé | **élevé** | plus limité |
| Infra requise | base vectorielle + embeddings | fichiers seuls | fichiers + git |
| Auditabilité | faible (vecteurs opaques) | bonne (source brute) | **forte** (diff git) |

### Les limites du LLM Wiki (ne pas le survendre)

- Pas de query **structurée multi-hop programmatique** ni de *typed edges* traversables par machine (un graphe sait faire ça, pas un wiki).
- Pas de fusion de rang type RRF.
- **Ingestion coûteuse** : chaque source touche plusieurs pages — l'inverse de l'index simple.
- **Scaling borné** : au-delà de quelques milliers de pages, le LLM ne peut plus charger l'ensemble en contexte, et le routage par lecture d'index atteint sa limite — d'où l'ajout d'un moteur de recherche (qmd…).

### Choisir sur le spectre

- **Beaucoup de documents, questions ponctuelles, fidélité à la source prioritaire** → **index simple**. On paie peu à l'ingestion, on relit la source à la demande.
- **Corpus relu souvent, questions de synthèse ou multi-hop, valeur dans les connexions** → **LLM Wiki**. On paie la synthèse une fois, toutes les queries suivantes en profitent.
- **Très gros corpus hétérogène, recherche par similarité, pas de structure éditoriale** → **RAG vectoriel** (ou en complément d'un index).
- **Échelle entreprise, requêtes structurées multi-hop programmatiques** → **GraphRAG** (knowledge graph + ontologie + typed edges + retrieval hybride, exposé aux agents via MCP).

Le pont conceptuel à retenir : **le schema d'un LLM Wiki *est* déjà une ontologie lightweight, écrite en prose.** Index, wiki et GraphRAG sont des points d'un même spectre — même principe (matérialiser de plus en plus de structure pour ne pas la redécouvrir), à des niveaux de formalisation croissants.


---

## Références

- **LLM Wiki — Andrej Karpathy** (idea file, avril 2026) : https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
