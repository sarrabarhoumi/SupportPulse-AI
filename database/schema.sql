PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS audit_logs;
DROP TABLE IF EXISTS ticket_corrections;
DROP TABLE IF EXISTS ticket_predictions;
DROP TABLE IF EXISTS imports;
DROP TABLE IF EXISTS tickets;
DROP TABLE IF EXISTS settings;
DROP TABLE IF EXISTS urgency_levels;
DROP TABLE IF EXISTS priorities;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('admin', 'analyst', 'viewer')),
    status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'inactive')),
    last_login_at TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    team_default TEXT,
    active INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE priorities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    weight INTEGER NOT NULL
);

CREATE TABLE urgency_levels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    weight INTEGER NOT NULL
);

CREATE TABLE settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    setting_key TEXT NOT NULL UNIQUE,
    setting_value TEXT NOT NULL,
    description TEXT,
    updated_at TEXT NOT NULL
);

CREATE TABLE tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reference_code TEXT NOT NULL UNIQUE,
    source TEXT NOT NULL DEFAULT 'manual' CHECK(source IN ('manual', 'import')),
    subject TEXT NOT NULL,
    customer_name TEXT,
    customer_email TEXT,
    channel TEXT NOT NULL DEFAULT 'email',
    content TEXT NOT NULL,
    language TEXT NOT NULL DEFAULT 'fr',
    status TEXT NOT NULL DEFAULT 'new' CHECK(status IN ('new', 'analyzed', 'reviewed', 'closed')),
    predicted_category TEXT,
    predicted_priority TEXT,
    predicted_urgency TEXT,
    predicted_sentiment TEXT,
    confidence_score REAL,
    summary TEXT,
    suggested_team TEXT,
    explanation TEXT,
    processing_time_ms INTEGER,
    latest_prediction_id INTEGER,
    created_by INTEGER,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(created_by) REFERENCES users(id),
    FOREIGN KEY(latest_prediction_id) REFERENCES ticket_predictions(id)
);

CREATE TABLE imports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_name TEXT NOT NULL,
    import_type TEXT NOT NULL CHECK(import_type IN ('csv', 'json')),
    imported_count INTEGER NOT NULL DEFAULT 0,
    failed_count INTEGER NOT NULL DEFAULT 0,
    created_by INTEGER,
    created_at TEXT NOT NULL,
    FOREIGN KEY(created_by) REFERENCES users(id)
);

CREATE TABLE ticket_predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_id INTEGER NOT NULL,
    category_name TEXT NOT NULL,
    priority_name TEXT NOT NULL,
    urgency_name TEXT NOT NULL,
    sentiment TEXT,
    confidence_score REAL NOT NULL,
    summary TEXT NOT NULL,
    suggested_team TEXT,
    explanation TEXT,
    reasons_json TEXT,
    engine_version TEXT NOT NULL,
    processed_by INTEGER,
    processed_at TEXT NOT NULL,
    FOREIGN KEY(ticket_id) REFERENCES tickets(id) ON DELETE CASCADE,
    FOREIGN KEY(processed_by) REFERENCES users(id)
);

CREATE TABLE ticket_corrections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_id INTEGER NOT NULL,
    previous_category TEXT,
    previous_priority TEXT,
    previous_urgency TEXT,
    new_category TEXT,
    new_priority TEXT,
    new_urgency TEXT,
    comment TEXT,
    corrected_by INTEGER,
    corrected_at TEXT NOT NULL,
    FOREIGN KEY(ticket_id) REFERENCES tickets(id) ON DELETE CASCADE,
    FOREIGN KEY(corrected_by) REFERENCES users(id)
);

CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    actor_id INTEGER,
    action TEXT NOT NULL,
    target_type TEXT NOT NULL,
    target_id INTEGER,
    severity TEXT NOT NULL DEFAULT 'info' CHECK(severity IN ('info', 'warning', 'error', 'security')),
    ip_address TEXT,
    details TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(actor_id) REFERENCES users(id)
);

CREATE INDEX idx_tickets_status ON tickets(status);
CREATE INDEX idx_tickets_category ON tickets(predicted_category);
CREATE INDEX idx_tickets_priority ON tickets(predicted_priority);
CREATE INDEX idx_tickets_created_at ON tickets(created_at);
CREATE INDEX idx_predictions_ticket_id ON ticket_predictions(ticket_id);
CREATE INDEX idx_audit_logs_actor_id ON audit_logs(actor_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);

INSERT INTO categories (name, description, team_default) VALUES
('bug', 'Anomalie applicative, défaut logiciel ou comportement inattendu.', 'Equipe Produit'),
('incident', 'Service indisponible, panne ou dégradation importante.', 'Support N2'),
('facturation', 'Question ou réclamation liée à la facturation.', 'Equipe Finance'),
('acces', 'Problème d''authentification, de permissions ou d''activation de compte.', 'Support IAM'),
('demande_information', 'Question d''usage, de documentation ou d''aide fonctionnelle.', 'Customer Success'),
('technique', 'Sujet technique avancé : API, intégration, configuration.', 'Support Technique'),
('reclamation', 'Plainte, insatisfaction ou escalade client.', 'Customer Care'),
('suggestion', 'Idée d''amélioration ou retour produit.', 'Equipe Produit');

INSERT INTO priorities (name, weight) VALUES
('faible', 1),
('moyenne', 2),
('haute', 3),
('critique', 4);

INSERT INTO urgency_levels (name, weight) VALUES
('basse', 1),
('normale', 2),
('elevee', 3);

INSERT INTO settings (setting_key, setting_value, description, updated_at) VALUES
('critical_keywords', 'bloque,impossible,panne,urgent,production,securite,indisponible', 'Mots-clés utilisés pour hausser la priorité.', datetime('now')),
('vip_domains', 'grande-entreprise.com,client-premium.fr', 'Domaines clients considérés comme prioritaires.', datetime('now')),
('confidence_threshold', '0.55', 'Seuil minimum de confiance recommandé pour validation.', datetime('now')),
('default_processing_minutes', '42', 'Temps moyen simulé de traitement.', datetime('now')),
('engine_version', '1.0.0-hybrid-fr', 'Version du moteur affichée dans l''interface.', datetime('now'));
