import sqlite3
from flask import Blueprint, render_template, request, redirect, url_for, g, flash, session
from . import database, printer, utils
from .auth import login_required
import os
import threading

bp = Blueprint('main', __name__)

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(database.DATABASE_FILE)
        g.db.row_factory = sqlite3.Row
    return g.db

def shutdown_server():
    os._exit(0)

@bp.route('/shutdown')
def shutdown():
    threading.Timer(1.0, shutdown_server).start()
    return "Applicatie wordt afgesloten..."

@bp.route('/')
def welcome():
    # Als gebruiker al ingelogd is, ga direct naar de tickets. Anders, toon login.
    if 'username' in session:
        return redirect(url_for('main.index'))
    return redirect(url_for('auth.login'))

@bp.route('/tickets')
@login_required
def index():
    user = g.user
    search_query = request.args.get('search', '')
    sort_by = request.args.get('sort', 'created_at_desc')
    filter_by = request.args.get('filter', 'all')
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
    tickets = db.execute(base_query, params).fetchall()

    return render_template('index.html', tickets=tickets, 
                           search_query=search_query, sort_by=sort_by, filter_by=filter_by)

@bp.route('/archive')
@login_required
def archive():
    user = g.user
    search_query = request.args.get('search', '')
    sort_by = request.args.get('sort', 'created_at_desc')
    filter_by = request.args.get('filter', 'all')
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
    archived_tickets = db.execute(base_query, params).fetchall()

    return render_template('archive.html', tickets=archived_tickets, 
                           search_query=search_query, sort_by=sort_by, filter_by=filter_by)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        encrypted_notes = utils.encrypt_data(request.form['sensitive_notes'], g.master_password)
        ticket_id = database.create_ticket(
            request.form['title'], request.form['description'], request.form['requester_name'],
            request.form['requester_email'], request.form['requester_phone'],
            request.form.get('priority', 'Gemiddeld'), encrypted_notes
        )
        new_ticket_data = get_db().execute('SELECT * FROM tickets WHERE id = ?', (ticket_id,)).fetchone()
        if new_ticket_data: printer.print_new_ticket(new_ticket_data)
        flash(f'Ticket #{ticket_id} succesvol aangemaakt!', 'success')
        return redirect(url_for('main.view_ticket', ticket_id=ticket_id))
    return render_template('create_ticket.html')

@bp.route('/ticket/<int:ticket_id>')
@login_required
def view_ticket(ticket_id):
    db = get_db()
    ticket_data = db.execute('''
        SELECT t.*, k.title as kb_article_title 
        FROM tickets t LEFT JOIN kb_articles k ON t.kb_article_id = k.id WHERE t.id = ?
    ''', (ticket_id,)).fetchone()
    
    if not ticket_data:
        flash(f'Ticket #{ticket_id} niet gevonden.', 'error')
        return redirect(url_for('main.index'))
    
    ticket = dict(ticket_data)
    if ticket.get('sensitive_notes'):
        ticket['sensitive_notes'] = utils.decrypt_data(ticket['sensitive_notes'], g.master_password)
    
    comments = db.execute('SELECT * FROM comments WHERE ticket_id = ? ORDER BY created_at ASC', (ticket_id,)).fetchall()
    templates = database.get_all_templates()
    kb_articles = database.get_all_kb_articles()

    return render_template('view_ticket.html', ticket=ticket, comments=comments, templates=templates, kb_articles=kb_articles)

@bp.route('/ticket/<int:ticket_id>/assign', methods=['POST'])
@login_required
def assign(ticket_id):
    ticket = get_db().execute('SELECT assigned_to FROM tickets WHERE id = ?', (ticket_id,)).fetchone()
    old_assignee = ticket['assigned_to'] if ticket else None
    database.assign_ticket(ticket_id, g.user, old_assignee)
    flash(f'Ticket #{ticket_id} toegewezen aan {g.user}.', 'success')
    return redirect(url_for('main.view_ticket', ticket_id=ticket_id))

@bp.route('/ticket/<int:ticket_id>/update', methods=['POST'])
@login_required
def update(ticket_id):
    ticket = get_db().execute('SELECT status FROM tickets WHERE id = ?', (ticket_id,)).fetchone()
    old_status = ticket['status'] if ticket else 'Onbekend'
    new_status = request.form['status']
    comment = request.form['comment']
    database.update_ticket(ticket_id, new_status, comment, g.user, old_status)
    flash(f'Ticket #{ticket_id} succesvol bijgewerkt.', 'success')
    return redirect(url_for('main.view_ticket', ticket_id=ticket_id))

@bp.route('/ticket/<int:ticket_id>/link_kb', methods=['POST'])
@login_required
def link_kb(ticket_id):
    kb_article_id = request.form.get('kb_article_id')
    if kb_article_id:
        kb_article = database.get_kb_article_by_id(kb_article_id)
        if kb_article:
            database.link_kb_article(ticket_id, kb_article_id, kb_article['title'], g.user)
            flash(f"Artikel '{kb_article['title']}' gekoppeld aan ticket.", 'success')
        else:
            flash("Geselecteerd kennisbank artikel niet gevonden.", 'error')
    else:
        flash("Geen kennisbank artikel geselecteerd.", 'error')
    return redirect(url_for('main.view_ticket', ticket_id=ticket_id))