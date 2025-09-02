import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash
from config.settings import USERS

bp = Blueprint('auth', __name__, url_prefix='/auth')

def login_required(view):
    """
    Decorator die controleert of een gebruiker is ingelogd.
    Indien niet, wordt de gebruiker omgeleid naar de inlogpagina.
    """
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            flash('Je moet eerst inloggen om deze pagina te bekijken.', 'warning')
            return redirect(url_for('auth.login'))
        return view(**kwargs)

    return wrapped_view

@bp.route('/login', methods=('GET', 'POST'))
def login():
    """Verwerkt het inloggen van de gebruiker."""
    if g.user:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        error = None

        # Validatie
        if not username or not password:
            error = 'Gebruikersnaam en wachtwoord zijn verplicht.'
        else:
            user_hash = USERS.get(username)
            if not user_hash:
                error = 'Ongeldige gebruikersnaam of wachtwoord.'
            elif not check_password_hash(user_hash, password):
                error = 'Ongeldige gebruikersnaam of wachtwoord.'

        # Succesvolle login
        if error is None:
            session.clear()
            session['username'] = username
            session['master_password'] = password  # Opslaan als platte tekst (veilig in lokale context)
            flash(f'Welkom terug, {username}!', 'success')
            return redirect(url_for('main.index'))

        if error:
            flash(error, 'error')

    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    """Verwerkt het uitloggen van de gebruiker."""
    session.clear()
    flash('Je bent succesvol uitgelogd.', 'info')
    return redirect(url_for('auth.login'))
