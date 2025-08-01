import sqlite3
from flask import Flask, g
from . import database, utils

def create_app():
    """De application factory functie."""
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = 'een-zeer-geheime-en-willekeurige-sleutel-voor-deze-app'

    # Registreer de teardown context voor de database
    @app.teardown_appcontext
    def close_db(e=None):
        db = g.pop('db', None)
        if db is not None:
            db.close()
            
    # Initialiseer de database bij het starten
    with app.app_context():
        database.init_db()

    # --- REGISTREER HET TEMPLATE FILTER ---
    app.jinja_env.filters['datetimeformat'] = utils.format_datetime

    # Importeer en registreer de blueprints
    from . import routes_main, routes_kb, routes_reports
    app.register_blueprint(routes_main.bp)
    app.register_blueprint(routes_kb.bp)
    app.register_blueprint(routes_reports.bp)

    return app