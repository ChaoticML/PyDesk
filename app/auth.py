import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash
from config.settings import USERS

bp = Blueprint('auth', __name__, url_prefix='/auth')

# --- 1. DEFINIEER DE DECORATOR EERST ---
def login_required(view):
    """
    Decorator die controleert of een gebruiker is ingelogd.
    Indien niet, wordt de gebruiker omgeleid naar de inlogpagina.
    """
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        # De enige taak is nu controleren. Het laden gebeurt in app.before_request.
        if g.user is None:
            flash('Je moet eerst inloggen om deze pagina te bekijken.', 'warning')
            return redirect(url_for('auth.login'))
        
        return view(**kwargs)

    return wrapped_view

# --- 2. DEFINIEER DE ROUTES DAARNA ---
@bp.route('/login', methods=('GET', 'POST'))
def login():
    """Verwerkt het inloggen van de gebruiker."""
    if g.user:
        # Als de gebruiker al is geladen via before_request, stuur direct door.
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        # Gebruik .get() voor robuustere input handling en .strip() om witruimte te verwijderen.
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '') # Wachtwoorden niet strippen
        error = None

        if not username or not password:
            error = 'Gebruikersnaam en wachtwoord zijn verplicht.'
        else:
            user_hash = USERS.get(username)
            if user_hash is None:
                error = 'Ongeldige gebruikersnaam of wachtwoord.'
            elif not check_password_hash(user_hash, password):
                error = 'Ongeldige gebruikersnaam of wachtwoord.'

        if error is None:
            session.clear()
            session['username'] = username
            session['master_password'] = password
            
            flash(f'Welkom terug, {username}!', 'success')
            return redirect(url_for('main.index'))

        flash(error, 'error')

    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    """Verwerkt het uitloggen van de gebruiker."""
    session.clear()
    flash('Je bent succesvol uitgelogd.', 'info')
    return redirect(url_for('auth.login'))