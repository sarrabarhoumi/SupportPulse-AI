# Guide d'installation

1. Installer Python 3.11+.
2. Créer un environnement virtuel.
3. Installer les dépendances avec `pip install -r requirements.txt`.
4. Initialiser la base avec `python scripts/init_db.py`.
5. Lancer l'application avec `python app.py`.
6. Ouvrir `http://127.0.0.1:5000`.

## Vérifications
- Le fichier `storage/supportpulse.db` doit être créé.
- La page de connexion doit afficher les comptes de démo.
- Le dashboard doit contenir déjà plusieurs tickets importés.
