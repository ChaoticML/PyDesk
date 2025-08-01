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

def init_db():
    """Initialiseert de database, maakt tabellen aan en voegt cruciale indexes toe."""
    os.makedirs(os.path.dirname(DATABASE_FILE), exist_ok=True)
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    # --- TABELLEN AANMAKEN ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, description TEXT,
            requester_name TEXT, requester_email TEXT, requester_phone TEXT,
            status TEXT NOT NULL, priority TEXT NOT NULL, created_at TEXT,
            updated_at TEXT, assigned_to TEXT, sensitive_notes TEXT,
            kb_article_id INTEGER, -- NIEUWE KOLOM VOOR KB-KOPPELING
            FOREIGN KEY (kb_article_id) REFERENCES kb_articles (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT, ticket_id INTEGER NOT NULL, author TEXT NOT NULL,
            comment_text TEXT NOT NULL, created_at TEXT NOT NULL, event_type TEXT DEFAULT 'comment', -- NIEUWE KOLOM VOOR GESCHIEDENIS
            FOREIGN KEY (ticket_id) REFERENCES tickets (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS kb_articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, category TEXT NOT NULL,
            content TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
        )
    ''')

    # --- NIEUWE TABEL VOOR SJABLONEN ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL
        )
    ''')

    # --- KOLOMMEN BIJWERKEN (voor upgrades) ---
    try: cursor.execute("ALTER TABLE tickets ADD COLUMN assigned_to TEXT")
    except sqlite3.OperationalError: pass
    try: cursor.execute("ALTER TABLE tickets ADD COLUMN sensitive_notes TEXT")
    except sqlite3.OperationalError: pass
    try: cursor.execute("ALTER TABLE tickets ADD COLUMN kb_article_id INTEGER")
    except sqlite3.OperationalError: pass
    try: cursor.execute("ALTER TABLE comments ADD COLUMN event_type TEXT DEFAULT 'comment'")
    except sqlite3.OperationalError: pass

    # --- DATABASE INDEXES ---
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets (status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_tickets_created_at ON tickets (created_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_comments_ticket_id ON comments (ticket_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_kb_articles_category ON kb_articles (category)')

    conn.commit()
    conn.close()

# --- Log Functie voor Gedetailleerde Geschiedenis ---
def log_event(ticket_id, author, text, event_type='event'):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute('INSERT INTO comments (ticket_id, author, comment_text, created_at, event_type) VALUES (?, ?, ?, ?, ?)',
                   (ticket_id, author, text, now, event_type))
    conn.commit()
    conn.close()

# --- Ticket Functies ---
def create_ticket(title, description, name, email, phone, priority, sensitive_notes):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute('INSERT INTO tickets (title, description, requester_name, requester_email, requester_phone, status, priority, created_at, updated_at, sensitive_notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                   (title, description, name, email, phone, 'New', priority, now, now, sensitive_notes))
    conn.commit()
    ticket_id = cursor.lastrowid
    conn.close()
    log_event(ticket_id, "Systeem", "Ticket aangemaakt.")
    return ticket_id

def assign_ticket(ticket_id, user_name, old_assignee):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute('UPDATE tickets SET assigned_to = ?, status = \'In Progress\', updated_at = ? WHERE id = ?', (user_name, now, ticket_id))
    conn.commit()
    conn.close()
    
    from_text = f"van '{old_assignee}'" if old_assignee else "van 'Niet toegewezen'"
    log_event(ticket_id, user_name, f"Ticket toegewezen {from_text} naar '{user_name}'.")

def update_ticket(ticket_id, new_status, comment, author, old_status):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    now = datetime.now().isoformat()

    if old_status != new_status:
        cursor.execute('UPDATE tickets SET status = ?, updated_at = ? WHERE id = ?', (new_status, now, ticket_id))
        log_event(ticket_id, author, f"Status gewijzigd van '{old_status}' naar '{new_status}'.")

    if comment:
        log_event(ticket_id, author, comment, event_type='comment')

    conn.commit()
    conn.close()

def link_kb_article(ticket_id, kb_article_id, kb_article_title, author):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute('UPDATE tickets SET kb_article_id = ?, updated_at = ? WHERE id = ?', (kb_article_id, now, ticket_id))
    conn.commit()
    conn.close()
    log_event(ticket_id, author, f"Kennisbank artikel #{kb_article_id} ('{kb_article_title}') gekoppeld.")

# --- Kennisbank Functies ---
def create_kb_article(title, category, content):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO kb_articles (title, category, content) VALUES (?, ?, ?)', (title, category, content))
    conn.commit()
    conn.close()

def get_all_kb_articles():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM kb_articles')
    articles = cursor.fetchall()
    conn.close()
    return articles

def get_kb_article_by_id(article_id):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM kb_articles WHERE id = ?', (article_id,))
    article = cursor.fetchone()
    conn.close()
    return article

def update_kb_article(article_id, title, category, content):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('UPDATE kb_articles SET title = ?, category = ?, content = ? WHERE id = ?', (title, category, content, article_id))
    conn.commit()
    conn.close()

def delete_kb_article(article_id):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM kb_articles WHERE id = ?', (article_id,))
    conn.commit()
    conn.close()

# --- SJABLOON FUNCTIES ---
def create_template(title, content):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO templates (title, content) VALUES (?, ?)', (title, content))
    conn.commit()
    conn.close()

def get_all_templates():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    templates = cursor.execute('SELECT * FROM templates ORDER BY title').fetchall()
    conn.close()
    return templates

def get_template_by_id(template_id):
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    template = cursor.execute('SELECT * FROM templates WHERE id = ?', (template_id,)).fetchone()
    conn.close()
    return template

def update_template(template_id, title, content):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('UPDATE templates SET title = ?, content = ? WHERE id = ?', (title, content, template_id))
    conn.commit()
    conn.close()

def delete_template(template_id):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM templates WHERE id = ?', (template_id,))
    conn.commit()
    conn.close()

# --- Rapportage Functies ---
def get_status_counts():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    status_counts = cursor.execute('SELECT status, COUNT(*) FROM tickets GROUP BY status').fetchall()
    conn.close()
    return status_counts

def get_priority_counts():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    priority_counts = cursor.execute('SELECT priority, COUNT(*) FROM tickets GROUP BY priority').fetchall()
    conn.close()
    return priority_counts

def get_assignment_counts():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    assignment_counts = cursor.execute('SELECT assigned_to, COUNT(*) FROM tickets GROUP BY assigned_to').fetchall()
    conn.close()
    return assignment_counts

def get_kb_category_counts():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    kb_category_counts = cursor.execute('SELECT category, COUNT(*) FROM kb_articles GROUP BY category').fetchall()
    conn.close()
    return kb_category_counts