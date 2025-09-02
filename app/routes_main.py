from flask import Blueprint, render_template, request, redirect, url_for, g, flash, session, current_app, abort
from . import database, printer, utils
from .auth import login_required
import os
import threading

bp = Blueprint('main', __name__)

def shutdown_server():
    """Stopt de applicatie geforceerd."""
    func = getattr(os._exit, '__call__')
    return func(0)  # Directe aanroep van _exit om thread-veilig te zijn

@bp.route('/shutdown')
def shutdown():
    """Route om de applicatie veilig af te sluiten."""
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
    sort_by = request.args.get('sort', 'created_at_desc') if request.args.get('sort') else 'created_at_desc'
    filter_by = request.args.get('filter', 'all')

    try:
        # Delegeer de query-logica naar de database module
        tickets = database.get_active_tickets(g.user, filter_by, search_query, sort_by)
        return render_template(
            'index.html',
            tickets=tickets,
            search_query=search_query,
            sort_by=sort_by,
            filter_by=filter_by
        )
    except Exception as e:
        current_app.logger.error(f"Fout bij ophalen van actieve tickets: {e}")
        flash('Er is een fout opgetreden bij het laden van de ticketlijst.', 'error')
        return render_template(
            'index.html',
            tickets=[],
            search_query=search_query,
            sort_by=sort_by,
            filter_by=filter_by
        )

@bp.route('/archive')
@login_required
def archive():
    """Toont de lijst met gearchiveerde tickets."""
    search_query = request.args.get('search', '')
    sort_by = request.args.get('sort', 'created_at_desc') if request.args.get('sort') else 'created_at_desc'
    filter_by = request.args.get('filter', 'all')

    try:
        archived_tickets = database.get_archived_tickets(g.user, filter_by, search_query, sort_by)
        return render_template(
            'archive.html',
            tickets=archived_tickets,
            search_query=search_query,
            sort_by=sort_by,
            filter_by=filter_by
        )
    except Exception as e:
        current_app.logger.error(f"Fout bij ophalen van gearchiveerde tickets: {e}")
        flash('Er is een fout opgetreden bij het laden van de archieflijst.', 'error')
        return render_template(
            'archive.html',
            tickets=[],
            search_query=search_query,
            sort_by=sort_by,
            filter_by=filter_by
        )

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Verwerkt het aanmaken van een nieuw ticket."""
    if request.method == 'POST':
        try:
            # Valideer verplichte velden
            required_fields = ['title', 'description']
            for field in required_fields:
                if not request.form.get(field, '').strip():
                    flash(f'Vel {field.replace("_", " ").capitalize()} is vereist.', 'error')
                    return render_template('create_ticket.html')

            # Encrypt gevoelige data
            encrypted_notes = utils.encrypt_data(
                request.form['sensitive_notes'],
                g.master_password,
                )

            ticket_id = database.create_ticket(
                title=request.form['title'].strip(),
                description=request.form['description'].strip(),
                name=request.form['requester_name'],
                email=request.form['requester_email'],
                phone=request.form['requester_phone'],
                priority=request.form.get('priority', 'Gemiddeld'),
                sensitive_notes=encrypted_notes
            )

            # Haal het nieuwe ticket op voor printen (indien geconfigureerd)
            new_ticket_data = database.get_ticket_by_id(ticket_id)

            if current_app.config.get('PRINT_NEW_TICKETS', False) and new_ticket_data:
                printer.print_new_ticket(new_ticket_data)

            flash(f'Ticket #{ticket_id} succesvol aangemaakt!', 'success')
        except Exception as e:
            current_app.logger.error(f"Fout bij aanmaken van ticket: {e}")
            flash('Er is een fout opgetreden bij het opslaan van het ticket.', 'error')

    return render_template(
        'create_ticket.html',
        default_priority='Gemiddeld'
    )

@bp.route('/ticket/<int:ticket_id>')
@login_required
def view_ticket(ticket_id):
    """Toont de details van een specifiek ticket."""
    try:
        # Haal ticketdata op en ontcrypt gevoelige notities als aanwezig
        ticket_data = database.get_ticket_by_id(ticket_id)
        if not ticket_data:
            flash(f'Ticket #{ticket_id} niet gevonden.', 'error')
            return redirect(url_for('main.index'))

        ticket = dict(ticket_data)  # Maak een muteerbare kopie
        if ticket.get('sensitive_notes'):
            try:
                decrypted_notes = utils.decrypt_data(
                    ticket['sensitive_notes'],
                    g.master_password,
                )
                ticket['sensitive_notes'] = decrypted_notes
            except Exception as e:
                current_app.logger.error(f"Fout bij ontcrypten van notities: {e}")
                flash("Gevoelige notities kunnen niet worden weergegeven.", 'warning')

        # Haal gerelateerde data op voor het template
        comments = database.get_comments_for_ticket(ticket_id)
        templates = database.get_all_templates()
        kb_articles = database.get_all_kb_articles()

        return render_template(
            'view_ticket.html',
            ticket=ticket,
            comments=comments if hasattr(comments, '__iter__') else [],
            templates=[dict(t) for t in templates] or [],
            kb_articles=[dict(a) for a in kb_articles] or []
        )
    except Exception as e:
        current_app.logger.error(f"Fout bij weergave van ticket: {e}")
        abort(500)

@bp.route('/ticket/<int:ticket_id>/assign', methods=['POST'])
@login_required
def assign(ticket_id):
    """Wijst een ticket toe aan de ingelogde gebruiker."""
    try:
        # Valideer dat het ticket bestaat en haal details op voor logging
        ticket = database.get_ticket_details_for_update(ticket_id)
        if not ticket:
            flash(f'Ticket #{ticket_id} niet gevonden.', 'error')
            return redirect(url_for('main.index'))

        old_assignee = ticket['assigned_to'] or "Niet toegewezen"
        new_assignee = g.user

        database.assign_ticket(ticket_id, new_assignee, old_assignee)
        flash(f'Ticket #{ticket_id} toegewezen aan {new_assignee}.', 'success')
    except Exception as e:
        current_app.logger.error(f"Fout bij toewijzing van ticket: {e}")
        flash('Er is een fout opgetreden bij het toewijzen van het ticket.', 'error')

    return redirect(url_for('main.view_ticket', ticket_id=ticket_id))

@bp.route('/ticket/<int:ticket_id>/update', methods=['POST'])
@login_required
def update(ticket_id):
    """Werkt de status en/of commentaren van een ticket bij."""
    try:
        # Valideer dat het ticket bestaat
        ticket = database.get_ticket_details_for_update(ticket_id)
        if not ticket:
            flash(f'Ticket #{ticket_id} niet gevonden.', 'error')
            return redirect(url_for('main.index'))

        old_status = ticket['status'] or "Onbekend"
        new_status = request.form.get('status', '')
        comment = request.form.get('comment', '').strip()

        # Valideer status
        valid_statuses = ['New', 'In Progress', 'Pending', 'Resolved', 'Closed']
        if not any(s.lower() == new_status.lower() for s in valid_statuses):
            flash(f"Ongeldige status '{new_status}'. Gebruik een van: {', '.join(valid_statuses)}.", 'error')
            return redirect(url_for('main.view_ticket', ticket_id=ticket_id))

        database.update_ticket(ticket_id, new_status, comment or None, g.user, old_status)
        flash(f'Ticket #{ticket_id} status bijgewerkt van {old_status} naar {new_status}.', 'success')
    except Exception as e:
        current_app.logger.error(f"Fout bij update ticket: {e}")
        flash('Er is een fout opgetreden bij het opslaan van de updates.', 'error')

    return redirect(url_for('main.view_ticket', ticket_id=ticket_id))

@bp.route('/ticket/<int:ticket_id>/link_kb', methods=['POST'])
@login_required
def link_kb(ticket_id):
    """Koppelt een kennisbankartikel aan een ticket."""
    try:
        kb_article_id = request.form.get('kb_article_id')

        if not kb_article_id or not kb_article_id.isdigit():
            flash("Geen geldig kennisbank artikel geselecteerd.", 'error')
            return redirect(url_for('main.view_ticket', ticket_id=ticket_id))

        try:
            kb_article = database.get_kb_article_by_id(int(kb_article_id))
            if not kb_article:
                flash("Geselecteerd kennisbank artikel niet gevonden.", 'error')
                return redirect(url_for('main.view_ticket', ticket_id=ticket_id))

            # Valideer dat het ticket bestaat
            ticket = database.get_ticket_by_id(ticket_id)
            if not ticket:
                flash(f'Ticket #{ticket_id} niet gevonden.', 'error')
                return redirect(url_for('main.index'))

            database.link_kb_article(
                ticket_id,
                int(kb_article['id']),
                kb_article['title'],
                g.user
            )
            flash(f"Artikel '{kb_article['title']}' gekoppeld aan ticket.", 'success')
        except ValueError:
            current_app.logger.warning("Ongeldige kennisbankartikel ID ontvangen.")
    except Exception as e:
        current_app.logger.error(f"Fout bij koppelen van kennisbank artikel: {e}")
        flash('Er is een fout opgetreden bij het koppelen.', 'error')

    return redirect(url_for('main.view_ticket', ticket_id=ticket_id))
