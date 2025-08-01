from flask import Blueprint, render_template, request, redirect, url_for, flash
from collections import defaultdict
from . import database

# --- Kennisbank Blueprint (ongewijzigd) ---
bp = Blueprint('kb', __name__, url_prefix='/kb')

@bp.route('/')
def kb_index():
    user = request.args.get('user')
    password = request.args.get('password')
    if not user or not password: return redirect(url_for('main.welcome'))
    articles = database.get_all_kb_articles()
    grouped_articles = defaultdict(list)
    for article in articles: grouped_articles[article['category']].append(article)
    return render_template('kb_index.html', grouped_articles=grouped_articles, user=user, password=password)

@bp.route('/create', methods=['GET', 'POST'])
def kb_create():
    user = request.args.get('user')
    password = request.args.get('password')
    if not user or not password: return redirect(url_for('main.welcome'))
    if request.method == 'POST':
        database.create_kb_article(request.form['title'], request.form['category'], request.form['content'])
        return redirect(url_for('kb.kb_index', user=user, password=password))
    return render_template('kb_form.html', user=user, password=password, article=None, title="Nieuw Artikel Aanmaken")

@bp.route('/<int:article_id>')
def kb_article(article_id):
    user = request.args.get('user')
    password = request.args.get('password')
    if not user or not password: return redirect(url_for('main.welcome'))
    article = database.get_kb_article_by_id(article_id)
    if not article: return "Artikel niet gevonden", 404
    return render_template('kb_article.html', article=article, user=user, password=password)

@bp.route('/<int:article_id>/edit', methods=['GET', 'POST'])
def kb_edit(article_id):
    user = request.args.get('user')
    password = request.args.get('password')
    if not user or not password: return redirect(url_for('main.welcome'))
    article = database.get_kb_article_by_id(article_id)
    if request.method == 'POST':
        database.update_kb_article(article_id, request.form['title'], request.form['category'], request.form['content'])
        return redirect(url_for('kb.kb_article', article_id=article_id, user=user, password=password))
    return render_template('kb_form.html', user=user, password=password, article=article, title="Artikel Bewerken")

@bp.route('/<int:article_id>/delete', methods=['POST'])
def kb_delete(article_id):
    user = request.args.get('user')
    password = request.args.get('password')
    if not user or not password: return redirect(url_for('main.welcome'))
    database.delete_kb_article(article_id)
    return redirect(url_for('kb.kb_index', user=user, password=password))

# --- NIEUWE BLUEPRINT VOOR SJABLONEN ---
bp_templates = Blueprint('templates', __name__, url_prefix='/templates')

@bp_templates.route('/')
def templates_index():
    user = request.args.get('user')
    password = request.args.get('password')
    if not user or not password: return redirect(url_for('main.welcome'))
    
    templates = database.get_all_templates()
    return render_template('templates_index.html', templates=templates, user=user, password=password)

@bp_templates.route('/create', methods=['GET', 'POST'])
def templates_create():
    user = request.args.get('user')
    password = request.args.get('password')
    if not user or not password: return redirect(url_for('main.welcome'))

    if request.method == 'POST':
        database.create_template(request.form['title'], request.form['content'])
        flash("Sjabloon succesvol aangemaakt.", 'success')
        return redirect(url_for('templates.templates_index', user=user, password=password))
    
    return render_template('templates_form.html', user=user, password=password, template=None, title="Nieuw Sjabloon Aanmaken")

@bp_templates.route('/<int:template_id>/edit', methods=['GET', 'POST'])
def templates_edit(template_id):
    user = request.args.get('user')
    password = request.args.get('password')
    if not user or not password: return redirect(url_for('main.welcome'))

    template = database.get_template_by_id(template_id)
    if request.method == 'POST':
        database.update_template(template_id, request.form['title'], request.form['content'])
        flash("Sjabloon succesvol bijgewerkt.", 'success')
        return redirect(url_for('templates.templates_index', user=user, password=password))
        
    return render_template('templates_form.html', user=user, password=password, template=template, title="Sjabloon Bewerken")

@bp_templates.route('/<int:template_id>/delete', methods=['POST'])
def templates_delete(template_id):
    user = request.args.get('user')
    password = request.args.get('password')
    if not user or not password: return redirect(url_for('main.welcome'))

    database.delete_template(template_id)
    flash("Sjabloon succesvol verwijderd.", 'success')
    return redirect(url_for('templates.templates_index', user=user, password=password))