from flask import Blueprint, render_template, request, redirect, url_for, g, flash, session
from . import database, printer, utils
from .auth import login_required
import os
import threading

bp = Blueprint('main', __name__)

# De lokale get_db() functie is verwijderd. We gebruiken nu de centrale versie.

def shutdown_server():
    """Stopt de applicatie geforceerd."""
    os._exit(0)

@bp.route('/shutdown')
def shutdown():
    """Route om de applicatie veilig af te sluiten."""
    # Start de shutdown in een thread om de HTTP response te kunnen sturen.
    threading.Timer(1.0, shutdown_server).start()
    return "Applicatie wordt afgesloten..."

@bp.route('/')
def welcome():
    """Hoofdpagina die doorverwijst naar login of de ticketlijst."""
    if 'username' in session:
        return redirect(url_for('main.index'))
    return redirect(url_for('auth.login'))

@bp.route('/tickets')
@login_required
def index():
    """Toont de lijst met actieve tickets."""
    search_query = request.args.get('search', '')
    sort_by = request.args.get('sort', 'created_at_desc')
    filter_by = request.args.get('filter', 'all')
    
    # Delegeer de query-logica naar de database module
    tickets = database.get_active_tickets(g.user, filter_by, search_query, sort_by)

    return render_template('index.html', tickets=tickets, 
                           search_query=search_query, sort_by=sort_by, filter_by=filter_by)

@bp.route('/archive')
@login_required
def archive():
    """Toont de lijst met gearchiveerde tickets."""
    search_query = request.args.get('search', '')
    sort_by = request.args.get('sort', 'created_at_desc')
    filter_by = request.args.get('filter', 'all')

    # Delegeer de query-logica naar de database module
    archived_tickets = database.get_archived_tickets(g.user, filter_by, search_query, sort_by)

    return render_template('archive.html', tickets=archived_tickets, 
                           search_query=search_query, sort_by=sort_by, filter_by=filter_by)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Verwerkt het aanmaken van een nieuw ticket."""
    if request.method == 'POST':
        encrypted_notes = utils.encrypt_data(request.form['sensitive_notes'], g.master_password)
        
        ticket_id = database.create_ticket(
            request.form['title'], request.form['description'], request.form['requester_name'],
            request.form['requester_email'], request.form['requester_phone'],
            request.form.get('priority', 'Gemiddeld'), encrypted_notes
        )
        
        new_ticket_data = database.get_ticket_by_id(ticket_id)
        if new_ticket_data:
            printer.print_new_ticket(new_ticket_data)
            
        flash(f'Ticket #{ticket_id} succesvol aangemaakt!', 'success')
        return redirect(url_for('main.view_ticket', ticket_id=ticket_id))
        
    return render_template('create_ticket.html')

@bp.route('/ticket/<int:ticket_id>')
@login_required
def view_ticket(ticket_id):
    """Toont de details van een specifiek ticket."""
    ticket_data = database.get_ticket_by_id(ticket_id)
    
    if not ticket_data:
        flash(f'Ticket #{ticket_id} niet gevonden.', 'error')
        return redirect(url_for('main.index'))
    
    # Maak een muteerbare kopie van de ticketdata
    ticket = dict(ticket_data)
    if ticket.get('sensitive_notes'):
        ticket['sensitive_notes'] = utils.decrypt_data(ticket['sensitive_notes'], g.master_password)
    
    comments = database.get_comments_for_ticket(ticket_id)
    templates = database.get_all_templates()
    kb_articles = database.get_all_kb_articles()

    return render_template('view_ticket.html', ticket=ticket, comments=comments, 
                           templates=templates, kb_articles=kb_articles)

@bp.route('/ticket/<int:ticket_id>/assign', methods=['POST'])
@login_required
def assign(ticket_id):
    """Wijst een ticket toe aan de ingelogde gebruiker."""
    ticket = database.get_ticket_details_for_update(ticket_id)
    old_assignee = ticket['assigned_to'] if ticket else None
    
    database.assign_ticket(ticket_id, g.user, old_assignee)
    flash(f'Ticket #{ticket_id} toegewezen aan {g.user}.', 'success')
    return redirect(url_for('main.view_ticket', ticket_id=ticket_id))

@bp.route('/ticket/<int:ticket_id>/update', methods=['POST'])
@login_required
def update(ticket_id):
    """Werkt de status en/of commentaren van een ticket bij."""
    ticket = database.get_ticket_details_for_update(ticket_id)
    old_status = ticket['status'] if ticket else 'Onbekend'
    
    new_status = request.form['status']
    comment = request.form['comment']
    
    database.update_ticket(ticket_id, new_status, comment, g.user, old_status)
    flash(f'Ticket #{ticket_id} succesvol bijgewerkt.', 'success')
    return redirect(url_for('main.view_ticket', ticket_id=ticket_id))

@bp.route('/ticket/<int:ticket_id>/link_kb', methods=['POST'])
@login_required
def link_kb(ticket_id):
    """Koppelt een kennisbankartikel aan een ticket."""
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