from flask import Blueprint, render_template, request, redirect, url_for, Response
from . import database, utils

bp = Blueprint('reports', __name__, url_prefix='/reports')

@bp.route('/')
def reports_index():
    user = request.args.get('user')
    password = request.args.get('password')
    if not user or not password: return redirect(url_for('main.welcome'))
    return render_template('reports.html', user=user, password=password)

@bp.route('/status_chart.png')
def status_chart():
    data = database.get_status_counts()
    chart_buffer = utils.generate_pie_chart(data, "Tickets per Status")
    return Response(chart_buffer.getvalue(), mimetype='image/png')

@bp.route('/priority_chart.png')
def priority_chart():
    data = database.get_priority_counts()
    chart_buffer = utils.generate_pie_chart(data, "Tickets per Prioriteit")
    return Response(chart_buffer.getvalue(), mimetype='image/png')

@bp.route('/assignment_chart.png')
def assignment_chart():
    data = database.get_assignment_counts()
    chart_buffer = utils.generate_pie_chart(data, "Toegewezen vs. Niet-toegewezen")
    return Response(chart_buffer.getvalue(), mimetype='image/png')

@bp.route('/kb_chart.png')
def kb_chart():
    data = database.get_kb_category_counts()
    chart_buffer = utils.generate_bar_chart(data, "KB Artikelen per Categorie", "Categorie", "Aantal Artikelen")
    return Response(chart_buffer.getvalue(), mimetype='image/png')