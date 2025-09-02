from flask import Blueprint, render_template, Response, current_app, abort
from . import database, utils
from .auth import login_required

bp = Blueprint('reports', __name__, url_prefix='/reports')

@bp.route('/')
@login_required
def reports_index():
    """Toont de hoofdpagina van de rapportages."""
    return render_template(
        'reports.html',
        status_counts=database.get_status_counts(),
        priority_counts=database.get_priority_counts(),
        assignment_counts=database.get_assignment_counts(),
        kb_category_counts=database.get_kb_category_counts()
    )

def _create_chart_response(chart_buffer):
    """Creëert een Flask Response object voor een grafiek met caching headers."""
    if not chart_buffer:
        current_app.logger.warning("Poging om leeg chart buffer te returnen")
        abort(503, description="Grafiek kon niet worden gegenereerd")

    response = Response(chart_buffer.getvalue(), mimetype='image/png')
    # Instrueer de browser om deze afbeelding voor 60 seconden te cachen.
    response.headers['Cache-Control'] = 'public, max-age=60'
    return response

def _process_chart_data(db_data):
    """Helper functie om database data consistent te verwerken."""
    if not db_data:
        current_app.logger.warning("Geen gegevens ontvangen van de database")
        abort(503)

    # Verwerk een enkele rij
    if isinstance(db_data, dict) and 'count' in db_data:
        return {db_data.get('status') or 'Unknown': db_data['count']}

    # Verwerk een lijst van rijen
    elif hasattr(db_data, '__iter__'):
        chart_data = {}
        for row in db_data:
            if isinstance(row, dict):
                key = next((v for k, v in row.items() if not k.endswith('_count')), 'Unknown')
                count = row.get('count', 0)
                # Verwerk None waarden
                display_key = str(key) if key is not None else 'Niet toegewezen'
                chart_data[display_key] = int(count)

        return chart_data

    current_app.logger.error("Onverwachte dataformat ontvangen")
    abort(503, description="Ongeldig gegevensformaat")

@bp.route('/status_chart.png')
@login_required
def status_chart():
    """Genereert een cirkeldiagram van tickets per status."""
    try:
        db_data = database.get_status_counts()
        chart_data = _process_chart_data(db_data)

        if not chart_data or len(chart_data) == 0:
            current_app.logger.warning("Geen ticketstatus gegevens beschikbaar voor grafiek")
            return Response(
                "No data available",
                mimetype='text/plain',
                status=204
            )

        chart_buffer = utils.generate_pie_chart(chart_data, "Tickets per Status")

    except Exception as e:
        current_app.logger.error(f"Fout bij genereren van status grafiek: {e}")
        abort(503)

    return _create_chart_response(chart_buffer)

@bp.route('/priority_chart.png')
@login_required
def priority_chart():
    """Genereert een cirkeldiagram van tickets per prioriteit."""
    try:
        db_data = database.get_priority_counts()
        chart_data = _process_chart_data(db_data)
        if not chart_data or len(chart_data) == 0:
            return Response(
                "No data available",
                mimetype='text/plain',
                status=204
            )

        chart_buffer = utils.generate_pie_chart(chart_data, "Tickets per Prioriteit")

    except Exception as e:
        current_app.logger.error(f"Fout bij genereren van prioriteit grafiek: {e}")
        abort(503)

    return _create_chart_response(chart_buffer)

@bp.route('/assignment_chart.png')
@login_required
def assignment_chart():
    """Genereert een cirkeldiagram van toegewezen vs. niet-toegewezen tickets."""
    try:
        db_data = database.get_assignment_counts()
        chart_data = _process_chart_data(db_data)
        if not chart_data or len(chart_data) == 0:
            return Response(
                "No data available",
                mimetype='text/plain',
                status=204
            )

        # Voeg een 'Geen Tickets' label toe als er geen tickets zijn
        total_tickets = sum(count for count in chart_data.values())
        if total_tickets == 0:
            chart_data['Geen Tickets'] = 1

        chart_buffer = utils.generate_pie_chart(chart_data, "Toegewezen vs. Niet-toegewezen")

    except Exception as e:
        current_app.logger.error(f"Fout bij genereren van assignment grafiek: {e}")
        abort(503)

    return _create_chart_response(chart_buffer)

@bp.route('/kb_chart.png')
@login_required
def kb_chart():
    """Genereert een staafdiagram van kennisbankartikelen per categorie."""
    try:
        db_data = database.get_kb_category_counts()
        chart_data = _process_chart_data(db_data)
        if not chart_data or len(chart_data) == 0:
            return Response(
                "No data available",
                mimetype='text/plain',
                status=204
            )

        # Voeg een 'Geen Artikelen' label toe als er geen artikelen zijn
        total_articles = sum(count for count in chart_data.values())
        if total_articles == 0:
            chart_data['Geen Artikelen'] = 1

        chart_buffer = utils.generate_bar_chart(
            chart_data,
            "KB Artikelen per Categorie",
            "Categorie",
            "Aantal Artikelen"
        )

    except Exception as e:
        current_app.logger.error(f"Fout bij genereren van KB grafiek: {e}")
        abort(503)

    return _create_chart_response(chart_buffer)
