# SupportPulse AI – Scoreur intelligent de tickets support

SupportPulse AI est un mini SaaS de démonstration conçu pour analyser automatiquement des tickets support et leur attribuer une catégorie, une priorité, un niveau d'urgence, un résumé, un sentiment, une équipe de traitement suggérée et un score de confiance.

## Stack
- Backend : Python 3 + Flask
- NLP / scoring : Python, scikit-learn, règles métier hybrides
- Frontend : HTML5, CSS3, Bootstrap 5, jQuery, JavaScript
- Base de données : SQLite

## Installation rapide
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows
pip install -r requirements.txt
python scripts/init_db.py
python app.py
```

Application : http://127.0.0.1:5000

## Comptes de démonstration
- Admin : admin@supportpulse.local / Admin123!
- Analyste : analyste@supportpulse.local / Analyst123!
- Lecteur : viewer@supportpulse.local / Viewer123!

## Structure
- `app.py` : point d'entrée Flask
- `services/` : logique métier, scoring, sécurité, audit, import
- `database/schema.sql` : schéma relationnel
- `data/` : jeu de données d'entraînement et tickets de démonstration
- `templates/` et `static/` : interface UI/UX
- `docs/` : documentation fonctionnelle, technique, architecture et sécurité

## Documentation détaillée
- `docs/guide-installation.md`
- `docs/guide-utilisateur.md`
- `docs/guide-technique.md`
- `docs/architecture.md`
- `docs/securite.md`
- `docs/dossier-projet-complet.md`
