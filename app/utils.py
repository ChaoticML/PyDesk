import base64
import functools
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet, InvalidToken
import matplotlib as mpl
mpl.use('Agg')  # Zorg ervoor dat we geen GUI backend gebruiken
import matplotlib.pyplot as plt
from io import BytesIO
from datetime import datetime
from flask import current_app

# --- DATUMFORMATTERING FUNCTIE ---
def format_datetime(value, format='%d-%m-%Y %H:%M'):
    """Converteert een ISO-datumstring naar een leesbaar formaat."""
    if not value or isinstance(value, str) and not value.strip():
        return ""
    try:
        dt_object = datetime.fromisoformat(str(value)) if isinstance(value, (str, bytes)) else value
        if not isinstance(dt_object, datetime):
            return str(value)
    except (ValueError, TypeError) as e:
        current_app.logger.debug(f"Fout bij parsen van datum: {e}")
        return str(value)
    try:
        return dt_object.strftime(format)
    except AttributeError:
        return str(dt_object)

# --- ENCRYPTIE FUNCTIES ---
@functools.lru_cache(maxsize=128)
def generate_key_from_password(password: str, salt=None, iterations=None):
    """Genereert een encryptiesleutel van een wachtwoord met PBKDF2HMAC."""
    if not password or isinstance(password, str) and not password.strip():
        raise ValueError("Wachtwoord mag niet leeg zijn")
    config = current_app.config
    salt = salt or config.get('ENCRYPTION_SALT')
    iterations = iterations or config.get('ENCRYPTION_ITERATIONS', 480000)
    if not salt:
        raise ValueError("Geen zout beschikbaar voor encryptie")
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=int(iterations)
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def encrypt_data(data: str, password: str) -> str | None:
    """Versleutelt de gegeven data met een afgeleide sleutel."""
    if not isinstance(data, str):
        current_app.logger.warning(f"Ongeldig type gegeven aan encrypt_data: {type(data)}")
        return None
    try:
        key = generate_key_from_password(password)
        f = Fernet(key)
        encrypted_bytes = f.encrypt(data.encode())
        return encrypted_bytes.decode()
    except Exception as e:
        current_app.logger.error(f"Fout bij versleutelen: {e}")
        return None

def decrypt_data(encrypted_data: str, password: str) -> str | bytes:
    """Ontsleutelt de gegeven data met een afgeleide sleutel."""
    if not isinstance(encrypted_data, str):
        current_app.logger.warning(f"Ongeldig type gegeven aan decrypt_data: {type(encrypted_data)}")
        return b"DECRYPTIE MISLUKT"
    try:
        key = generate_key_from_password(password)
        f = Fernet(key)
        if not encrypted_data or (isinstance(encrypted_data, str) and not encrypted_data.strip()):
            return ""
        decrypted_bytes = f.decrypt(encrypted_data.encode())
        return decrypted_bytes.decode()
    except InvalidToken:
        return b"DECRYPTIE MISLUKT (ongeldig token)"
    except Exception as e:
        current_app.logger.error(f"Fout bij ontsleutelen: {e}")
        return b"DECRYPTIE MISLUKT"

# --- GRAFIEK GENERATIE FUNCTIES ---

def _finalize_chart(fig: plt.Figure) -> BytesIO:
    """Slaat een Matplotlib figuur op in een in-memory buffer en sluit het figuur."""
    buf = BytesIO()
    try:
        fig.tight_layout(pad=1.0)
        fig.savefig(buf, format="png", transparent=True)
        buf.seek(0)
        return buf
    finally:
        plt.close(fig)  # Essentieel om geheugenlekkage te voorkomen

def generate_pie_chart(data_dict: dict, title: str) -> BytesIO:
    """Genereert een donut-stijl cirkeldiagram."""
    fig, ax = plt.subplots(figsize=(8, 5), dpi=100)
    
    # Toon 'Geen data' melding als de dictionary leeg is
    if not data_dict or all(v == 0 for v in data_dict.values()):
        ax.text(0.5, 0.5, "Geen data beschikbaar", horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
        ax.axis('off') # Verberg de assen
    else:
        # Aggregeer kleine waarden in een 'Andere' categorie
        total = sum(data_dict.values())
        threshold = total * 0.05  # items kleiner dan 5% worden gegroepeerd
        
        filtered_data = {}
        others_sum = 0
        for key, value in data_dict.items():
            if value < threshold and len(data_dict) > 3:
                others_sum += value
            else:
                filtered_data[key] = value
        
        if others_sum > 0:
            filtered_data['Andere'] = others_sum

        ax.pie(
            filtered_data.values(),
            labels=filtered_data.keys(),
            autopct='%1.1f%%',
            startangle=90,
            wedgeprops={'width': 0.4, 'edgecolor': 'white'}
        )
        ax.axis('equal')

    ax.set_title(title, pad=20)
    return _finalize_chart(fig)

def generate_bar_chart(data_dict: dict, title: str) -> BytesIO:
    """Genereert een staafdiagram."""
    fig, ax = plt.subplots(figsize=(8, 5), dpi=100)

    # Toon 'Geen data' melding als de dictionary leeg is
    if not data_dict or all(v == 0 for v in data_dict.values()):
        ax.text(0.5, 0.5, "Geen data beschikbaar", horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
        ax.axis('off') # Verberg de assen
    else:
        keys = list(data_dict.keys())
        values = list(data_dict.values())
        
        ax.bar(keys, values, color=plt.cm.viridis(0.6))
        
        # Verbeter layout
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.tick_params(axis='x', rotation=45)
    
    ax.set_title(title, pad=20)
    return _finalize_chart(fig)