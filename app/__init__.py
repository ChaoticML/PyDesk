import sqlite3
from flask import Flask, g
from . import database, utils

def create_app():
    """De application factory functie."""
    app = Flask(__name__)
    
    # Deze sleutel is essentieel voor het beveiligen van de sessie!
    # Verander dit in een unieke, willekeurige string.
    app.config['SECRET_KEY'] = 'vervang-dit-door-een-echte-willekeurige-geheime-sleutel'
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

    @app.teardown_appcontext
    def close_db(e=None):
        db = g.pop('db', None)
        if db is not None:
            db.close()
            
    with app.app_context():
        database.init_db()

    app.jinja_env.filters['datetimeformat'] = utils.format_datetime

    # Importeer en registreer de blueprints
    from . import routes_main, routes_kb, routes_reports, auth # NIEUW: auth importeren
    app.register_blueprint(auth.bp) # NIEUW: auth blueprint registreren
    app.register_blueprint(routes_main.bp)
    app.register_blueprint(routes_kb.bp)
    app.register_blueprint(routes_reports.bp)
    
    # REGISTREER DE SJABLONEN BLUEPRINT
    from .routes_kb import bp_templates
    app.register_blueprint(bp_templates)

    return app