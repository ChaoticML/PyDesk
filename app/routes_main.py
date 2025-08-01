import sqlite3
from flask import Blueprint, render_template, request, redirect, url_for, g, flash
from . import database, printer, utils
import os
import threading

bp = Blueprint('main', __name__)

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(database.DATABASE_FILE)
        g.db.row_factory = sqlite3.Row
    return g.db

# ... (shutdown en welcome functies blijven ongewijzigd) ...
def shutdown_server():
    os._exit(0)

@bp.route('/shutdown')
def shutdown():
    threading.Timer(1.0, shutdown_server).start()
    return "Applicatie wordt afgesloten..."

@bp.route('/')
def welcome():
    return render_template('login.html')

# --- Dynamische Query voor Actieve Tickets ---
@bp.route('/tickets', methods=['POST', 'GET'])
def index():
    user = request.form.get('user') or request.args.get('user')
    password = request.form.get('password') or request.args.get('password')
    if not user or not password: return redirect(url_for('main.welcome'))
    
    # Haal alle filter- en sorteeropties uit de URL
    search_query = request.args.get('search', '')
    sort_by = request.args.get('sort', 'created_at_desc')
    filter_by = request.args.get('filter', 'all')

    db = get_db()
    
    # Bouw de SQL query dynamisch op
    base_query = "SELECT * FROM tickets WHERE status NOT IN ('Resolved', 'Closed')"
    params = []
    
    # Filter logica
    if filter_by == 'mine':
        base_query += " AND assigned_to = ?"
        params.append(user)
    elif filter_by == 'unassigned':
        base_query += " AND assigned_to IS NULL"

    # Zoek logica
    if search_query:
        base_query += " AND (title LIKE ? OR description LIKE ?)"
        params.extend([f'%{search_query}%', f'%{search_query}%'])
        
    # Sorteer logica
    sort_options = {
        'created_at_desc': 'ORDER BY created_at DESC',
        'created_at_asc': 'ORDER BY created_at ASC',
        'priority': "ORDER BY CASE priority WHEN 'Hoog' THEN 1 WHEN 'Gemiddeld' THEN 2 WHEN 'Laag' THEN 3 END ASC",
        'status': 'ORDER BY status ASC'
    }
    base_query += " " + sort_options.get(sort_by, 'ORDER BY created_at DESC') # Veilige fallback

    tickets = db.execute(base_query, params).fetchall()

    return render_template('index.html', tickets=tickets, user=user, password=password, 
                           search_query=search_query, sort_by=sort_by, filter_by=filter_by)

# --- Dynamische Query voor Archief ---
@bp.route('/archive')
def archive():
    user = request.args.get('user')
    password = request.args.get('password')
    if not user or not password: return redirect(url_for('main.welcome'))
    
    # Haal alle filter- en sorteeropties uit de URL
    search_query = request.args.get('search', '')
    sort_by = request.args.get('sort', 'created_at_desc')
    filter_by = request.args.get('filter', 'all')
    
    db = get_db()
    
    # Bouw de SQL query dynamisch op
    base_query = "SELECT * FROM tickets WHERE status IN ('Resolved', 'Closed')"
    params = []

    # Filter logica
    if filter_by == 'mine':
        base_query += " AND assigned_to = ?"
        params.append(user)
    
    # Zoek logica
    if search_query:
        base_query += " AND (title LIKE ? OR description LIKE ?)"
        params.extend([f'%{search_query}%', f'%{search_query}%'])
        
    # Sorteer logica
    sort_options = {
        'created_at_desc': 'ORDER BY created_at DESC',
        'created_at_asc': 'ORDER BY created_at ASC',
        'priority': "ORDER BY CASE priority WHEN 'Hoog' THEN 1 WHEN 'Gemiddeld' THEN 2 WHEN 'Laag' THEN 3 END ASC",
        'status': 'ORDER BY status ASC'
    }
    base_query += " " + sort_options.get(sort_by, 'ORDER BY created_at DESC')

    archived_tickets = db.execute(base_query, params).fetchall()

    return render_template('archive.html', tickets=archived_tickets, user=user, password=password,
                           search_query=search_query, sort_by=sort_by, filter_by=filter_by)


# ... (create, view_ticket, assign, update functies) ...
@bp.route('/create', methods=['GET', 'POST'])
def create():
    user = request.args.get('user')
    password = request.args.get('password')
    if not user or not password: return redirect(url_for('main.welcome'))
    if request.method == 'POST':
        encrypted_notes = utils.encrypt_data(request.form['sensitive_notes'], password)
        ticket_id = database.create_ticket(request.form['title'], request.form['description'], request.form['requester_name'], request.form['requester_email'], request.form['requester_phone'], request.form.get('priority', 'Gemiddeld'), encrypted_notes)
        new_ticket_data = get_db().execute('SELECT * FROM tickets WHERE id = ?', (ticket_id,)).fetchone()
        if new_ticket_data: printer.print_new_ticket(new_ticket_data)
        flash(f'Ticket #{ticket_id} succesvol aangemaakt!', 'success')
        return redirect(url_for('main.view_ticket', ticket_id=ticket_id, user=user, password=password))
    return render_template('create_ticket.html', user=user, password=password)

@bp.route('/ticket/<int:ticket_id>')
def view_ticket(ticket_id):
    user = request.args.get('user')
    password = request.args.get('password')
    if not user or not password: return redirect(url_for('main.welcome'))
    
    db = get_db()
    # Gebruik een JOIN om direct de titel van het gekoppelde KB-artikel op te halen
    ticket_data = db.execute('''
        SELECT t.*, k.title as kb_article_title 
        FROM tickets t 
        LEFT JOIN kb_articles k ON t.kb_article_id = k.id 
        WHERE t.id = ?
    ''', (ticket_id,)).fetchone()
    
    if not ticket_data:
        flash(f'Ticket #{ticket_id} niet gevonden.', 'error')
        return redirect(url_for('main.index', user=user, password=password))
    
    ticket = dict(ticket_data)
    if ticket.get('sensitive_notes'):
        ticket['sensitive_notes'] = utils.decrypt_data(ticket['sensitive_notes'], password)
    
    comments = db.execute('SELECT * FROM comments WHERE ticket_id = ? ORDER BY created_at ASC', (ticket_id,)).fetchall()
    
    # Haal alle sjablonen en KB-artikelen op voor de dropdowns
    templates = database.get_all_templates()
    kb_articles = database.get_all_kb_articles()

    return render_template('view_ticket.html', ticket=ticket, comments=comments, user=user, password=password, templates=templates, kb_articles=kb_articles)

@bp.route('/ticket/<int:ticket_id>/assign', methods=['POST'])
def assign(ticket_id):
    user = request.args.get('user')
    password = request.args.get('password')
    if not user or not password: return redirect(url_for('main.welcome'))
    
    # Haal de huidige toegewezen persoon op voor de logging
    ticket = get_db().execute('SELECT assigned_to FROM tickets WHERE id = ?', (ticket_id,)).fetchone()
    old_assignee = ticket['assigned_to'] if ticket else None

    database.assign_ticket(ticket_id, user, old_assignee)
    flash(f'Ticket #{ticket_id} toegewezen aan {user}.', 'success')
    return redirect(url_for('main.view_ticket', ticket_id=ticket_id, user=user, password=password))

@bp.route('/ticket/<int:ticket_id>/update', methods=['POST'])
def update(ticket_id):
    user = request.args.get('user')
    password = request.args.get('password')
    if not user or not password: return redirect(url_for('main.welcome'))
    
    # Haal de huidige status op voor de logging
    ticket = get_db().execute('SELECT status FROM tickets WHERE id = ?', (ticket_id,)).fetchone()
    old_status = ticket['status'] if ticket else 'Onbekend'

    new_status = request.form['status']
    comment = request.form['comment']
    database.update_ticket(ticket_id, new_status, comment, user, old_status)
    flash(f'Ticket #{ticket_id} succesvol bijgewerkt.', 'success')
    return redirect(url_for('main.view_ticket', ticket_id=ticket_id, user=user, password=password))

# --- NIEUWE ROUTE VOOR KB-KOPPELING ---
@bp.route('/ticket/<int:ticket_id>/link_kb', methods=['POST'])
def link_kb(ticket_id):
    user = request.args.get('user')
    password = request.args.get('password')
    if not user or not password: return redirect(url_for('main.welcome'))

    kb_article_id = request.form.get('kb_article_id')
    if kb_article_id:
        # Haal de titel op voor de logging
        kb_article = database.get_kb_article_by_id(kb_article_id)
        if kb_article:
            database.link_kb_article(ticket_id, kb_article_id, kb_article['title'], user)
            flash(f"Artikel '{kb_article['title']}' gekoppeld aan ticket.", 'success')
        else:
            flash("Geselecteerd kennisbank artikel niet gevonden.", 'error')
    else:
        flash("Geen kennisbank artikel geselecteerd.", 'error')

    return redirect(url_for('main.view_ticket', ticket_id=ticket_id, user=user, password=password))