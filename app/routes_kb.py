from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from collections import defaultdict
from . import database
from .auth import login_required

# Kennisbank Blueprint
bp = Blueprint('kb', __name__, url_prefix='/kb')

@bp.route('/')
@login_required
def kb_index():
    articles = database.get_all_kb_articles()
    grouped_articles = defaultdict(list)
    for article in articles: grouped_articles[article['category']].append(article)
    return render_template('kb_index.html', grouped_articles=grouped_articles)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def kb_create():
    if request.method == 'POST':
        database.create_kb_article(request.form['title'], request.form['category'], request.form['content'])
        flash('Kennisbank artikel succesvol aangemaakt.', 'success')
        return redirect(url_for('kb.kb_index'))
    return render_template('kb_form.html', article=None, title="Nieuw Artikel Aanmaken")

@bp.route('/<int:article_id>')
@login_required
def kb_article(article_id):
    article = database.get_kb_article_by_id(article_id)
    if not article: 
        flash(f"Kennisbank artikel met ID {article_id} niet gevonden.", "error")
        return redirect(url_for('kb.kb_index'))
    return render_template('kb_article.html', article=article)

@bp.route('/<int:article_id>/edit', methods=['GET', 'POST'])
@login_required
def kb_edit(article_id):
    article = database.get_kb_article_by_id(article_id)
    if request.method == 'POST':
        database.update_kb_article(article_id, request.form['title'], request.form['category'], request.form['content'])
        flash('Kennisbank artikel succesvol bijgewerkt.', 'success')
        return redirect(url_for('kb.kb_article', article_id=article_id))
    return render_template('kb_form.html', article=article, title="Artikel Bewerken")

@bp.route('/<int:article_id>/delete', methods=['POST'])
@login_required
def kb_delete(article_id):
    database.delete_kb_article(article_id)
    flash('Kennisbank artikel succesvol verwijderd.', 'success')
    return redirect(url_for('kb.kb_index'))

# SJABLONEN BLUEPRINT
bp_templates = Blueprint('templates', __name__, url_prefix='/templates')

@bp_templates.route('/')
@login_required
def templates_index():
    templates = database.get_all_templates()
    return render_template('templates_index.html', templates=templates)

@bp_templates.route('/create', methods=['GET', 'POST'])
@login_required
def templates_create():
    if request.method == 'POST':
        database.create_template(request.form['title'], request.form['content'])
        flash("Sjabloon succesvol aangemaakt.", 'success')
        return redirect(url_for('templates.templates_index'))
    return render_template('templates_form.html', template=None, title="Nieuw Sjabloon Aanmaken")

@bp_templates.route('/<int:template_id>/edit', methods=['GET', 'POST'])
@login_required
def templates_edit(template_id):
    template = database.get_template_by_id(template_id)
    if request.method == 'POST':
        database.update_template(template_id, request.form['title'], request.form['content'])
        flash("Sjabloon succesvol bijgewerkt.", 'success')
        return redirect(url_for('templates.templates_index'))
    return render_template('templates_form.html', template=template, title="Sjabloon Bewerken")

@bp_templates.route('/<int:template_id>/delete', methods=['POST'])
@login_required
def templates_delete(template_id):
    database.delete_template(template_id)
    flash("Sjabloon succesvol verwijderd.", 'success')
    return redirect(url_for('templates.templates_index'))