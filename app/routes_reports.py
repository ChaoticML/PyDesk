from flask import Blueprint, render_template, Response
from . import database, utils
from .auth import login_required

bp = Blueprint('reports', __name__, url_prefix='/reports')

@bp.route('/')
@login_required
def reports_index():
    return render_template('reports.html')

@bp.route('/status_chart.png')
@login_required
def status_chart():
    data = database.get_status_counts()
    chart_buffer = utils.generate_pie_chart(dict(data), "Tickets per Status")
    return Response(chart_buffer.getvalue(), mimetype='image/png')

@bp.route('/priority_chart.png')
@login_required
def priority_chart():
    data = database.get_priority_counts()
    chart_buffer = utils.generate_pie_chart(dict(data), "Tickets per Prioriteit")
    return Response(chart_buffer.getvalue(), mimetype='image/png')

@bp.route('/assignment_chart.png')
@login_required
def assignment_chart():
    data = database.get_assignment_counts()
    # Vervang None door 'Niet toegewezen' voor een duidelijkere grafiek
    processed_data = { (k if k is not None else 'Niet toegewezen'): v for k, v in data }
    chart_buffer = utils.generate_pie_chart(processed_data, "Toegewezen vs. Niet-toegewezen")
    return Response(chart_buffer.getvalue(), mimetype='image/png')

@bp.route('/kb_chart.png')
@login_required
def kb_chart():
    data = database.get_kb_category_counts()
    chart_buffer = utils.generate_bar_chart(dict(data), "KB Artikelen per Categorie", "Categorie", "Aantal Artikelen")
    return Response(chart_buffer.getvalue(), mimetype='image/png')