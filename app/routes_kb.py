from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from collections import defaultdict
from . import database
from .auth import login_required

# --- Kennisbank Blueprint ---
bp = Blueprint('kb', __name__, url_prefix='/kb')

@bp.route('/')
@login_required
def kb_index():
    """Toont een overzicht van alle kennisbankartikelen, gegroepeerd per categorie."""
    articles = database.get_all_kb_articles()
    # defaultdict is een efficiënte manier om dit te groeperen.
    grouped_articles = defaultdict(list)
    for article in articles:
        grouped_articles[article['category']].append(article)
    return render_template('kb_index.html', grouped_articles=grouped_articles)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def kb_create():
    """Verwerkt het aanmaken van een nieuw kennisbankartikel."""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        category = request.form.get('category', '').strip()
        content = request.form.get('content', '').strip()

        if not title or not category or not content:
            flash('Titel, categorie en inhoud zijn verplichte velden.', 'error')
        else:
            database.create_kb_article(title, category, content)
            flash('Kennisbank artikel succesvol aangemaakt.', 'success')
            return redirect(url_for('kb.kb_index'))
            
    return render_template('kb_form.html', article=None, title="Nieuw Artikel Aanmaken")

@bp.route('/<int:article_id>')
@login_required
def kb_article(article_id):
    """Toont een specifiek kennisbankartikel."""
    article = database.get_kb_article_by_id(article_id)
    if not article:
        abort(404)  # Geeft een standaard 'Not Found' pagina weer.
    return render_template('kb_article.html', article=article)

@bp.route('/<int:article_id>/edit', methods=['GET', 'POST'])
@login_required
def kb_edit(article_id):
    """Verwerkt het bewerken van een kennisbankartikel."""
    article = database.get_kb_article_by_id(article_id)
    if not article:
        abort(404)

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        category = request.form.get('category', '').strip()
        content = request.form.get('content', '').strip()

        if not title or not category or not content:
            flash('Titel, categorie en inhoud zijn verplichte velden.', 'error')
        else:
            database.update_kb_article(article_id, title, category, content)
            flash('Kennisbank artikel succesvol bijgewerkt.', 'success')
            return redirect(url_for('kb.kb_article', article_id=article_id))
            
    return render_template('kb_form.html', article=article, title="Artikel Bewerken")

@bp.route('/<int:article_id>/delete', methods=['POST'])
@login_required
def kb_delete(article_id):
    """Verwijdert een kennisbankartikel."""
    # Controleer of het artikel bestaat voordat het wordt verwijderd.
    article = database.get_kb_article_by_id(article_id)
    if not article:
        abort(404)
        
    database.delete_kb_article(article_id)
    flash('Kennisbank artikel succesvol verwijderd.', 'success')
    return redirect(url_for('kb.kb_index'))

# --- Sjablonen Blueprint ---
bp_templates = Blueprint('templates', __name__, url_prefix='/templates')

@bp_templates.route('/')
@login_required
def templates_index():
    """Toont een overzicht van alle sjablonen."""
    templates = database.get_all_templates()
    return render_template('templates_index.html', templates=templates)

@bp_templates.route('/create', methods=['GET', 'POST'])
@login_required
def templates_create():
    """Verwerkt het aanmaken van een nieuw sjabloon."""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()

        if not title or not content:
            flash('Titel en inhoud zijn verplichte velden.', 'error')
        else:
            database.create_template(title, content)
            flash("Sjabloon succesvol aangemaakt.", 'success')
            return redirect(url_for('templates.templates_index'))
            
    return render_template('templates_form.html', template=None, title="Nieuw Sjabloon Aanmaken")

@bp_templates.route('/<int:template_id>/edit', methods=['GET', 'POST'])
@login_required
def templates_edit(template_id):
    """Verwerkt het bewerken van een sjabloon."""
    template = database.get_template_by_id(template_id)
    if not template:
        abort(404)

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()

        if not title or not content:
            flash('Titel en inhoud zijn verplichte velden.', 'error')
        else:
            database.update_template(template_id, title, content)
            flash("Sjabloon succesvol bijgewerkt.", 'success')
            return redirect(url_for('templates.templates_index'))
            
    return render_template('templates_form.html', template=template, title="Sjabloon Bewerken")

@bp_templates.route('/<int:template_id>/delete', methods=['POST'])
@login_required
def templates_delete(template_id):
    """Verwijdert een sjabloon."""
    template = database.get_template_by_id(template_id)
    if not template:
        abort(404)
        
    database.delete_template(template_id)
    flash("Sjabloon succesvol verwijderd.", 'success')
    return redirect(url_for('templates.templates_index'))