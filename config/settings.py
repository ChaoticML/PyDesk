import os
import sys

# ==============================================================================
# HESK LITE CONFIGURATIE
# Dit bestand bevat alle instellingen voor de HESK Lite applicatie.
# ==============================================================================

# --- Server Instellingen ---
# Host en poort waarop de applicatie draait.
HOST = '127.0.0.1'
PORT = 5001

# --- Applicatie Configuratie ---
# BELANGRIJK: Vervang deze sleutel met een eigen, unieke waarde voor productie.
# Dit is essentieel voor de beveiliging van de sessie.
# Genereer een nieuwe met `secrets.token_hex(16)` in een Python-shell.
SECRET_KEY = 'change-this-to-a-real-secret-key-in-production'

# --- Printer Instellingen ---
# Zet op True om nieuwe tickets automatisch te printen, of False om dit uit te schakelen.
PRINT_NEW_TICKETS = False

# --- Pad naar het databasebestand ---
# Deze logica bepaalt automatisch de juiste locatie voor de database,
# zowel in de ontwikkelomgeving als in de gebundelde .exe-versie.
if getattr(sys, 'frozen', False):
    # Als de applicatie is 'bevroren' (gebundeld met PyInstaller)
    application_path = os.path.dirname(sys.executable)
    PROJECT_ROOT = application_path
else:
    # In een normale ontwikkelomgeving
    application_path = os.path.dirname(os.path.abspath(__file__))
    # Ga een niveau omhoog vanuit 'config' naar de project root
    PROJECT_ROOT = os.path.abspath(os.path.join(application_path, os.pardir))

DATABASE_FILE = os.path.join(PROJECT_ROOT, 'data', 'tickets.db')

# --- Gebruikersauthenticatie ---
# BELANGRIJK: Dit is een placeholder. Genereer uw eigen hash voor een sterk wachtwoord
# en vervang deze waarde voordat u de applicatie bouwt voor productie.
# Het standaard wachtwoord voor deze hash is 'test123'.
USERS = {
    "admin": "scrypt:32768:8:1$uei4xBji4Z6afAQw$2ef112b5e13e5aad4576149f9533adaa0bcf0aef211ffe99830834915d9c050834664b607ae332108ab3857a4618cdb1ad607f75ed2bf3b20e4e56296b6840f3"
}

# --- Encryptie Instellingen ---
# Een willekeurige, vaste salt voor het afleiden van de encryptiesleutel.
# BELANGRIJK: Deze salt mag NIET veranderen als u bestaande data wilt blijven ontsleutelen.
ENCRYPTION_SALT = b'q\x8c\xbf\xe3\x9c\x01\xfd`\xe9\x1f\xd1\xec\x97\xd8\xda\x15'
# Aantal iteraties voor de key derivation function. Hoger is veiliger maar trager.
ENCRYPTION_ITERATIONS = 480000