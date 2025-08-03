import os
import sys

# Server Instellingen
HOST = '127.0.0.1'
PORT = 5001

# Applicatie Configuratie
SECRET_KEY = 'jouw-geheime-sleutel-hier'

# Printer Instellingen
PRINT_NEW_TICKETS = False  # Zet op False om automatisch printen uit te schakelen

# Pad naar het databasebestand
# Bepaal het correcte pad voor het databasebestand, ook voor PyInstaller.
if getattr(sys, 'frozen', False):
    # Als de applicatie is 'bevroren' (gebundeld met PyInstaller)
    application_path = os.path.dirname(sys.executable)
else:
    # In een normale ontwikkelomgeving
    application_path = os.path.dirname(os.path.abspath(__file__))

# Ga een niveau omhoog vanuit 'config' naar de project root
PROJECT_ROOT = os.path.abspath(os.path.join(application_path, os.pardir))
DATABASE_FILE = os.path.join(PROJECT_ROOT, 'data', 'tickets.db')

# Gebruikersauthenticatie
USERS = {
    "admin": "scrypt:..." # Jouw hash
}

# Encryptie Instellingen
# Een willekeurige, vaste salt voor het afleiden van de encryptiesleutel.
# Deze moet geheim blijven en niet veranderen, anders kunnen oude data niet meer worden ontsleuteld.
ENCRYPTION_SALT = b'q\x8c\xbf\xe3\x9c\x01\xfd`\xe9\x1f\xd1\xec\x97\xd8\xda\x15'
# Aantal iteraties voor de key derivation function. Hoger is veiliger maar trager.
ENCRYPTION_ITERATIONS = 480000