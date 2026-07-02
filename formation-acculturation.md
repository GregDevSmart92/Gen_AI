# Formation / Acculturation à l'agentique — corpus de concepts

> **Objet.** Corpus de concepts clés de l'IA agentique, chacun avec une mini-storyline pour l'introduire/l'expliquer. Source réutilisable pour différents supports : slides, talks, one-pagers, interventions, formation Qualiopi.
>
> **Méthode.** Boule de neige. Chaque concept porte des **bullet points concis** : les messages/explications clés, au niveau acculturation. On enrichira ensuite (analogies travaillées, exemples chiffrés, visuels).
>
> **Statut.** Passe de contenu en cours. On scindera en répertoire multi-fichiers plus tard, au passage à la rédaction détaillée.

## Légende des niveaux

- `[A]` — acculturation pure (accessible à tous)
- `[A+]` — acculturation un peu technique
- `[E]` — expert (renvoyé en annexe, hors cœur)

---

## Fil rouge

> Un LLM seul ne sait qu'écrire — il **hallucine** et n'a pas accès à vos **données métier**. Pour en faire un collaborateur fiable on l'**ancre** dans vos données (grounding/retrieval), on lui donne des **outils + une boucle** (agent), on **vérifie** qu'on peut lui faire confiance (eval **+ contrôle humain**), et on l'**encadre** (sécurité, conformité, **gouvernance**). Et pour bâtir **VOTRE** agentique adaptée à votre contexte, on commence par la **gouvernance** qui en dessine la forme.

### Storyline map — chaque chapitre répond à une question ouverte par le précédent

| Ch. | Chapitre | Question |
|-----|----------|----------|
| 0 | Introduction | *Une révolution à saisir : de quoi parle-t-on ?* |
| 1 | Fondations | *Qu'est-ce que cette machine ?* |
| 2 | Histoire | *D'où ça vient, pourquoi maintenant ?* |
| 3 | Économie & frugalité | *Combien ça coûte (€ et planète), et faut-il le plus gros modèle ?* |
| 4 | Le paysage des modèles | *Qui propose quoi, et où sont mes données ?* |
| 5 | Grounding & retrieval | *Comment lui faire servir MES données/règles sans qu'il hallucine ?* |
| 6 | Agent & harnais | *Comment il passe de l'écriture à l'action ?* |
| 7 | Évaluation & confiance | *Comment lui faire confiance — machine ET humain ?* |
| 8 | Sécurité, conformité & gouvernance | *Comment l'encadrer : dangers, loi, responsabilités ?* |
| 9 | Construire son agentique | *Comment bâtir LE mien, adapté à mon contexte ? → gouvernance d'abord* |

---

## Ch.0 — Introduction

> *Une révolution à saisir : de quoi parle-t-on ?*

### Une révolution à saisir `[A]`
- En quelques années, la machine est devenue capable de **manier le langage humain** — une rupture du même ordre que l'arrivée d'internet.
- L'enjeu n'est pas de « suivre une mode » mais de **saisir une révolution** pendant qu'elle se construit.
- Ce corpus donne le **vocabulaire commun** pour décider, encadrer et construire — au niveau intuition, sans être technique.

### Du langage à un système à construire `[A]`
- Un **LLM** (modèle de langage) nous apporte la **puissance du langage**.
- Avec le langage, on peut **communiquer, raisonner et donner des ordres**.
- Mais la richesse du langage est aussi sa faiblesse : **puissant mais ambigu** — une même phrase peut être comprise de dix façons, donc difficile à maîtriser.
- Un **LLM nu** ne fait que produire du **texte plausible** : il discute d'**informations généralistes, non sourcées** (hors de votre contexte pro), il **hallucine**, et surtout **il n'agit pas**.
- Pour le rendre **opérationnel et maîtrisable**, on construit autour de lui : l'**ancrer** (grounding), l'**outiller** (agent), le **vérifier** (eval), l'**encadrer** (gouvernance).
- Message clé : **le pouvoir réside dans le système construit autour du modèle, avant le modèle lui-même.**
- Et ce système, **il faut le construire pour VOTRE organisation** (→ ch.9).

---

## Ch.1 — Fondations : c'est quoi une IA générative ?

> *Qu'est-ce que cette machine ?*

### LLM `[A]`
- *Large Language Model* : un modèle entraîné à **prédire le mot (token) suivant**, à partir de ce qu'il a appris d'énormes corpus de texte.
- Ce n'est ni une base de connaissances ni un moteur de recherche : c'est un **générateur de texte probabiliste**.
- Sa force = le langage (raisonner, reformuler, synthétiser, donner des ordres) ; sa limite aussi : dès qu'il faut du 100 % exact, il faut l'outiller.

### Token `[A]`
- Unité de découpage du texte manipulée par le modèle ; en gros **1 token ≈ un mot** (souvent un morceau de mot).
- Tout se compte en tokens : ce qu'on envoie (entrée) **et** ce qu'il génère (sortie).
- C'est l'unité de **facturation** et la **limite** de la fenêtre de contexte (cf. ch.3).

### Entraînement & inférence `[A+]`
- On **entraîne** le modèle sur d'**énormes corpus** : il ajuste ses **poids** pour apprendre le langage et des connaissances générales — ce sont ses **connaissances internes**.
- Puis il **infère** : à chaque requête, il **calcule les tokens les plus probables** à partir de ce qu'il a appris.
- Deux régimes très différents : l'**entraînement** (une fois, énorme, fait par le fournisseur) vs l'**inférence** (à chaque usage, payée par vous).
- Ces connaissances internes sont **figées à une date** (*knowledge cutoff*) et **moyennées** : ni à jour, ni spécifiques à votre métier → d'où le besoin de **grounding** (ch.5).
- Chaque inférence = un coût (tokens, énergie) — cf. ch.3.

### Fenêtre de contexte `[A]`
- C'est la **mémoire de travail** : tout ce que le modèle a sous les yeux pour répondre. On y met : l'**instruction initiale** (rôle, consignes), la **question**, ses **connaissances internes**, le **résultat des outils** (morceaux de documents, sorties d'exécution) et le **dialogue** en cours.
- Objectif : qu'il s'appuie **le moins possible sur ses connaissances internes** (généralistes, faillibles) et **le plus possible sur les éléments fournis** (sourcés).
- **Limitée** en taille (en tokens) : il faut **laisser de la place** pour le raisonnement, le dialogue et l'exécution des outils.
- Aucune mémoire entre deux conversations : hors de la fenêtre, le modèle oublie.
- La remplir avec **trop de choses** dilue la pertinence → réponses approximatives, voire **hallucination** (section suivante).
- *(Renvoi : c'est l'**agent** et sa boucle d'outils qui remplissent progressivement cette fenêtre — détaillé au ch.6.)*

### Hallucination `[A]`
- Le modèle produit une affirmation **fausse mais formulée avec assurance**.
- Causes : il optimise la **plausibilité** du texte (pas la vérité), et/ou une **fenêtre de contexte trop remplie** (dilution).
- Risque majeur dès qu'on lui fait confiance sans vérification ni sources.
- Antidote : l'ancrer dans des faits (grounding, ch.5) et vérifier (ch.7) — un bon contexte fait chuter le taux d'erreur (ordre de grandeur observé : ~40 % → ~5 %, voire 0 %).

### Déterminisme & température `[A+]`
- Un LLM est **probabiliste** : à question identique, deux réponses peuvent différer.
- La **température** règle l'aléa : basse = stable/répétable ; haute = le modèle **pioche dans les réponses moins probables** (créatif/varié).
- Les extrêmes nuisent : **trop basse**, le modèle se répète/tourne en rond ; **trop haute**, les réponses deviennent instables et inexploitables.
- Implication : reproductibilité limitée → ça compte pour les tests et la confiance (ch.7).

### Embeddings `[A+]`
- Transformer un texte en une **liste de nombres** (vecteur) qui capture son **sens**.
- Deux textes proches en sens → vecteurs proches : on peut mesurer une **proximité sémantique**.
- Brique de base de la recherche sémantique et du RAG (ch.5).
- Effet utile : « voiture » et « automobile » deviennent proches, même sans mots communs.

### Multimodalité `[A]`
- Au-delà du texte, les modèles comprennent/produisent aussi **image, audio, voix, code**.
- Ouvre des usages : lire un document scanné, décrire une photo, dialoguer à la voix.
- Le langage reste le pivot, mais les entrées/sorties se diversifient.

### Modèles de raisonnement `[A+]`
- Certains modèles « **réfléchissent avant de répondre** » : ils déroulent des **étapes intermédiaires** avant la réponse finale.
- Meilleurs sur les tâches complexes (maths, code, planification, analyse).
- Coût : plus de temps et de tokens → à réserver quand la tâche le justifie (frugalité, ch.3).

---

## Ch.2 — Histoire : de ChatGPT à l'agentique

> *D'où ça vient, pourquoi maintenant ?*

### De ChatGPT à l'agentique `[A]`
- **2017** : l'architecture *Transformer* rend les modèles de langue scalables.
- **2022** : ChatGPT ouvre le **dialogue naturel** avec un modèle, grand public — c'est le **chatbot** : il répond avec ses connaissances figées.
- **2025** : les **assistants** se connectent (web, vos fichiers, vos données) et produisent des livrables.
- **2026** : les **agents** reçoivent un objectif et **enchaînent des outils en autonomie** jusqu'au résultat (détail ch.6).

---

## Ch.3 — Économie & frugalité

> *Combien ça coûte (€ et planète), et faut-il le plus gros modèle ?*

### Les coûts `[A]`
- Deux coûts **très différents** : **entraîner** le modèle (une fois, énorme) vs l'**utiliser/inférence** (à chaque requête).
- À l'inférence on paie **au token**, et le token **généré** (sortie) coûte typiquement bien plus cher que le token **ingéré** (entrée).
- Donc : un prompt long coûte, mais une réponse longue coûte **davantage**.
- Ordre de grandeur : facturation en **$ par million de tokens**, très variable selon le modèle.

### Frugalité `[A]`
- Plus un modèle est **puissant**, plus il est **cher, lent et lourd** ; or **toutes les tâches n'en ont pas besoin**.
- Frugalité = choisir le **bon modèle pour la bonne tâche**, moduler la dépense.
- **Frontier models** (les plus puissants, chers) vs **petits modèles** (ex. 7B : moins chers, rapides, hébergeables localement) : beaucoup de cas se traitent très bien avec un **petit modèle bien groundé/outillé**.
- Gain double : **coût** et **empreinte**.

### Empreinte environnementale `[A]`
- L'IA consomme **énergie et eau** (refroidissement des datacenters) — à l'entraînement comme à l'usage.
- Ordres de grandeur (à sourcer avant diffusion) : entraîner un grand modèle ≈ **~1 000 MWh** et **plusieurs centaines de tonnes de CO₂** (≈ des centaines d'allers-retours transatlantiques) ; une requête à un assistant ≈ **~0,3 Wh** (quelques secondes d'une ampoule LED) et **quelques mL d'eau**.
- L'entraînement = gros **pic ponctuel** ; l'inférence = minuscule à l'unité mais **massivement répétée** — c'est le volume qui pèse.
- Levier direct : la **frugalité**.

### Souveraineté & lock-in `[A+]`
- Beaucoup de modèles leaders sont **hébergés hors UE**, sous juridictions étrangères.
- Dépendre d'un seul fournisseur = risque de **lock-in** (prix, disponibilité, conditions).
- Enjeux : où vont les données, conformité (ch.8), capacité à **changer** de fournisseur.
- Alternatives : open weights, hébergement local/européen, architecture portable (infra : cf. ch.4).
- **Au cœur de la souveraineté : la protection des données** — confier ses données métier à un modèle hébergé hors UE, c'est les exposer à un autre droit et perdre la maîtrise de leur usage (cf. RGPD, ch.8).

---

## Ch.4 — Le paysage des modèles

> *Qui propose quoi, et où sont mes données ?*

### Les principaux fournisseurs `[A]`
- **Anthropic** (Claude), **OpenAI** (GPT), **Google** (Gemini), **Mistral** (FR/UE), **Meta** (Llama, open), **DeepSeek**…
- Ils se distinguent par : qualité de raisonnement, sécurité/valeurs, prix, ouverture, langues, localisation.
- **La course des modèles** : ils se dépassent à tour de rôle, nouveaux modèles tous les quelques mois.
- Pas de « meilleur » absolu : **ça dépend de l'usage** et des contraintes.

### Deux façons de consommer un modèle : API hébergée vs auto-hébergé `[A]`
- **Propriétaire via API** : le modèle reste **chez le fournisseur** (ex. Claude, GPT), **facturé à l'usage / au token** ; vos **données transitent** vers lui (souvent hors UE).
- **Open weights auto-hébergé** : on télécharge les **poids** et on l'héberge soi-même (ex. Llama, Mistral, DeepSeek) ; **données chez vous**, mais on **porte le coût d'inférence et d'infra**.
- Arbitrage : simplicité + qualité de pointe (API) vs contrôle + confidentialité + souveraineté (auto-hébergé).
- La vraie question : **où tournent les données**, et est-ce compatible avec vos exigences (ch.8) ?

### Infrastructure : GPU/CPU `[A+]`
- Entraînement et inférence tournent surtout sur des **GPU** (processeurs massivement parallèles), bien plus efficaces que les CPU pour ça.
- C'est la **ressource rare et chère** : à la source du coût et de l'empreinte (ch.3), et un enjeu de **souveraineté** (qui possède les GPU).
- Auto-héberger un modèle = **disposer de (et payer) ces GPU**.

---

## Ch.5 — Ancrer le modèle : grounding & retrieval

> *Comment lui faire servir MES données/règles sans qu'il hallucine ?*

### Grounding / ancrage / sourcing `[A]`
- Grounding = **ancrer** le modèle dans des faits/règles fiables au moment de répondre.
- Concrètement : injecter dans la fenêtre de contexte **juste ce qu'il faut**, ni trop ni trop peu.
- C'est **LE** remède à l'hallucination — et surtout ce qui rend la solution **opérationnelle et pertinente** pour votre métier. C'est l'un des **4 piliers du harness** (ch.6).
- « Sourcing » : on peut **citer** d'où vient l'info → traçabilité et confiance.

### Le continuum : prompt → retrieval → (fine-tuning) `[A]`
- Trois leviers pour spécialiser un modèle, **du plus léger au plus lourd**.
- **Prompt** : bien formuler/instruire — gratuit, immédiat, à essayer en premier.
- **Retrieval** : aller chercher les bonnes infos et les fournir — le cœur du grounding.
- **Fine-tuning** : réentraîner — coûteux, **rarement nécessaire**.
- Règle : ne monter en lourdeur **que si** le niveau précédent ne suffit pas.

### Prompt engineering `[A]`
- Art de **bien formuler la demande** : objectif, contexte, format attendu, exemples.
- Levier le plus **rentable** : gratuit, instantané, gros effet sur la qualité.
- Bonnes pratiques : être explicite, donner des exemples, découper la tâche.

### Retrieval & ses techniques `[A+]`
- Retrieval = **retrouver les infos pertinentes** à fournir au modèle. Plusieurs techniques, complémentaires :
	- **Mots-clés** (grep / BM25) : exact et rapide, idéal pour identifiants, noms propres, références ; sert aussi à **identifier les documents/morceaux à charger**.
	- **Index** : organiser les contenus comme une **bibliothèque** pour retrouver vite.
	- **Proximité sémantique (RAG)** : découper le corpus en morceaux et donner au modèle les bouts les plus **proches du sens** de la question ; surtout utile sur **gros corpus / besoin d'exactitude** (ex. juridique).
	- **Graphe** : exploiter les **relations** entre entités pour un raisonnement multi-étapes.
- Le bon système **combine** souvent plusieurs techniques (hybride).

### Base de connaissance & mémoire `[A+]`
- Pour bien retrouver, il faut une **base de connaissance structurée et fiable**, pas juste un tas de documents.
- **Garbage in, garbage out** est encore plus vrai ici : une base fausse ou mal organisée = des réponses fausses, avec assurance.
- **Graphe de connaissance / ontologie / couche sémantique** = décrire les entités, le jargon, les relations de votre métier.
- C'est **« le guidebook de l'IA de votre organisation »** : la partition commune qui évite que les agents dérivent (hallucinent).
- Lié à la **mémoire** : ce qui persiste au-delà d'une conversation.
- Bonne nouvelle : **l'agentique elle-même aide à construire et maintenir** ce guidebook.

### Fine-tuning `[A+]`
- **Réentraîner** partiellement un modèle sur vos données pour l'adapter (style, format, domaine).
- Coûteux, fige des données, demande expertise et maintenance.
- **Très rarement nécessaire** : prompt + retrieval couvrent la grande majorité des besoins.
- Pertinent surtout pour un style/format très spécifique ou des contraintes fortes.

---

## Ch.6 — L'agent et son harnais

> *Comment il passe de l'écriture à l'action ?*

### Agent `[A]`
- Un agent = **un LLM + des outils + une boucle + un objectif**.
- Il ne se contente pas de répondre : il **agit** (cherche, calcule, écrit des fichiers, appelle des API).
- Autonomie **encadrée** : il décide des étapes pour atteindre le but fixé.
- C'est le passage **« de l'écriture à l'action »**.

### Tool use / loop `[A]`
- **Tool use** : on donne au modèle des **outils** qu'il peut appeler (recherche, code, connecteurs).
- **Loop** : il appelle un outil → **observe** le résultat → décide de l'étape suivante → recommence jusqu'au but.
- Cette boucle est ce qui rend un agent capable de tâches **multi-étapes**.
- Chaque tour consomme tokens et temps **et remplit la fenêtre de contexte** (cf. ch.1)

### Human-in-the-loop & niveaux d'autonomie `[A]`
- On règle le **curseur d'autonomie** : du « propose et je valide » au « agis seul ».
- **Human-in-the-loop** = un humain valide les étapes sensibles (envoi, suppression, dépense).
- Plus l'action est **risquée/irréversible**, plus on garde l'humain dans la boucle.
- C'est un choix de **gouvernance** (ch.8/9), pas seulement technique.

### Harness & ses 4 piliers `[A+]`
- Le **modèle seul n'est pas opérationnel** ; le harness = tout ce qu'on assemble autour pour le rendre utile.
- **4 piliers** : 
	- **grounding** (mémoire + contexte métier)
	- **outils** (ce qu'il peut faire)
	- **environnement d'exécution** (où il tourne/agit) 
	- **interface** (par où on lui parle).
- La puissance réelle vient de la **qualité de l'assemblage**, pas seulement du modèle.
- Les sections suivantes détaillent chaque pilier — le **grounding** étant traité au **ch.5**.

### Pilier *outils* — ce que l'agent peut faire `[A+]`
- **Catégories d'outils** :
	- **Basiques** : lire/écrire des fichiers, **recherche web**, **exécuter du code**, **créer des artefacts** (pptx, docx, tableurs)…
	- **Connecteurs aux composants du SI** : messagerie, bases de données, GED… pour **agir sur vos systèmes**.
	- **Outils de workflow** : outils plus élaborés (ou enchaînements d'outils) qui réalisent un **workflow** complet.
	- **Sous-agents** : déléguer une sous-tâche à un agent spécialisé (cf. multi-agents plus bas).
- **Brancher un outil — CLI & MCP** : il faut un **standard de branchement**. **CLI** = une commande que l'agent déclenche ; **MCP** = un protocole standardisé pour exposer outils/données (la « prise standard »). Un **format commun** pour brancher sans tout réinventer.
- Distinguer **ce que fait** l'outil (catégorie) de **comment on le branche** (CLI/MCP).

### Pilier *environnement d'exécution* — où il tourne et agit `[A+]`
- L'endroit où l'agent **exécute** réellement ses actions : ton **ordinateur** (local), une **sandbox cloud**, un **conteneur**…
- **Permanent ou éphémère** ; plus ou moins ouvert (accès aux fichiers, au réseau, droit d'exécuter du code).
- C'est ce qui détermine ce que la **puissance** et le **périmètre** de l'agent — et la **surface de risque** (cf. ch.8).

### Pilier *interface* — par où on lui parle `[A]`
- Comment on interagit avec l'agent : **chat web**, **application desktop**, **terminal / CLI**, **extension IDE** (VSCode…), **add-in Office**…
- Chaque interface **ouvre ou limite** des usages (mobilité, accès aux fichiers locaux, intégration au poste de travail).
- Même modèle, expériences très différentes selon l'interface.


---

## Ch.7 — Évaluer & faire confiance

> *Comment lui faire confiance — machine ET humain ?*

### Eval des systèmes IA `[A+]`
- Évaluer = **mesurer objectivement** si le système fait bien le travail.
- Distinguer **model evals** (benchmarks génériques du modèle) et **app evals** (la fiabilité de **VOTRE** système sur **VOS** cas).
- Sert à **observer, surveiller, tracer** le système, l'**auto-améliorer**, et le **monitorer** en production.
- Sans eval, on pilote à l'aveugle.

### Benchmarks & leur piège `[A]`
- Les benchmarks comparent les modèles sur des tests standardisés — utile mais **limité**.
- Piège : **90 % en démo ≠ 90 % en prod** (souvent bien moins sur vos données réelles).
- Parfois « appris » par les modèles → scores gonflés.
- Surtout : **un modèle moyen avec un bon harness > le meilleur modèle avec un harness bâclé**.
- À utiliser comme **indice**, jamais comme garantie.

### LLM-as-a-judge vs human-as-judge `[A+]`
- Pour noter des réponses, deux juges : un **LLM** (rapide, scalable, mais bruité) ou un **humain** (fiable, mais lent et cher).
- En pratique, **approche hybride** : le LLM dégrossit, l'humain arbitre les cas clés et **cale** le juge IA.
- Toujours garder un **human-in-the-loop** sur ce qui compte.
- Penser à « **évaluer l'évaluateur** » : aligner le juge IA sur le jugement humain.

### Observabilité / monitoring `[A]`
- **Voir ce que fait l'agent** : ses étapes, ses appels d'outils, ses coûts, ses erreurs.
- Indispensable en production pour détecter dérives, hallucinations, surcoûts.
- Donne la **traçabilité** (« pourquoi l'IA a fait ça ? ») nécessaire à la confiance et à l'audit.
- Essentiel aussi pour l'**auto-évaluation → auto-amélioration** du système.

---

## Ch.8 — Sécurité, conformité & gouvernance

> *Comment l'encadrer : dangers, loi, responsabilités ?*

### Double casquette de la sécurité `[A]`
- Deux risques distincts à gérer **ensemble** :
	- **Cyber classique** : accès, secrets, droits, surface d'attaque (comme tout logiciel).
	- **Risque propre à l'IA** : comportement du modèle (hallucination, manipulation, fuite via le contexte) — et, technologie nouvelle oblige, une **nouvelle surface d'attaque** avec de **nouveaux types d'attaques**.
- Un système peut être « sécurisé » côté cyber **et** dangereux côté comportement — il faut **les deux**.

### Panorama des dangers du LLM `[A]`
- **Prompt injection** : des instructions cachées dans une entrée détournent le modèle (« ignore tes consignes… »).
- **Fuite de données** : le modèle révèle des infos sensibles de son contexte ou de son entraînement.
- **Hallucination** : production de faux présentés comme vrais.
- **Supply chain** : modèles, plugins ou données d'entraînement compromis.
- **Déni de service** : requêtes conçues pour être coûteuses en calcul.

### Guardrails `[A]`
- **Garde-fous** qui filtrent/valident les entrées et surtout les **sorties** de l'agent.
- Exemples : interdire certaines actions, bloquer des contenus, exiger une validation humaine (ex. les *hooks* de Claude Code qui interceptent une action avant exécution).
- Complètent le grounding : on **cadre** ce que l'agent a le droit de dire et de faire.

### Red teaming `[A+]`
- **Attaquer volontairement** son propre système pour trouver les failles avant les autres.
- Inclut prompt injections, tentatives de fuite, scénarios adverses multi-tours.
- Démarche **continue**, pas un audit one-shot.
- Objectif : **durcir** avant la mise en production.

### IA Act & RGPD `[A]`
- **IA Act** : règlement européen qui classe les usages par **niveau de risque** (inacceptable / élevé / limité / minimal), avec des obligations **selon l'usage** — c'est l'**usage** qui détermine le niveau, pas la techno.
- **Usages interdits** (risque inacceptable) : notation sociale, manipulation subliminale, exploitation de personnes vulnérables, reconnaissance des émotions au travail/à l'école, identification biométrique de masse en temps réel dans l'espace public…
- **Usages à haut risque** (annexe III) : recrutement/RH, accès au crédit & à l'assurance, éducation/examens, services publics essentiels, justice, migration/frontières, infrastructures critiques, biométrie.
- **RGPD** : protection des données personnelles — données traitées, base légale, traçabilité, durée de conservation.
- Vigilance : beaucoup de modèles sont **hébergés hors UE** (cf. souveraineté, ch.3).

### Gouvernance & contrôle humain `[A]`
- **Gouvernance = décider quelle sera l'IA de notre organisation** : quels axes prioritaires ? jusqu'où va-t-on (performante / conforme / sécurisée) ?
- **Pour quels usages je veux absolument de l'IA ? Pour quels usages je n'en veux pas ?**
- Définir **où et comment** l'IA intervient, avec quelles **règles** et **responsabilités** : qui valide quoi, qui est responsable, ce qui est interdit, ce qui est tracé.
- Le **contrôle humain** reste central sur les décisions sensibles.
- C'est le socle qui rend l'IA **déployable, responsable, sûre — maîtrisée** → amorce du ch.9.

---

## Ch.9 — Construire son propre agentique adapté à son contexte

> *Comment bâtir LE mien, adapté à mon contexte ? → gouvernance d'abord*

### Gouvernance d'abord : définir son IA `[A]`
- **Avant de coder, on pose la gouvernance** (cf. ch.8) : c'est elle qui **dessine la forme** du système.
- Périmètre d'intervention, règles, responsabilités, garde-fous.
- La gouvernance est « **première** » pour *construire*, même si on l'a vue en dernier dans le parcours.

### Le changement de démarche : socle IA d'abord, cas d'usage ensuite `[A]`
- **Ancienne démarche** : choisir un workflow et l'**accélérer** avec de la bonne data + éventuellement de l'IA.
- **Nouvelle démarche** : poser un **socle d'IA générative maîtrisable** — un **SIA** (système d'information agentique) sur une **data structurée et déjà automatisée au maximum** — puis **absorber les cas d'usage** dessus, les uns après les autres.
- La **structuration du SI et de la data** peut elle-même se faire avec des **outils agentiques**.
- L'état d'esprit : **réfléchir à toutes les tâches opérationnelles dont on peut s'affranchir.**
- La **priorisation** des cas d'usage peut rester **ROIste** (impact × faisabilité), mais ce n'est plus le point de départ.

### Assembler les briques `[A]`
- On recompose tout le parcours : **grounding** (ch.5) → **agent/harnais** (ch.6) → **eval** (ch.7) → **sécurité/gouvernance** (ch.8).
- Concrètement : **mettre à disposition un système (multi-)agent**, le **grounder petit à petit** et l'**outiller** pour qu'il prenne en charge **de plus en plus de workflows**.
- Construire **portable et observable**, pour durer et évoluer.