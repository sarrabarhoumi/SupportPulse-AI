import json
import os
import time
from collections import defaultdict

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from config import DATA_DIR, ENGINE_VERSION
from services.utils.text_processing import clean_text, normalize_text, summarize_text

CATEGORY_KEYWORDS = {
    'bug': ['bug', 'erreur', 'anomalie', 'crash', 'exception'],
    'incident': ['panne', 'indisponible', 'interruption', 'incident', 'ralentissement'],
    'facturation': ['facture', 'paiement', 'abonnement', 'remboursement', 'tarif'],
    'acces': ['connexion', 'mot de passe', 'acces', 'permission', 'verrouille'],
    'demande_information': ['comment', 'documentation', 'question', 'explication', 'aide'],
    'technique': ['api', 'integration', 'webhook', 'sdk', 'configuration'],
    'reclamation': ['mecontent', 'inadmissible', 'plainte', 'reclamation', 'decu'],
    'suggestion': ['suggestion', 'amelioration', 'idee', 'proposer', 'feature'],
}

TEAM_MAPPING = {
    'bug': 'Equipe Produit',
    'incident': 'Support N2',
    'facturation': 'Equipe Finance',
    'acces': 'Support IAM',
    'demande_information': 'Customer Success',
    'technique': 'Support Technique',
    'reclamation': 'Customer Care',
    'suggestion': 'Equipe Produit',
}

POSITIVE_WORDS = {
    'merci', 'apprecie', 'satisfait', 'super', 'parfait', 'excellent', 'bravo'
}

NEGATIVE_WORDS = {
    'urgent', 'bloque', 'mecontent', 'inadmissible', 'impossible', 'panne',
    'critique', 'decu', 'erreur', 'probleme', 'echec', 'remboursement',
    'double prelevement', 'debite deux fois', 'indisponible', 'plainte',
    'reclamation', 'lent', 'lenteur', 'resiliation'
}

class HybridTicketScorer:
    def __init__(self):
        training_path = os.path.join(DATA_DIR, 'training_examples.json')
        with open(training_path, 'r', encoding='utf-8') as handle:
            data = json.load(handle)
        texts = [clean_text(item['subject'] + '. ' + item['content']) for item in data]
        category_labels = [item['category'] for item in data]
        priority_labels = [item['priority'] for item in data]
        self.category_model = Pipeline([
            ('tfidf', TfidfVectorizer(ngram_range=(1, 2), min_df=1, max_features=6000)),
            ('clf', LogisticRegression(max_iter=1000)),
        ])
        self.priority_model = Pipeline([
            ('tfidf', TfidfVectorizer(ngram_range=(1, 2), min_df=1, max_features=6000)),
            ('clf', LogisticRegression(max_iter=1000)),
        ])
        self.category_model.fit(texts, category_labels)
        self.priority_model.fit(texts, priority_labels)
        self.version = ENGINE_VERSION

    def _keyword_scores(self, text):
        normalized = normalize_text(text)
        scores = defaultdict(float)
        for category, words in CATEGORY_KEYWORDS.items():
            for word in words:
                if word in normalized:
                    scores[category] += 0.15
        return scores

    def _urgency_from_rules(self, text, customer_email=''):
        normalized = normalize_text(text)
        strong = ['urgent', 'bloque', 'impossible', 'production', 'panne', 'indisponible', 'critique', 'securite']
        medium = ['rapidement', 'aujourdhui', 'avant midi', 'client', 'des que possible']
        if any(word in normalized for word in strong):
            return 'elevee'
        if any(word in normalized for word in medium):
            return 'normale'
        if customer_email.endswith('@grande-entreprise.com') or customer_email.endswith('@client-premium.fr'):
            return 'elevee'
        return 'basse'

    def _sentiment(self, text):
        normalized = normalize_text(text)

        strong_negative = [
            'debite deux fois',
            'double prelevement',
            'remboursement',
            'impossible',
            'bloque',
            'panne',
            'indisponible',
            'inadmissible',
            'resiliation'
        ]

        if any(term in normalized for term in strong_negative):
            return 'negatif'

        pos = sum(1 for word in POSITIVE_WORDS if word in normalized)
        neg = sum(1 for word in NEGATIVE_WORDS if word in normalized)

        if neg > pos:
            return 'negatif'
        if pos > neg and neg == 0:
            return 'positif'
        return 'neutre'

    def _priority_from_rules(self, category, text, urgency):
        normalized = normalize_text(text)
        if urgency == 'elevee' and any(word in normalized for word in ['production', 'securite', 'indisponible', 'panne']):
            return 'critique'
        if category in {'incident', 'acces'} and urgency == 'elevee':
            return 'haute'
        if category in {'bug', 'facturation', 'reclamation', 'technique'}:
            return 'haute' if urgency in {'normale', 'elevee'} else 'moyenne'
        if category in {'demande_information', 'suggestion'}:
            return 'faible' if urgency == 'basse' else 'moyenne'
        return 'moyenne'

    def _collect_reasons(self, text, category, priority, urgency):
        normalized = normalize_text(text)
        reasons = []
        for keyword in CATEGORY_KEYWORDS.get(category, []):
            if keyword in normalized:
                reasons.append(f"Mot-clé détecté pour la catégorie : {keyword}")
        if priority in {'haute', 'critique'}:
            reasons.append('Le contenu indique un impact opérationnel ou une forte attente client.')
        if urgency == 'elevee':
            reasons.append("Des marqueurs d'urgence ont été repérés dans le ticket.")
        if not reasons:
            reasons.append('La classification provient principalement du modèle statistique entraîné sur le jeu de démonstration.')
        return reasons[:4]

    def analyze(self, subject, content, customer_email=''):
        start = time.perf_counter()
        merged = clean_text(f"{subject}. {content}")
        category_probs = self.category_model.predict_proba([merged])[0]
        categories = list(self.category_model.classes_)
        boosts = self._keyword_scores(merged)
        combined = {label: float(category_probs[i]) + boosts.get(label, 0.0) for i, label in enumerate(categories)}
        category = max(combined, key=combined.get)

        priority_probs = self.priority_model.predict_proba([merged])[0]
        priorities = list(self.priority_model.classes_)
        ml_priority = priorities[int(priority_probs.argmax())]
        urgency = self._urgency_from_rules(merged, customer_email)
        rules_priority = self._priority_from_rules(category, merged, urgency)

        priority_rank = {'faible': 1, 'moyenne': 2, 'haute': 3, 'critique': 4}
        priority = rules_priority if priority_rank[rules_priority] >= priority_rank[ml_priority] else ml_priority

        sentiment = self._sentiment(merged)
        summary = summarize_text(content or subject)
        reasons = self._collect_reasons(merged, category, priority, urgency)
        confidence = round(min(0.98, max(combined.values()) * 0.72 + max(priority_probs) * 0.18 + 0.10), 2)

        return {
            'category': category,
            'priority': priority,
            'urgency': urgency,
            'summary': summary,
            'sentiment': sentiment,
            'confidence_score': confidence,
            'suggested_team': TEAM_MAPPING.get(category, 'Support General'),
            'reasons': reasons,
            'explanation': ' ; '.join(reasons),
            'processing_time_ms': int((time.perf_counter() - start) * 1000),
            'engine_version': self.version,
        }


SCORER = HybridTicketScorer()
