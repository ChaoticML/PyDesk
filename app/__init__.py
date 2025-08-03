import sqlite3
from flask import Flask, g, session

def create_app():
    """De application factory functie."""
    app = Flask(__name__)
    
    # --- 1. Centraliseer Configuratie ---
    # Laad configuratie vanuit het settings.py bestand
    app.config.from_object('config.settings')
    
    # Stel extra sessie-instellingen in voor veiligheid
    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax'
    )

    # --- 2. Beheer Database Connectie Centraal ---
    def get_db():
        """Maakt een database connectie aan of retourneert de bestaande."""
        if 'db' not in g:
            g.db = sqlite3.connect(app.config['DATABASE_FILE'])
            g.db.row_factory = sqlite3.Row
        return g.db

    @app.teardown_appcontext
    def close_db(e=None):
        """Sluit de database connectie aan het einde van de request."""
        db = g.pop('db', None)
        if db is not None:
            db.close()

    # --- 3. Initialiseer de Database ---
    from . import database
    with app.app_context():
        # Geef de app configuratie door aan init_db
        database.init_db(app.config)
        
    # --- 4. Registreer Custom Jinja Filters ---
    from . import utils
    app.jinja_env.filters['datetimeformat'] = utils.format_datetime

    # --- 5. Registreer Blueprints ---
    from . import auth, routes_main, routes_kb, routes_reports
    app.register_blueprint(auth.bp)
    app.register_blueprint(routes_main.bp)
    app.register_blueprint(routes_kb.bp)
    app.register_blueprint(routes_reports.bp)
    
    from .routes_kb import bp_templates
    app.register_blueprint(bp_templates)
    
    # --- 6. Maak Gebruikersinformatie Beschikbaar in Elke Request ---
    @app.before_request
    def load_logged_in_user():
        """Laadt de gebruikersdata in g.user als de gebruiker is ingelogd."""
        username = session.get('username')
        if username is None:
            g.user = None
        else:
            # Hier kun je eventueel meer gebruikersinfo laden uit een database
            # Voor nu is de gebruikersnaam voldoende.
            g.user = username
            g.master_password = session.get('master_password')

    return app