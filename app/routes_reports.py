from flask import Blueprint, render_template, Response
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
    # Instrueer de browser om deze afbeelding voor 60 seconden te cachen.
    response.headers['Cache-Control'] = 'public, max-age=60'
    return response

@bp.route('/status_chart.png')
@login_required
def status_chart():
    """Genereert een cirkeldiagram van tickets per status."""
    db_data = database.get_status_counts()
    # Converteer de lijst van Row objecten expliciet naar een dictionary
    chart_data = {row['status']: row['count'] for row in db_data}
    
    chart_buffer = utils.generate_pie_chart(chart_data, "Tickets per Status")
    return _create_chart_response(chart_buffer)

@bp.route('/priority_chart.png')
@login_required
def priority_chart():
    """Genereert een cirkeldiagram van tickets per prioriteit."""
    db_data = database.get_priority_counts()
    chart_data = {row['priority']: row['count'] for row in db_data}
    
    chart_buffer = utils.generate_pie_chart(chart_data, "Tickets per Prioriteit")
    return _create_chart_response(chart_buffer)

@bp.route('/assignment_chart.png')
@login_required
def assignment_chart():
    """Genereert een cirkeldiagram van toegewezen vs. niet-toegewezen tickets."""
    db_data = database.get_assignment_counts()
    # Verwerk de data: vervang None door een leesbare string
    chart_data = {
        (row['assigned_to'] if row['assigned_to'] is not None else 'Niet toegewezen'): row['count']
        for row in db_data
    }
    
    chart_buffer = utils.generate_pie_chart(chart_data, "Toegewezen vs. Niet-toegewezen")
    return _create_chart_response(chart_buffer)

@bp.route('/kb_chart.png')
@login_required
def kb_chart():
    """Genereert een staafdiagram van kennisbankartikelen per categorie."""
    db_data = database.get_kb_category_counts()
    chart_data = {row['category']: row['count'] for row in db_data}
    
    chart_buffer = utils.generate_bar_chart(chart_data, "KB Artikelen per Categorie", "Categorie", "Aantal Artikelen")
    return _create_chart_response(chart_buffer)