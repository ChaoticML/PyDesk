import sqlite3
from flask import Flask, g, session
from datetime import datetime
import markdown
from markupsafe import Markup

def create_app():
    """De application factory functie."""
    app = Flask(__name__)
    
    # --- Laad Configuratie ---
    app.config.from_object('config.settings')
    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax'
    )

    # --- Koppel de teardown functie aan de app ---
    @app.teardown_appcontext
    def close_db(e=None):
        """Sluit de database connectie aan het einde van de request."""
        db = g.pop('db', None)
        if db is not None:
            db.close()

    # --- Initialiseer de Database ---
    from . import database
    with app.app_context():
        database.init_db(app.config)
        
    # --- Registreer Custom Jinja Filters ---
    from . import utils
    app.jinja_env.filters['datetimeformat'] = utils.format_datetime
    
    # Registreer het Markdown filter
    def markdown_filter(s):
        return Markup(markdown.markdown(s, extensions=['fenced_code', 'tables']))
    app.jinja_env.filters['markdown'] = markdown_filter

    # --- Registreer Blueprints ---
    from . import auth, routes_main, routes_kb, routes_reports
    app.register_blueprint(auth.bp)
    app.register_blueprint(routes_main.bp)
    app.register_blueprint(routes_kb.bp)
    app.register_blueprint(routes_reports.bp)
    
    from .routes_kb import bp_templates
    app.register_blueprint(bp_templates)
    
    # --- Functies die voor elke request worden uitgevoerd ---
    @app.before_request
    def before_request_callbacks():
        """
        Wordt uitgevoerd voor elke request.
        Opent de databaseverbinding en laadt de ingelogde gebruiker.
        """
        g.db = sqlite3.connect(app.config['DATABASE_FILE'])
        g.db.row_factory = sqlite3.Row
        
        username = session.get('username')
        g.user = username
        if username:
            g.master_password = session.get('master_password')
        else:
            g.master_password = None

    # --- Maak variabelen beschikbaar in alle templates ---
    @app.context_processor
    def inject_now():
        """Injecteert de huidige datum/tijd in de template context."""
        return {'now': datetime.utcnow()}

    return app