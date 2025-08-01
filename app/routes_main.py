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

def shutdown_server():
    os._exit(0)

@bp.route('/shutdown')
def shutdown():
    threading.Timer(1.0, shutdown_server).start()
    return "Applicatie wordt afgesloten..."

@bp.route('/')
def welcome():
    return render_template('login.html')

@bp.route('/tickets', methods=['POST', 'GET'])
def index():
    user = request.form.get('user') or request.args.get('user')
    password = request.form.get('password') or request.args.get('password')
    if not user or not password: return redirect(url_for('main.welcome'))
    
    # --- ZOEKFUNCTIONALITEIT LOGICA ---
    search_query = request.args.get('search', '')
    db = get_db()
    
    base_query = "SELECT * FROM tickets WHERE status NOT IN ('Resolved', 'Closed')"
    params = []
    
    if search_query:
        base_query += " AND (title LIKE ? OR description LIKE ?)"
        params.extend([f'%{search_query}%', f'%{search_query}%'])
        
    base_query += " ORDER BY created_at DESC"
    tickets = db.execute(base_query, params).fetchall()

    return render_template('index.html', tickets=tickets, user=user, password=password, search_query=search_query)

@bp.route('/archive')
def archive():
    user = request.args.get('user')
    password = request.args.get('password')
    if not user or not password: return redirect(url_for('main.welcome'))
    
    # --- ZOEKFUNCTIONALITEIT LOGICA ---
    search_query = request.args.get('search', '')
    db = get_db()
    
    base_query = "SELECT * FROM tickets WHERE status IN ('Resolved', 'Closed')"
    params = []
    
    if search_query:
        base_query += " AND (title LIKE ? OR description LIKE ?)"
        params.extend([f'%{search_query}%', f'%{search_query}%'])
        
    base_query += " ORDER BY created_at DESC"
    archived_tickets = db.execute(base_query, params).fetchall()

    return render_template('archive.html', tickets=archived_tickets, user=user, password=password, search_query=search_query)

# ... (create, view_ticket, assign, update functies blijven hetzelfde) ...
@bp.route('/create', methods=['GET', 'POST'])
def create():
    user = request.args.get('user')
    password = request.args.get('password')
    if not user or not password: return redirect(url_for('main.welcome'))
    if request.method == 'POST':
        encrypted_notes = utils.encrypt_data(request.form['sensitive_notes'], password)
        ticket_id = database.create_ticket(request.form['title'], request.form['description'], request.form['requester_name'], request.form['requester_email'], request.form['requester_phone'], request.form.get('priority', 'Medium'), encrypted_notes)
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
    ticket_data = get_db().execute('SELECT * FROM tickets WHERE id = ?', (ticket_id,)).fetchone()
    if not ticket_data:
        flash(f'Ticket #{ticket_id} niet gevonden.', 'error')
        return redirect(url_for('main.index', user=user, password=password))
    ticket = dict(ticket_data)
    if ticket.get('sensitive_notes'):
        ticket['sensitive_notes'] = utils.decrypt_data(ticket['sensitive_notes'], password)
    comments = get_db().execute('SELECT * FROM comments WHERE ticket_id = ? ORDER BY created_at ASC', (ticket_id,)).fetchall()
    return render_template('view_ticket.html', ticket=ticket, comments=comments, user=user, password=password)

@bp.route('/ticket/<int:ticket_id>/assign', methods=['POST'])
def assign(ticket_id):
    user = request.args.get('user')
    password = request.args.get('password')
    if not user or not password: return redirect(url_for('main.welcome'))
    database.assign_ticket(ticket_id, user)
    flash(f'Ticket #{ticket_id} toegewezen aan {user}.', 'success')
    return redirect(url_for('main.view_ticket', ticket_id=ticket_id, user=user, password=password))

@bp.route('/ticket/<int:ticket_id>/update', methods=['POST'])
def update(ticket_id):
    user = request.args.get('user')
    password = request.args.get('password')
    if not user or not password: return redirect(url_for('main.welcome'))
    database.update_ticket(ticket_id, request.form['status'], request.form['comment'], user)
    flash(f'Ticket #{ticket_id} succesvol bijgewerkt.', 'success')
    return redirect(url_for('main.view_ticket', ticket_id=ticket_id, user=user, password=password))