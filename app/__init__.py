import sqlite3
from flask import Flask, g
from . import database

def create_app():
    """De application factory functie."""
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = 'een-zeer-geheime-en-willekeurige-sleutel-voor-deze-app'

    @app.teardown_appcontext
    def close_db(e=None):
        db = g.pop('db', None)
        if db is not None:
            db.close()
            
    with app.app_context():
        database.init_db()

    from . import routes_main, routes_kb, routes_reports
    app.register_blueprint(routes_main.bp)
    app.register_blueprint(routes_kb.bp)
    app.register_blueprint(routes_reports.bp)

    return app