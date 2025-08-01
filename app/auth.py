import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash
from config.settings import USERS  # Importeer de gedefinieerde gebruikers

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    """Verwerkt het inloggen van de gebruiker."""
    # Als de gebruiker al is ingelogd, stuur direct door naar de index.
    if 'username' in session:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None

        user_hash = USERS.get(username)

        if user_hash is None:
            error = 'Ongeldige gebruikersnaam.'
        elif not check_password_hash(user_hash, password):
            error = 'Ongeldig wachtwoord.'

        if error is None:
            # Sla de gebruiker op in een nieuwe, schone sessie
            session.clear()
            session['username'] = username
            # BELANGRIJK: Sla het wachtwoord op in de sessie voor data-decryptie.
            # Dit is veiliger dan in de URL, maar blijft een gevoelig punt.
            session['master_password'] = password
            
            flash(f'Welkom terug, {username}!', 'success')
            return redirect(url_for('main.index'))

        flash(error, 'error')

    return render_template('login.html')

@bp.route('/logout')
def logout():
    """Verwerkt het uitloggen van de gebruiker."""
    session.clear()
    flash('Je bent succesvol uitgelogd.', 'info')
    return redirect(url_for('auth.login'))

def login_required(view):
    """
    Decorator die controleert of een gebruiker is ingelogd.
    Indien niet, wordt de gebruiker omgeleid naar de inlogpagina.
    """
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'username' not in session or 'master_password' not in session:
            flash('Je moet eerst inloggen om deze pagina te bekijken.', 'warning')
            return redirect(url_for('auth.login'))
        
        # Maak de gebruiker en het master wachtwoord beschikbaar voor de view via het g-object
        g.user = session['username']
        g.master_password = session['master_password']

        return view(**kwargs)

    return wrapped_view