import os
import sys

# ==============================================================================
# PyDesk CONFIGURATIE
# Dit bestand bevat alle instellingen voor de PyDesk applicatie.
# ==============================================================================

# --- Server Instellingen ---
HOST = '127.0.0.1'
PORT = 5001

# --- Applicatie Configuratie ---
SECRET_KEY = 'change-this-to-a-real-secret-key-in-production'

# --- Printer Instellingen ---
PRINT_NEW_TICKETS = True

# --- Pad naar het databasebestand ---
if getattr(sys, 'frozen', False):
    # Als de applicatie is 'bevroren' (gebundeld met PyInstaller)
    application_path = os.path.dirname(sys.executable)
else:
    # In een normale ontwikkelomgeving
    application_path = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(application_path, os.pardir))

DATABASE_FILE = os.path.join(PROJECT_ROOT, 'data', 'tickets.db')

# --- Gebruikersauthenticatie ---
USERS = {
    "admin": "scrypt:32768:8:1$uei4xBji4Z6afAQw$2ef112b5e13e5aad4576149f9533adaa0bcf0aef211ffe99830834915d9c050834664b607ae332108ab3857a4618cdb1ad607f75ed2bf3b20e4e56296b6840f3"
}

# --- Encryptie Instellingen ---
ENCRYPTION_SALT = b'q\x8c\xbf\xe3\x9c\x01\xfd`\xe9\x1f\xd1\xec\x97\xd8\xda\x15'
ENCRYPTION_ITERATIONS = 480000
