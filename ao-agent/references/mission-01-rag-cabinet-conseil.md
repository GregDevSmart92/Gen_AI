# Mission : Assistant RAG interne pour un cabinet de conseil

Client : cabinet de conseil en stratégie (environ 150 collaborateurs).

Contexte : les consultants perdaient un temps important à rechercher des informations
dans une base documentaire mal indexée (SharePoint). L'objectif était de donner accès
aux méthodologies internes, anciennes missions et référentiels de compétences via un
assistant conversationnel.

Réalisation : mise en place d'un pipeline RAG complet (extraction des documents,
chunking, embeddings, indexation dans une base vectorielle Qdrant, reranking), connecté
à la source documentaire existante, avec une interface de chat web simple. Gouvernance
des accès mise en place pour que chaque utilisateur ne voie que les documents auxquels
il a droit.

Résultat : temps de recherche divisé par 5 sur les demandes courantes, forte adoption
par les équipes juniors dès les premières semaines.

Expertises mobilisées : RAG / retrieval, base vectorielle Qdrant, gouvernance des accès,
connecteur SharePoint.
