# SupportPulse AI – Dossier projet complet

## A. Présentation du projet
**Nom** : SupportPulse AI – Scoreur intelligent de tickets support

**Contexte** : Les équipes support reçoivent des volumes croissants de tickets hétérogènes. Sans tri automatisé, la priorisation et l'orientation dépendent fortement de l'expérience humaine et augmentent les délais de réponse.

**Problématique** : Comment analyser automatiquement des tickets support afin d'accélérer le tri, l'attribution et la décision de traitement, tout en conservant une logique explicable dans un MVP crédible ?

**Objectifs** :
- catégoriser automatiquement les tickets,
- estimer priorité et urgence,
- générer un résumé opérationnel,
- proposer une équipe de traitement,
- fournir un score de confiance et des motifs,
- historiser et corriger les résultats.

**Utilisateurs cibles** : support managers, analystes support, product ops, fondateurs de startup SaaS, jury académique.

**Cas d'usage** : réception de tickets, import de backlog, revue d'escalades, démonstration produit, portfolio senior.

**Proposition de valeur** : un mini SaaS démonstratif, moderne et compréhensible, combinant expérience B2B, scoring NLP hybride et traçabilité métier.

## B. Analyse fonctionnelle
### Besoins fonctionnels
- authentification par rôles,
- création manuelle et import en lot,
- scoring automatique,
- liste filtrable,
- détail avec explication,
- correction manuelle,
- dashboard et statistiques,
- audit et paramètres.

### Besoins non fonctionnels
- interface professionnelle,
- architecture modulaire,
- sécurité minimale sérieuse,
- démontrabilité rapide,
- documentation exploitable,
- maintenabilité.

### Workflow utilisateur
Connexion → consultation dashboard → ajout/import → scoring → revue du ticket → correction éventuelle → suivi statistiques/logs.

### Workflow d'analyse
Ticket brut → nettoyage texte → vectorisation → prédiction statistique → règles métier urgence/priorité → résumé → confiance → stockage → affichage.

### Scénario complet
Un administrateur importe 50 tickets CSV. Chaque ticket est stocké, scoré puis visible dans le tableau. Un analyste ouvre un ticket critique, lit l'explication, ajuste la catégorie si besoin, puis l'action apparaît dans l'audit.

## C. Vision ingénieur expérimenté
- séparation claire des responsabilités entre routes, services et base,
- validation systématique des entrées,
- code commenté de façon utile et non verbeuse,
- fonctions courtes et explicites,
- usage systématique des paramètres SQL,
- journalisation des actions sensibles,
- structure réutilisable pour itérations futures.

## D. Vision architecte expérimenté
Le projet met en place une architecture en couches avec un moteur de scoring isolé du web. Les dépendances restent simples : Flask orchestre les vues et invoque les services, le moteur NLP ne dépend pas de Flask, SQLite stocke l'historique et les prédictions. Cette séparation facilite le remplacement futur du moteur ou du stockage.

## E. Vision UI/UX expérimentée
L'interface privilégie une sidebar sobre, des cartes KPI lisibles, des tableaux avec badges, un formulaire d'ajout assisté par prévisualisation, et un détail ticket structuré pour rendre visible la logique de scoring. L'esthétique vise un rendu corporate crédible, avec palette maîtrisée, espacements généreux et faible charge cognitive.

## F. Base de données
### Tables
- `users`
- `categories`
- `priorities`
- `urgency_levels`
- `settings`
- `tickets`
- `imports`
- `ticket_predictions`
- `ticket_corrections`
- `audit_logs`

### Relations
- `tickets.created_by` → `users.id`
- `ticket_predictions.ticket_id` → `tickets.id`
- `ticket_predictions.processed_by` → `users.id`
- `ticket_corrections.ticket_id` → `tickets.id`
- `ticket_corrections.corrected_by` → `users.id`
- `imports.created_by` → `users.id`
- `audit_logs.actor_id` → `users.id`

Le SQL complet est fourni dans `database/schema.sql`.

## G. Code source complet
Le dossier contient tout le code nécessaire pour exécuter le projet localement : backend Flask, services Python, moteur de scoring, templates, CSS, JS, SQL, scripts d'initialisation et fichiers Docker.

## H. Données de démonstration
- `data/training_examples.json` pour entraîner les modèles de démonstration.
- `data/demo_tickets.csv` et `data/demo_tickets.json` pour alimenter la base.
- Comptes de démonstration déjà fournis.

## I. Documentation
- README général
- guide d'installation
- guide utilisateur
- guide technique
- documentation d'architecture
- documentation sécurité

## J. Vérification finale
- Cohérence fonctionnelle : oui
- Compatibilité fichiers/services : oui
- Démontrabilité locale : oui
- Documentation exploitable : oui
- UI/UX professionnelle : oui
- Extensibilité future : oui

## Pistes d'amélioration
- moteur ML enrichi par annotations réelles,
- endpoints API REST,
- authentification SSO,
- commentaires internes et SLA,
- notifications e-mail/Slack,
- indicateurs de productivité support.
