import sqlite3
import os
from datetime import datetime
from flask import g

# --- Database Initialisatie ---
# Deze functie wordt nu aangeroepen vanuit app/__init__.py

def init_db(config):
    """Initialiseert de database en maakt/update tabellen."""
    DATABASE_FILE = config['DATABASE_FILE']
    os.makedirs(os.path.dirname(DATABASE_FILE), exist_ok=True)
    
    # Maak een tijdelijke, directe verbinding alleen voor initialisatie
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    # --- TABELDEFINITIES ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, description TEXT,
            requester_name TEXT, requester_email TEXT, requester_phone TEXT,
            status TEXT NOT NULL, priority TEXT NOT NULL, created_at TEXT,
            updated_at TEXT, assigned_to TEXT, sensitive_notes TEXT,
            kb_article_id INTEGER,
            FOREIGN KEY (kb_article_id) REFERENCES kb_articles (id) ON DELETE SET NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT, ticket_id INTEGER NOT NULL, author TEXT NOT NULL,
            comment_text TEXT NOT NULL, created_at TEXT NOT NULL, event_type TEXT DEFAULT 'comment',
            FOREIGN KEY (ticket_id) REFERENCES tickets (id) ON DELETE CASCADE
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS kb_articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, category TEXT NOT NULL,
            content TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, content TEXT NOT NULL
        )
    ''')

    # --- KOLOMMEN BIJWERKEN (voor upgrades) ---
    try: cursor.execute("ALTER TABLE tickets ADD COLUMN kb_article_id INTEGER REFERENCES kb_articles(id) ON DELETE SET NULL")
    except: pass
    try: cursor.execute("ALTER TABLE comments ADD COLUMN event_type TEXT DEFAULT 'comment'")
    except: pass

    # --- DATABASE INDEXES ---
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets (status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_tickets_created_at ON tickets (created_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_comments_ticket_id ON comments (ticket_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_kb_articles_category ON kb_articles (category)')

    conn.commit()
    conn.close()

# --- Helper Functie ---
def get_db():
    """
    Retourneert de database connectie uit de globale context 'g'.
    Deze wordt geopend in de @app.before_request handler in __init__.py.
    """
    return g.db

# --- Event Logging ---
def log_event(ticket_id, author, text, event_type='event'):
    db = get_db()
    now = datetime.now().isoformat()
    db.execute('INSERT INTO comments (ticket_id, author, comment_text, created_at, event_type) VALUES (?, ?, ?, ?, ?)',
                   (ticket_id, author, text, now, event_type))
    db.commit()

# --- Ticket Functies ---
def create_ticket(title, description, name, email, phone, priority, sensitive_notes):
    db = get_db()
    now = datetime.now().isoformat()
    cursor = db.execute('INSERT INTO tickets (title, description, requester_name, requester_email, requester_phone, status, priority, created_at, updated_at, sensitive_notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                   (title, description, name, email, phone, 'New', priority, now, now, sensitive_notes))
    db.commit()
    ticket_id = cursor.lastrowid
    log_event(ticket_id, "Systeem", "Ticket aangemaakt.")
    return ticket_id

def assign_ticket(ticket_id, user_name, old_assignee):
    db = get_db()
    now = datetime.now().isoformat()
    db.execute('UPDATE tickets SET assigned_to = ?, status = \'In Progress\', updated_at = ? WHERE id = ?', (user_name, now, ticket_id))
    db.commit()
    from_text = f"van '{old_assignee}'" if old_assignee else "van 'Niet toegewezen'"
    log_event(ticket_id, user_name, f"Ticket toegewezen {from_text} naar '{user_name}'.")

def update_ticket(ticket_id, new_status, comment, author, old_status):
    db = get_db()
    now = datetime.now().isoformat()
    if old_status != new_status:
        db.execute('UPDATE tickets SET status = ?, updated_at = ? WHERE id = ?', (new_status, now, ticket_id))
        log_event(ticket_id, author, f"Status gewijzigd van '{old_status}' naar '{new_status}'.")
    if comment:
        log_event(ticket_id, author, comment, event_type='comment')
    db.commit()

def link_kb_article(ticket_id, kb_article_id, kb_article_title, author):
    db = get_db()
    now = datetime.now().isoformat()
    db.execute('UPDATE tickets SET kb_article_id = ?, updated_at = ? WHERE id = ?', (kb_article_id, now, ticket_id))
    db.commit()
    log_event(ticket_id, author, f"Kennisbank artikel #{kb_article_id} ('{kb_article_title}') gekoppeld.")

# --- Kennisbank Functies ---
def create_kb_article(title, category, content):
    db = get_db()
    now = datetime.now().isoformat()
    db.execute('INSERT INTO kb_articles (title, category, content, created_at, updated_at) VALUES (?, ?, ?, ?, ?)', (title, category, content, now, now))
    db.commit()

def get_all_kb_articles():
    return get_db().execute('SELECT * FROM kb_articles ORDER BY category, title').fetchall()

def get_kb_article_by_id(article_id):
    return get_db().execute('SELECT * FROM kb_articles WHERE id = ?', (article_id,)).fetchone()

def update_kb_article(article_id, title, category, content):
    db = get_db()
    now = datetime.now().isoformat()
    db.execute('UPDATE kb_articles SET title = ?, category = ?, content = ?, updated_at = ? WHERE id = ?', (title, category, content, now, article_id))
    db.commit()

def delete_kb_article(article_id):
    db = get_db()
    db.execute('DELETE FROM kb_articles WHERE id = ?', (article_id,))
    db.commit()

# --- Sjabloon Functies ---
def create_template(title, content):
    db = get_db()
    db.execute('INSERT INTO templates (title, content) VALUES (?, ?)', (title, content))
    db.commit()

def get_all_templates():
    return get_db().execute('SELECT * FROM templates ORDER BY title').fetchall()

def get_template_by_id(template_id):
    return get_db().execute('SELECT * FROM templates WHERE id = ?', (template_id,)).fetchone()

def update_template(template_id, title, content):
    db = get_db()
    db.execute('UPDATE templates SET title = ?, content = ? WHERE id = ?', (title, content, template_id))
    db.commit()

def delete_template(template_id):
    db = get_db()
    db.execute('DELETE FROM templates WHERE id = ?', (template_id,))
    db.commit()

# --- Rapportage Functies ---
def get_status_counts():
    return get_db().execute('SELECT status, COUNT(*) as count FROM tickets GROUP BY status').fetchall()

def get_priority_counts():
    return get_db().execute('SELECT priority, COUNT(*) as count FROM tickets GROUP BY priority').fetchall()

def get_assignment_counts():
    return get_db().execute('SELECT assigned_to, COUNT(*) as count FROM tickets GROUP BY assigned_to').fetchall()

def get_kb_category_counts():
    return get_db().execute('SELECT category, COUNT(*) as count FROM kb_articles GROUP BY category').fetchall()

# --- Functies voor Routes ---

def get_active_tickets(user, filter_by, search_query, sort_by):
    db = get_db()
    base_query = "SELECT * FROM tickets WHERE status NOT IN ('Resolved', 'Closed')"
    params = []
    
    if filter_by == 'mine':
        base_query += " AND assigned_to = ?"
        params.append(user)
    elif filter_by == 'unassigned':
        base_query += " AND assigned_to IS NULL"

    if search_query:
        base_query += " AND (title LIKE ? OR description LIKE ?)"
        params.extend([f'%{search_query}%', f'%{search_query}%'])
        
    sort_options = {
        'created_at_desc': 'ORDER BY created_at DESC', 'created_at_asc': 'ORDER BY created_at ASC',
        'priority': "ORDER BY CASE priority WHEN 'Hoog' THEN 1 WHEN 'Gemiddeld' THEN 2 WHEN 'Laag' THEN 3 END ASC",
        'status': 'ORDER BY status ASC'
    }
    base_query += " " + sort_options.get(sort_by, 'ORDER BY created_at DESC')
    return db.execute(base_query, params).fetchall()

def get_archived_tickets(user, filter_by, search_query, sort_by):
    db = get_db()
    base_query = "SELECT * FROM tickets WHERE status IN ('Resolved', 'Closed')"
    params = []

    if filter_by == 'mine':
        base_query += " AND assigned_to = ?"
        params.append(user)
    
    if search_query:
        base_query += " AND (title LIKE ? OR description LIKE ?)"
        params.extend([f'%{search_query}%', f'%{search_query}%'])
        
    sort_options = {
        'created_at_desc': 'ORDER BY created_at DESC', 'created_at_asc': 'ORDER BY created_at ASC',
        'priority': "ORDER BY CASE priority WHEN 'Hoog' THEN 1 WHEN 'Gemiddeld' THEN 2 WHEN 'Laag' THEN 3 END ASC",
        'status': 'ORDER BY status ASC'
    }
    base_query += " " + sort_options.get(sort_by, 'ORDER BY created_at DESC')
    return db.execute(base_query, params).fetchall()

def get_ticket_by_id(ticket_id):
    return get_db().execute('''
        SELECT t.*, k.title as kb_article_title 
        FROM tickets t LEFT JOIN kb_articles k ON t.kb_article_id = k.id WHERE t.id = ?
    ''', (ticket_id,)).fetchone()

def get_comments_for_ticket(ticket_id):
    return get_db().execute('SELECT * FROM comments WHERE ticket_id = ? ORDER BY created_at ASC', (ticket_id,)).fetchall()

def get_ticket_details_for_update(ticket_id):
    return get_db().execute('SELECT assigned_to, status FROM tickets WHERE id = ?', (ticket_id,)).fetchone()