from flask import Blueprint, render_template, Response, current_app, abort
from . import database, utils
from .auth import login_required

bp = Blueprint('reports', __name__, url_prefix='/reports')

@bp.route('/')
@login_required
def reports_index():
    """Toont de hoofdpagina van de rapportages."""
    return render_template('reports.html')

def _create_chart_response(chart_buffer):
    """Creëert een Flask Response object voor een grafiek met caching headers."""
    response = Response(chart_buffer.getvalue(), mimetype='image/png')
    response.headers['Cache-Control'] = 'public, max-age=60'
    return response

def _process_db_data_to_dict(db_data):
    """Converteert database rijen (lijst van Row-objecten) naar een simpele dictionary."""
    if not db_data:
        return {}  # Geef een lege dict terug als er geen data is

    chart_data = {}
    for row in db_data:
        # De eerste kolom is de key, de tweede is de value
        key = row[0]
        value = row[1]
        
        # Geef een logische naam aan 'None' keys (bijv. voor niet-toegewezen tickets)
        display_key = str(key) if key is not None else 'Niet toegewezen'
        chart_data[display_key] = int(value)
        
    return chart_data

@bp.route('/status_chart.png')
@login_required
def status_chart():
    """Genereert een cirkeldiagram van tickets per status."""
    try:
        db_data = database.get_status_counts()
        chart_data = _process_db_data_to_dict(db_data)
        chart_buffer = utils.generate_pie_chart(chart_data, "Tickets per Status")
        return _create_chart_response(chart_buffer)
    except Exception as e:
        current_app.logger.error(f"Fout bij genereren van status grafiek: {e}")
        abort(503)

@bp.route('/priority_chart.png')
@login_required
def priority_chart():
    """Genereert een cirkeldiagram van tickets per prioriteit."""
    try:
        db_data = database.get_priority_counts()
        chart_data = _process_db_data_to_dict(db_data)
        chart_buffer = utils.generate_pie_chart(chart_data, "Tickets per Prioriteit")
        return _create_chart_response(chart_buffer)
    except Exception as e:
        current_app.logger.error(f"Fout bij genereren van prioriteit grafiek: {e}")
        abort(503)

@bp.route('/assignment_chart.png')
@login_required
def assignment_chart():
    """Genereert een cirkeldiagram van toegewezen vs. niet-toegewezen tickets."""
    try:
        db_data = database.get_assignment_counts()
        chart_data = _process_db_data_to_dict(db_data)
        chart_buffer = utils.generate_pie_chart(chart_data, "Toegewezen vs. Niet-toegewezen")
        return _create_chart_response(chart_buffer)
    except Exception as e:
        current_app.logger.error(f"Fout bij genereren van assignment grafiek: {e}")
        abort(503)

@bp.route('/kb_chart.png')
@login_required
def kb_chart():
    """Genereert een staafdiagram van kennisbankartikelen per categorie."""
    try:
        db_data = database.get_kb_category_counts()
        chart_data = _process_db_data_to_dict(db_data)
        chart_buffer = utils.generate_bar_chart(
            chart_data,
            "KB Artikelen per Categorie"
        )
        return _create_chart_response(chart_buffer)
    except Exception as e:
        current_app.logger.error(f"Fout bij genereren van KB grafiek: {e}")
        abort(503)