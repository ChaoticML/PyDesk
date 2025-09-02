import base64
import functools
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet, InvalidToken
import matplotlib as mpl  # Gebruik 'as' om conflict met andere imports te voorkomen
mpl.use('Agg')  # Zorg ervoor dat we geen GUI backend gebruiken
import matplotlib.pyplot as plt
from io import BytesIO
from datetime import datetime
import math  # Voeg toe voor wiskundige functies
from flask import current_app

# --- DATUMFORMATTERING FUNCTIE ---
def format_datetime(value, format='%d-%m-%Y %H:%M'):
    """
    Converteert een ISO-datumstring naar een leesbaar formaat.
    Args:
        value: De datum als string of datetime object
        format: Het gewenste uitvoerformat (default: DD-MM-JJ HH:MM)
    Returns:
        Geformateerde datumsring, of de originele waarde bij mislukking
    """
    if not value or isinstance(value, str) and not value.strip():
        return ""

    try:
        # Probeer te parsen met en zonder microseconden voor flexibiliteit
        dt_object = datetime.fromisoformat(str(value)) if isinstance(value, (str, bytes)) else value

        # Zorg ervoor dat we een valide datetime object hebben
        if not isinstance(dt_object, datetime):
            return str(value)

    except (ValueError, TypeError) as e:
        current_app.logger.debug(f"Fout bij parsen van datum: {e}")
        return str(value)  # Geef de originele waarde terug als het parsen mislukt

    try:
        return dt_object.strftime(format)
    except AttributeError:
        return str(dt_object)

# --- ENCRYPTIE FUNCTIES ---
@functools.lru_cache(maxsize=128)  # Verhoogde cachegrootte voor meer wachtwoorden
def generate_key_from_password(password: str, salt=None, iterations=None):
    """
    Genereert een encryptiesleutel van een wachtwoord met PBKDF2HMAC.
    Args:
        password: Het hoofdwachtwoord om de sleutel af te leiden
        salt: Optioneel zout (wordt overruled door app config)
        iterations: Optioneel iteratiegemiddeld (wordt overruled door app config)

    Returns:
        De geencodeerde encryptiesleutel als bytes object

    Raises:
        ValueError als er geen geldig wachtwoord of zout kan worden verkregen
    """
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
    """
    Versleutelt de gegeven data met een afgeleide sleutel.
    Args:
        data: De te versleutelen string
        password: Het hoofdwachtwoord voor het genereren van de sleutel

    Returns:
        De versleutelde data als base64-gecodeerde string, of None bij mislukking
    """
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
    """
    Ontsleutelt de gegeven data met een afgeleide sleutel.
    Args:
        encrypted_data: De te ontsleutelen base64-gecodeerde string
        password: Het hoofdwachtwoord voor het genereren van de sleutel

    Returns:
        De ontsleutelde data als string, of bytes bij mislukking
    """
    if not isinstance(encrypted_data, str):
        current_app.logger.warning(f"Ongeldig type gegeven aan decrypt_data: {type(encrypted_data)}")
        return b"DECRYPTIE MISLUKT"

    try:
        key = generate_key_from_password(password)
        f = Fernet(key)

        # Handle empty data
        if not encrypted_data or (isinstance(encrypted_data, str) and not encrypted_data.strip()):
            return ""

        decrypted_bytes = f.decrypt(encrypted_data.encode())
        return decrypted_bytes.decode()
    except InvalidToken as e:
        current_app.logger.warning(f"Ongeldig encryptietoken ontvangen: {e}")
        return b"DECRYPTIE MISLUKT"
    except Exception as e:
        current_app.logger.error(f"Fout bij ontsleutelen: {e}")
        return b"DECRYPTIE MISLUKT"

# --- GRAFIEK GENERATIE FUNCTIES ---
def _generate_chart_base(data_dict, title):
    """
    Helper functie om basisgrafiekconfiguratie te creëren.
    Args:
        data_dict: De gegevens voor de grafiek
        title: De titel van de grafiek

    Returns:
        fig en ax objecten met basiscfg
    """
    if not isinstance(data_dict, dict) or len(data_dict) == 0:
        raise ValueError("Data dictionary mag niet leeg zijn")

    # Maak een nieuwe figuur en as aan voor elke grafiek om geheugenlekkage te voorkomen
    with plt.figure(figsize=(8, 6), dpi=150):
        ax = plt.gca()
        return plt.gcf(), ax

def generate_pie_chart(data_dict: dict, title: str) -> BytesIO:
    """
    Genereert een donut-stijl cirkeldiagram en retourneert het als in-memory buffer.
    Args:
        data_dict: Dictionary met labels (keys) en waarden
        title: Titel voor de grafiek

    Returns:
        BytesIO object met de gegenereerde afbeelding
    """
    try:
        fig, ax = _generate_chart_base(data_dict, title)

        # Voeg een 'Geen Data' label toe als er geen gegevens zijn
        if not data_dict or all(v == 0 for v in data_dict.values()):
            ax.text(0.5, 0.5,
                   "Geen data beschikbaar",
                   horizontalalignment='center',
                   verticalalignment='center')
        else:
            # Voeg een 'Andere' categorie toe voor kleine waarden
            total = sum(data_dict.values())
            other_threshold = max(total * 0.1, math.isfinite(2) if not math.isnan(2) else float('inf') if len(data_dict) <= 3 else 2)

            filtered_data = {}
            others_sum = 0

            for key in data_dict:
                value = data_dict[key]
                # Fixed: Removed the 'isinstance(value, (int, float))' check as it's not necessary here
                if math.isfinite(float(value)):
                    if value >= other_threshold or len(data_dict) <= 3:  # Geen 'Andere' voor kleine datasets
                        filtered_data[key] = int(round(float(value)))
                    else:
                        others_sum += float(value)

            if others_sum > 0 and not math.isnan(others_sum):
                filtered_data['Andere'] = int(round(others_sum))

            ax.pie(
                filtered_data.values(),
                labels=filtered_data.keys(),
                autopct='%1.1f%%',
                startangle=90,
                wedgeprops={'width': 0.4, 'edgecolor': 'white'}
            )

        # Configureer de grafiek
        ax.axis('equal')
        ax.set_title(title, pad=20)
        fig.tight_layout()

    except Exception as e:
        current_app.logger.error(f"Fout bij genereren van pie chart: {e}")
        raise

def generate_bar_chart(data_dict: dict, title: str, xlabel: str = None, ylabel: str = None) -> BytesIO:
    """
    Genereert een staafdiagram en retourneert het als in-memory buffer.
    Args:
        data_dict: Dictionary met labels (keys) en waarden
        title: Titel voor de grafiek
        xlabel: Label voor X-as (optioneel)
        ylabel: Label voor Y-as (optioneel)

    Returns:
        BytesIO object met de gegenereerde afbeelding
    """
    try:
        fig, ax = _generate_chart_base(data_dict, title)

        # Voeg een 'Geen Data' label toe als er geen gegevens zijn
        if not data_dict or all(v == 0 for v in data_dict.values()):
            ax.text(0.5, 0.7,
                   "Geen data beschikbaar",
                   horizontalalignment='center',
                   verticalalignment='center')
        else:
            # Zorg voor een consistente kleurenpalet
            colors = mpl.colors.TABLEAU_COLORS if hasattr(mpl.colors, 'TABLEAU_COLORS') else None

            ax.bar(
                data_dict.keys(),
                [int(v) for v in data_dict.values()],
                color=colors,
                edgecolor='white',
                linewidth=0.7
            )

        # Voeg labels toe als deze zijn gegeven
        if xlabel:
            ax.set_xlabel(xlabel)
        if ylabel:
            ax.set_ylabel(ylabel)

    except Exception as e:
        current_app.logger.error(f"Fout bij genereren van bar chart: {e}")
        raise

def _finalize_chart(fig):
    """
    Sluit een grafiek figuur af en keert deze terug als buffer.
    """
    buf = BytesIO()

    try:
        # Zorg ervoor dat de achtergrond transparant is
        fig.patch.set_facecolor('none')
        for spine in plt.gca().spines.values():
            spine.set_visible(False)

        # Save the figure to a bytes buffer
        fig.savefig(buf, format="png", transparent=True)
    except Exception as e:
        current_app.logger.error(f"Fout bij finaliseren van grafiek: {e}")
        raise  # Gooi de exceptie opnieuw op na het loggen
    finally:
        # Dit blok wordt altijd uitgevoerd
        plt.close(fig)  # Essentieel om geheugenlekkage te voorkomen
        buf.seek(0)

    return buf