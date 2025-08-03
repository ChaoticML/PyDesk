import base64
import functools
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet, InvalidToken
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
from datetime import datetime
from flask import current_app

# De SALT is nu verplaatst naar de configuratie.

# --- DATUMFORMATTERING FUNCTIE ---
def format_datetime(value, format='%d-%m-%Y %H:%M'):
    """Converteert een ISO-datumstring naar een leesbaar formaat."""
    if not value:
        return ""
    try:
        # Probeer te parsen met en zonder microseconden voor flexibiliteit
        dt_object = datetime.fromisoformat(value)
    except (ValueError, TypeError):
        return value  # Geef de originele waarde terug als het parsen mislukt
    return dt_object.strftime(format)

# --- ENCRYPTIE FUNCTIES ---

@functools.lru_cache(maxsize=1)
def generate_key_from_password(password: str) -> bytes:
    """
    Genereert een encryptiesleutel van een wachtwoord met PBKDF2HMAC.
    Gebruikt lru_cache om te voorkomen dat de dure operatie onnodig wordt herhaald.
    """
    config = current_app.config
    salt = config['ENCRYPTION_SALT']
    iterations = config['ENCRYPTION_ITERATIONS']
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=iterations
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def encrypt_data(data: str, password: str) -> str | None:
    """Versleutelt de gegeven data met de afgeleide sleutel."""
    if not data:
        return None
    key = generate_key_from_password(password)
    f = Fernet(key)
    return f.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data: str, password: str) -> str:
    """Ontsleutelt de gegeven data met de afgeleide sleutel."""
    if not encrypted_data:
        return ""
    key = generate_key_from_password(password)
    f = Fernet(key)
    try:
        return f.decrypt(encrypted_data.encode()).decode()
    except InvalidToken:
        return "DECRYPTIE MISLUKT: Ongeldig hoofdwachtwoord?"

# --- GRAFIEK GENERATIE FUNCTIES ---

def generate_pie_chart(data_dict: dict, title: str) -> BytesIO:
    """Genereert een donut-stijl cirkeldiagram en retourneert het als een in-memory buffer."""
    fig, ax = plt.subplots()
    ax.pie(data_dict.values(), labels=data_dict.keys(), autopct='%1.1f%%', startangle=90, wedgeprops=dict(width=0.4))
    ax.axis('equal')  # Zorgt ervoor dat de cirkel een cirkel is.
    ax.set_title(title, pad=20)
    
    buf = BytesIO()
    fig.savefig(buf, format="png", transparent=True)
    plt.close(fig)  # Essentieel om geheugenlekkage te voorkomen
    buf.seek(0)
    return buf

def generate_bar_chart(data_dict: dict, title: str, xlabel: str, ylabel: str) -> BytesIO:
    """Genereert een staafdiagram en retourneert het als een in-memory buffer."""
    fig, ax = plt.subplots()
    ax.bar(data_dict.keys(), data_dict.values())
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.set_title(title)
    fig.tight_layout()  # Zorgt ervoor dat labels niet buiten de figuur vallen
    
    buf = BytesIO()
    fig.savefig(buf, format="png", transparent=True)
    plt.close(fig)
    buf.seek(0)
    return buf