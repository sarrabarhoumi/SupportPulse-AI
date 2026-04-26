# SupportPulse AI

**SupportPulse AI** est une plateforme de démonstration orientée **scoring intelligent de tickets support**.  
Le projet simule un mini SaaS capable d’analyser automatiquement des demandes clients afin d’aider les équipes support à mieux **qualifier**, **prioriser** et **traiter** les tickets.

L’application produit notamment :
- une **catégorie**
- une **priorité**
- un **niveau d’urgence**
- un **résumé automatique**
- un **sentiment**
- une **équipe de traitement suggérée**
- un **score de confiance**

---

## Aperçu du projet

Dans de nombreux environnements support, les tickets arrivent en volume, avec des niveaux de qualité variables et des urgences parfois mal identifiées.  
**SupportPulse AI** a été conçu comme une réponse démonstrative à ce besoin métier : proposer une première couche d’analyse automatique, lisible et exploitable, tout en conservant la possibilité de correction humaine.

Ce projet a été pensé comme un livrable crédible pour :
- un **portfolio développeur**
- un **projet de fin d’études**
- un **MVP de démonstration**
- une **présentation technique ou produit**

---

## Fonctionnalités principales

### Gestion des tickets
- création manuelle de tickets
- import en lot via **CSV** ou **JSON**
- consultation de la liste des tickets
- recherche, tri et filtrage
- détail complet d’un ticket
- historique des analyses

### Analyse intelligente
- classification automatique de la **catégorie**
- estimation de la **priorité**
- estimation du **niveau d’urgence**
- génération d’un **résumé automatique**
- calcul d’un **score de confiance**
- détection simple du **sentiment**
- proposition d’une **équipe de traitement**
- affichage des **raisons détectées** en mode transparence

### Pilotage et visualisation
- tableau de bord global
- indicateurs clés de suivi
- graphiques de répartition
- activité récente
- statistiques globales
- historique des imports

### Administration
- gestion des utilisateurs
- consultation des logs
- configuration de certains paramètres fonctionnels
- correction manuelle des prédictions

---

## Stack technique

### Backend
- **Python 3**
- **Flask**

### NLP / Scoring
- **Python**
- **scikit-learn**
- règles métier hybrides
- prétraitement textuel simple

### Frontend
- **HTML5**
- **CSS3**
- **Bootstrap 5**
- **JavaScript**
- **jQuery**
- **Chart.js**

### Base de données
- **SQLite**

---

## Architecture générale

Le projet est structuré autour de plusieurs couches afin de garder une séparation claire des responsabilités :

- **présentation** : templates HTML et assets statiques
- **backend web** : routes Flask et gestion des vues
- **logique métier** : services dédiés aux tickets, imports, dashboard, sécurité et audit
- **moteur de scoring** : classification hybride et enrichissement des tickets
- **persistance** : base SQLite et schéma relationnel versionné

Cette organisation permet une base de code plus lisible, plus maintenable et plus facile à faire évoluer.

---

## Lancement du projet

### 1. Cloner le dépôt
```bash
git clone <URL_DU_DEPOT>
cd SupportPulse-AI