# Guide technique

## Moteur NLP
Le moteur `HybridTicketScorer` combine :
- une vectorisation TF-IDF sur le sujet et le contenu,
- un modèle de classification statistique pour la catégorie,
- un modèle de classification statistique pour la priorité,
- des règles métier pour l'urgence et l'escalade de priorité,
- un résumé extractif simple,
- un score de confiance calculé à partir des probabilités et des boosts métiers.

## Services
- `auth_service.py` : authentification, autorisations et session.
- `ticket_service.py` : création, scoring, correction et lecture.
- `import_service.py` : ingestion CSV/JSON.
- `dashboard_service.py` : indicateurs et statistiques.
- `audit_service.py` : journal des actions et événements.
- `settings_service.py` : paramètres configurables.

## Sécurité implémentée
- sessions Flask côté serveur,
- jeton CSRF maison pour tous les formulaires critiques,
- mots de passe hashés avec Werkzeug,
- validation de longueur côté serveur,
- requêtes SQL paramétrées,
- séparation des rôles admin / analyst / viewer.
