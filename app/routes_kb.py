from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, current_app
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
    grouped_articles = defaultdict(list)
    for article in articles:
        # Convert row to dict if it's not already
        article_dict = dict(article) if hasattr(article, 'keys') else article
        grouped_articles[article_dict['category']].append(article_dict)

    return render_template('kb_index.html', grouped_articles=grouped_articles)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def kb_create():
    """Verwerkt het aanmaken van een nieuw kennisbankartikel."""
    if request.method == 'POST':
        # Valideer en verwerk POST data
        title = request.form.get('title', '').strip()
        category = request.form.get('category', '').strip()
        content = request.form.get('content', '').strip()

        validation_errors = []
        if not title:
            validation_errors.append("Titel")
        if not category:
            validation_errors.append("Categorie")
        if not content:
            validation_errors.append("Inhoud")

        if validation_errors:
            flash(f'{", ".join(validation_errors)} zijn verplichte velden.', 'error')
        else:
            try:
                database.create_kb_article(title, category, content)
                flash('Kennisbank artikel succesvol aangemaakt.', 'success')
                return redirect(url_for('kb.kb_index'))
            except Exception as e:
                current_app.logger.error(f"Fout bij aanmaken van kennisbankartikel: {e}")
                flash('Er is een fout opgetreden bij het opslaan van het artikel. Raadpleeg de logs voor details.', 'error')

    return render_template(
        'kb_form.html',
        article=None,
        title="Nieuw Artikel Aanmaken",
        action=url_for('kb.kb_create')
    )

@bp.route('/<int:article_id>')
@login_required
def kb_article(article_id):
    """Toont een specifiek kennisbankartikel."""
    try:
        article = database.get_kb_article_by_id(article_id)
        if not article:
            abort(404)

        # Convert row to dict for template consistency
        article_dict = dict(article) if hasattr(article, 'keys') else article

        return render_template('kb_article.html', article=article_dict)
    except Exception as e:
        current_app.logger.error(f"Fout bij ophalen van kennisbankartikel: {e}")
        abort(500)

@bp.route('/<int:article_id>/edit', methods=['GET', 'POST'])
@login_required
def kb_edit(article_id):
    """Verwerkt het bewerken van een kennisbankartikel."""
    try:
        article = database.get_kb_article_by_id(article_id)
        if not article:
            abort(404)

        # Convert row to dict for template consistency
        article_dict = dict(article) if hasattr(article, 'keys') else article

        if request.method == 'POST':
            title = request.form.get('title', '').strip()
            category = request.form.get('category', '').strip()
            content = request.form.get('content', '').strip()

            validation_errors = []
            if not title:
                validation_errors.append("Titel")
            if not category:
                validation_errors.append("Categorie")
            if not content:
                validation_errors.append("Inhoud")

            if validation_errors:
                flash(f'{", ".join(validation_errors)} zijn verplichte velden.', 'error')
            else:
                try:
                    database.update_kb_article(
                        article_id,
                        title=title,
                        category=category,
                        content=content
                    )
                    flash('Kennisbank artikel succesvol bijgewerkt.', 'success')
                    return redirect(url_for('kb.kb_article', article_id=article_id))
                except Exception as e:
                    current_app.logger.error(f"Fout bij updaten van kennisbankartikel: {e}")
                    flash('Er is een fout opgetreden bij het opslaan. Raadpleeg de logs voor details.', 'error')

        return render_template(
            'kb_form.html',
            article=article_dict,
            title="Artikel Bewerken",
            action=f"/kb/{article_id}/edit"
        )
    except Exception as e:
        current_app.logger.error(f"Fout in kb_edit: {e}")
        abort(500)

@bp.route('/<int:article_id>/delete', methods=['POST'])
@login_required
def kb_delete(article_id):
    """Verwijdert een kennisbankartikel."""
    try:
        article = database.get_kb_article_by_id(article_id)
        if not article:
            abort(404)

        # Voeg extra bevestiging toe voor gevaarlijke acties
        confirmation = request.form.get('confirmation', '').strip()
        if confirmation != f"delete_{article_id}":
            flash("Bevestigingsprobleem. Probeer het opnieuw.", "error")
            return redirect(url_for('kb.kb_article', article_id=article_id))

        try:
            database.delete_kb_article(article_id)
            flash('Kennisbank artikel succesvol verwijderd.', 'success')
            return redirect(url_for('kb.kb_index'))
        except Exception as e:
            current_app.logger.error(f"Fout bij verwijderen van kennisbankartikel: {e}")
            if "kennisbankartikel niet verwijderen - het wordt nog gebruikt door ticket(s)" in str(e):
                flash("Dit artikel kan niet worden verwijderd omdat het nog aan tickets is gekoppeld.", 'error')
            else:
                flash('Er is een fout opgetreden bij het verwijderen. Raadpleeg de logs voor details.', 'error')

    except Exception as e:
        current_app.logger.error(f"Fout in kb_delete: {e}")
        abort(500)

# --- Sjablonen Blueprint ---
bp_templates = Blueprint('templates', __name__, url_prefix='/templates')

@bp_templates.route('/')
@login_required
def templates_index():
    """Toont een overzicht van alle sjablonen."""
    try:
        templates = database.get_all_templates()
        return render_template(
            'templates_index.html',
            templates=[dict(t) if hasattr(t, 'keys') else t for t in templates]
        )
    except Exception as e:
        current_app.logger.error(f"Fout bij ophalen van sjablonen: {e}")
        abort(500)

@bp_templates.route('/create', methods=['GET', 'POST'])
@login_required
def templates_create():
    """Verwerkt het aanmaken van een nieuw sjabloon."""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()

        validation_errors = []
        if not title:
            validation_errors.append("Titel")
        if not content:
            validation_errors.append("Inhoud")

        if validation_errors:
            flash(f'{", ".join(validation_errors)} zijn verplichte velden.', 'error')
        else:
            try:
                database.create_template(title, content)
                flash("Sjabloon succesvol aangemaakt.", 'success')
                return redirect(url_for('templates.templates_index'))
            except Exception as e:
                current_app.logger.error(f"Fout bij aanmaken van sjabloon: {e}")
                flash('Er is een fout opgetreden bij het opslaan. Raadpleeg de logs voor details.', 'error')

    return render_template(
        'templates_form.html',
        template=None,
        title="Nieuw Sjabloon Aanmaken",
        action=url_for('templates.templates_create')
    )

@bp_templates.route('/<int:template_id>/edit', methods=['GET', 'POST'])
@login_required
def templates_edit(template_id):
    """Verwerkt het bewerken van een sjabloon."""
    try:
        template = database.get_template_by_id(template_id)
        if not template:
            abort(404)

        # Convert row to dict for template consistency
        template_dict = dict(template) if hasattr(template, 'keys') else template

        if request.method == 'POST':
            title = request.form.get('title', '').strip()
            content = request.form.get('content', '').strip()

            validation_errors = []
            if not title:
                validation_errors.append("Titel")
            if not content:
                validation_errors.append("Inhoud")

            if validation_errors:
                flash(f'{", ".join(validation_errors)} zijn verplichte velden.', 'error')
            else:
                try:
                    database.update_template(template_id, title=title, content=content)
                    flash("Sjabloon succesvol bijgewerkt.", 'success')
                    return redirect(url_for('templates.templates_index'))
                except Exception as e:
                    current_app.logger.error(f"Fout bij updaten van sjabloon: {e}")
                    flash('Er is een fout opgetreden bij het opslaan. Raadpleeg de logs voor details.', 'error')

        return render_template(
            'templates_form.html',
            template=template_dict,
            title="Sjabloon Bewerken",
            action=f"/templates/{template_id}/edit"
        )
    except Exception as e:
        current_app.logger.error(f"Fout in templates_edit: {e}")
        abort(500)

@bp_templates.route('/<int:template_id>/delete', methods=['POST'])
@login_required
def templates_delete(template_id):
    """Verwijdert een sjabloon."""
    try:
        template = database.get_template_by_id(template_id)
        if not template:
            abort(404)

        # Voeg extra bevestiging toe voor gevaarlijke acties
        confirmation = request.form.get('confirmation', '').strip()
        if confirmation != f"delete_{template_id}":
            flash("Bevestigingsprobleem. Probeer het opnieuw.", "error")
            return redirect(url_for('templates.templates_index'))

        try:
            database.delete_template(template_id)
            flash("Sjabloon succesvol verwijderd.", 'success')
            return redirect(url_for('templates.templates_index'))
        except Exception as e:
            current_app.logger.error(f"Fout bij verwijderen van sjabloon: {e}")
            flash('Er is een fout opgetreden bij het verwijderen. Raadpleeg de logs voor details.', 'error')
    except Exception as e:
        current_app.logger.error(f"Fout in templates_delete: {e}")
        abort(500)
