import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet, InvalidToken
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
from datetime import datetime

SALT = b'q\x8c\xbf\xe3\x9c\x01\xfd`\xe9\x1f\xd1\xec\x97\xd8\xda\x15'

# ---  DATUMFORMATTERING FUNCTIE ---
def format_datetime(value, format='%d-%m-%Y %H:%M'):
    """Converteert een ISO-datumstring naar een leesbaar formaat."""
    if value is None:
        return ""
    # Probeer te parsen met en zonder microseconden voor flexibiliteit
    try:
        dt_object = datetime.fromisoformat(value)
    except ValueError:
        return value # Geef de originele waarde terug als het parsen mislukt
    return dt_object.strftime(format)

def generate_key_from_password(password):
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=SALT, iterations=480000)
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def encrypt_data(data, password):
    if not data: return None
    f = Fernet(generate_key_from_password(password))
    return f.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data, password):
    if not encrypted_data: return ""
    f = Fernet(generate_key_from_password(password))
    try:
        return f.decrypt(encrypted_data.encode()).decode()
    except InvalidToken:
        return "DECRYPTIE MISLUKT: Ongeldig hoofdwachtwoord?"

def generate_pie_chart(data_dict, title):
    fig, ax = plt.subplots()
    ax.pie(data_dict.values(), labels=data_dict.keys(), autopct='%1.1f%%', startangle=90, wedgeprops=dict(width=0.4))
    ax.axis('equal')
    ax.set_title(title, pad=20)
    buf = BytesIO()
    fig.savefig(buf, format="png", transparent=True)
    plt.close(fig)
    buf.seek(0)
    return buf

def generate_bar_chart(data_dict, title, xlabel, ylabel):
    fig, ax = plt.subplots()
    ax.bar(data_dict.keys(), data_dict.values())
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.set_title(title)
    fig.tight_layout()
    buf = BytesIO()
    fig.savefig(buf, format="png", transparent=True)
    plt.close(fig)
    buf.seek(0)
    return buf