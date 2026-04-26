# Documentation sécurité

## Contrôles présents
- Hashage des mots de passe par `generate_password_hash`.
- Contrôle d'accès par rôles.
- Validation des entrées et tailles maximales.
- Requêtes SQL paramétrées pour éviter l'injection.
- Jeton CSRF sur les formulaires.
- Journal d'audit sur les connexions, créations, imports, corrections et mises à jour de paramètres.

## Recommandations futures
- Rotation du `SECRET_KEY` via variable d'environnement.
- Désactivation du mode debug en production.
- Ajout d'une limitation anti-bruteforce.
- Journalisation centralisée.
- Chiffrement applicatif de certains champs sensibles si nécessaire.
