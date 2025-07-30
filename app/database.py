import sqlite3
import os
import sys
from datetime import datetime

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

    cursor.execute('CREATE TABLE IF NOT EXISTS tickets (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, description TEXT, requester_name TEXT, requester_email TEXT, requester_phone TEXT, status TEXT NOT NULL, priority TEXT NOT NULL, created_at TEXT, updated_at TEXT, assigned_to TEXT, sensitive_notes TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS comments (id INTEGER PRIMARY KEY AUTOINCREMENT, ticket_id INTEGER NOT NULL, author TEXT NOT NULL, comment_text TEXT NOT NULL, created_at TEXT NOT NULL, FOREIGN KEY (ticket_id) REFERENCES tickets (id))')
    cursor.execute('CREATE TABLE IF NOT EXISTS kb_articles (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, category TEXT NOT NULL, content TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL)')

    try: cursor.execute("ALTER TABLE tickets ADD COLUMN assigned_to TEXT")
    except sqlite3.OperationalError: pass
    try: cursor.execute("ALTER TABLE tickets ADD COLUMN sensitive_notes TEXT")
    except sqlite3.OperationalError: pass

    cursor.execute('CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets (status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_tickets_created_at ON tickets (created_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_comments_ticket_id ON comments (ticket_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_kb_articles_category ON kb_articles (category)')

    conn.commit()
    conn.close()

def create_ticket(title, description, name, email, phone, priority, sensitive_notes):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute('INSERT INTO tickets (title, description, requester_name, requester_email, requester_phone, status, priority, created_at, updated_at, sensitive_notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                   (title, description, name, email, phone, 'New', priority, now, now, sensitive_notes))
    conn.commit()
    ticket_id = cursor.lastrowid
    conn.close()
    return ticket_id

def assign_ticket(ticket_id, user_name):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute('UPDATE tickets SET assigned_to = ?, status = \'In Progress\', updated_at = ? WHERE id = ?', (user_name, now, ticket_id))
    comment_text = f"Ticket toegewezen aan {user_name}."
    cursor.execute('INSERT INTO comments (ticket_id, author, comment_text, created_at) VALUES (?, ?, ?, ?)', (ticket_id, "Systeem", comment_text, now))
    conn.commit()
    conn.close()

def update_ticket(ticket_id, new_status, comment, author):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute('UPDATE tickets SET status = ?, updated_at = ? WHERE id = ?', (new_status, now, ticket_id))
    comment_text = f"Status gewijzigd naar {new_status}. {comment}"
    cursor.execute('INSERT INTO comments (ticket_id, author, comment_text, created_at) VALUES (?, ?, ?, ?)', (ticket_id, author, comment_text, now))
    conn.commit()
    conn.close()

def create_kb_article(title, category, content):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute('INSERT INTO kb_articles (title, category, content, created_at, updated_at) VALUES (?, ?, ?, ?, ?)',
                   (title, category.strip(), content, now, now))
    conn.commit()
    conn.close()

def get_all_kb_articles():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    articles = cursor.execute('SELECT * FROM kb_articles ORDER BY category, title').fetchall()
    conn.close()
    return articles

def get_kb_article_by_id(article_id):
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    article = cursor.execute('SELECT * FROM kb_articles WHERE id = ?', (article_id,)).fetchone()
    conn.close()
    return article

def update_kb_article(article_id, title, category, content):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute('UPDATE kb_articles SET title = ?, category = ?, content = ?, updated_at = ? WHERE id = ?',
                   (title, category.strip(), content, now, article_id))
    conn.commit()
    conn.close()

def delete_kb_article(article_id):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM kb_articles WHERE id = ?', (article_id,))
    conn.commit()
    conn.close()

def get_status_counts():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT status, COUNT(*) as count FROM tickets GROUP BY status")
    data = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()
    return data

def get_priority_counts():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT priority, COUNT(*) as count FROM tickets GROUP BY priority")
    data = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()
    return data

def get_assignment_counts():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT CASE WHEN assigned_to IS NULL THEN 'Niet toegewezen' ELSE 'Toegewezen' END, COUNT(*) FROM tickets GROUP BY 1")
    data = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()
    return data

def get_kb_category_counts():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT category, COUNT(*) as count FROM kb_articles GROUP BY category")
    data = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()
    return data