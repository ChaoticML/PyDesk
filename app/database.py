import sqlite3
import os
import sys
from datetime import datetime

# Bepaal het correcte pad voor het databasebestand.
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

DATABASE_FILE = os.path.join(application_path, 'data', 'tickets.db')

def get_db_conn():
    """Maakt een database connectie aan met Row factory voor dict-achtige resultaten."""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialiseert de database en maakt/update tabellen."""
    os.makedirs(os.path.dirname(DATABASE_FILE), exist_ok=True)
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
    # Dit is een simpele migratie-aanpak.
    try: cursor.execute("ALTER TABLE tickets ADD COLUMN assigned_to TEXT")
    except: pass
    try: cursor.execute("ALTER TABLE tickets ADD COLUMN sensitive_notes TEXT")
    except: pass
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

# --- Event Logging ---
def log_event(ticket_id, author, text, event_type='event'):
    conn = get_db_conn()
    now = datetime.now().isoformat()
    conn.execute('INSERT INTO comments (ticket_id, author, comment_text, created_at, event_type) VALUES (?, ?, ?, ?, ?)',
                   (ticket_id, author, text, now, event_type))
    conn.commit()
    conn.close()

# --- Ticket Functies ---
def create_ticket(title, description, name, email, phone, priority, sensitive_notes):
    conn = get_db_conn()
    now = datetime.now().isoformat()
    cursor = conn.execute('INSERT INTO tickets (title, description, requester_name, requester_email, requester_phone, status, priority, created_at, updated_at, sensitive_notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                   (title, description, name, email, phone, 'New', priority, now, now, sensitive_notes))
    conn.commit()
    ticket_id = cursor.lastrowid
    conn.close()
    log_event(ticket_id, "Systeem", "Ticket aangemaakt.")
    return ticket_id

def assign_ticket(ticket_id, user_name, old_assignee):
    conn = get_db_conn()
    now = datetime.now().isoformat()
    conn.execute('UPDATE tickets SET assigned_to = ?, status = \'In Progress\', updated_at = ? WHERE id = ?', (user_name, now, ticket_id))
    conn.commit()
    conn.close()
    from_text = f"van '{old_assignee}'" if old_assignee else "van 'Niet toegewezen'"
    log_event(ticket_id, user_name, f"Ticket toegewezen {from_text} naar '{user_name}'.")

def update_ticket(ticket_id, new_status, comment, author, old_status):
    conn = get_db_conn()
    now = datetime.now().isoformat()
    if old_status != new_status:
        conn.execute('UPDATE tickets SET status = ?, updated_at = ? WHERE id = ?', (new_status, now, ticket_id))
        log_event(ticket_id, author, f"Status gewijzigd van '{old_status}' naar '{new_status}'.")
    if comment:
        log_event(ticket_id, author, comment, event_type='comment')
    conn.commit()
    conn.close()

def link_kb_article(ticket_id, kb_article_id, kb_article_title, author):
    conn = get_db_conn()
    now = datetime.now().isoformat()
    conn.execute('UPDATE tickets SET kb_article_id = ?, updated_at = ? WHERE id = ?', (kb_article_id, now, ticket_id))
    conn.commit()
    conn.close()
    log_event(ticket_id, author, f"Kennisbank artikel #{kb_article_id} ('{kb_article_title}') gekoppeld.")

# --- Kennisbank Functies ---
def create_kb_article(title, category, content):
    conn = get_db_conn()
    now = datetime.now().isoformat()
    conn.execute('INSERT INTO kb_articles (title, category, content, created_at, updated_at) VALUES (?, ?, ?, ?, ?)', (title, category, content, now, now))
    conn.commit()
    conn.close()

def get_all_kb_articles():
    conn = get_db_conn()
    articles = conn.execute('SELECT * FROM kb_articles ORDER BY category, title').fetchall()
    conn.close()
    return articles

def get_kb_article_by_id(article_id):
    conn = get_db_conn()
    article = conn.execute('SELECT * FROM kb_articles WHERE id = ?', (article_id,)).fetchone()
    conn.close()
    return article

def update_kb_article(article_id, title, category, content):
    conn = get_db_conn()
    now = datetime.now().isoformat()
    conn.execute('UPDATE kb_articles SET title = ?, category = ?, content = ?, updated_at = ? WHERE id = ?', (title, category, content, now, article_id))
    conn.commit()
    conn.close()

def delete_kb_article(article_id):
    conn = get_db_conn()
    conn.execute('DELETE FROM kb_articles WHERE id = ?', (article_id,))
    conn.commit()
    conn.close()

# --- Sjabloon Functies ---
def create_template(title, content):
    conn = get_db_conn()
    conn.execute('INSERT INTO templates (title, content) VALUES (?, ?)', (title, content))
    conn.commit()
    conn.close()

def get_all_templates():
    conn = get_db_conn()
    templates = conn.execute('SELECT * FROM templates ORDER BY title').fetchall()
    conn.close()
    return templates

def get_template_by_id(template_id):
    conn = get_db_conn()
    template = conn.execute('SELECT * FROM templates WHERE id = ?', (template_id,)).fetchone()
    conn.close()
    return template

def update_template(template_id, title, content):
    conn = get_db_conn()
    conn.execute('UPDATE templates SET title = ?, content = ? WHERE id = ?', (title, content, template_id))
    conn.commit()
    conn.close()

def delete_template(template_id):
    conn = get_db_conn()
    conn.execute('DELETE FROM templates WHERE id = ?', (template_id,))
    conn.commit()
    conn.close()

# --- Rapportage Functies ---
def get_status_counts():
    conn = get_db_conn()
    return conn.execute('SELECT status, COUNT(*) as count FROM tickets GROUP BY status').fetchall()

def get_priority_counts():
    conn = get_db_conn()
    return conn.execute('SELECT priority, COUNT(*) as count FROM tickets GROUP BY priority').fetchall()

def get_assignment_counts():
    conn = get_db_conn()
    return conn.execute('SELECT assigned_to, COUNT(*) as count FROM tickets GROUP BY assigned_to').fetchall()

def get_kb_category_counts():
    conn = get_db_conn()
    return conn.execute('SELECT category, COUNT(*) as count FROM kb_articles GROUP BY category').fetchall()