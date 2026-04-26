# Architecture

## Vision architecte expérimenté
L'application est organisée en couches :
1. **Présentation** : templates Jinja + Bootstrap + jQuery.
2. **Contrôle applicatif** : routes Flask dans `app.py`.
3. **Logique métier** : services Python modulaires.
4. **Scoring / NLP** : `services/scoring_engine.py`.
5. **Accès aux données** : `services/db.py` + SQLite.
6. **Sécurité / audit** : `auth_service.py` et `audit_service.py`.

## Flux principal
Saisie ticket → validation → persistance `tickets` → scoring hybride → persistance `ticket_predictions` → mise à jour du ticket → affichage du résultat dans l'interface et alimentation des KPI.

## Extensibilité
Le projet peut évoluer vers :
- API REST versionnée,
- PostgreSQL,
- modèle spaCy ou transformers,
- file d'attente Celery/RQ,
- RBAC avancé,
- multitenant.
