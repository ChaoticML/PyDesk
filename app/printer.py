import os
import sys
import tempfile
import subprocess
from flask import current_app
from . import utils

def generate_ticket_print_content(ticket_data: dict) -> str:
    """Formatteert ticket data naar een schone string voor de printer."""
    # Gebruik de robuuste, centrale datumformattering uit utils.py
    created_at_formatted = utils.format_datetime(ticket_data.get('created_at'), '%Y-%m-%d %H:%M:%S')

    content = [
        "--- NIEUW HELPDESK TICKET ---",
        f"\nTicket ID:      #{ticket_data.get('id')}",
        f"Aangemaakt op:  {created_at_formatted}",
        f"Prioriteit:     {ticket_data.get('priority')}",
        "--------------------------------",
        f"Aanvrager:      {ticket_data.get('requester_name')}",
        f"Telefoon:       {ticket_data.get('requester_phone')}",
        f"E-mail:         {ticket_data.get('requester_email')}",
        "--------------------------------",
        f"Onderwerp: {ticket_data.get('title')}\n",
        f"Beschrijving:\n{ticket_data.get('description')}\n",
        "--------------------------------",
        "\n*** Om veiligheidsredenen worden vertrouwelijke notities NIET geprint. ***"
    ]
    return "\n".join(content)

def print_new_ticket(ticket_data: dict) -> None:
    """
    Creëert een tijdelijk bestand met ticketinfo en stuurt dit naar de standaardprinter,
    indien geconfigureerd.
    """
    # Controleer of de printfunctionaliteit is ingeschakeld in de configuratie.
    if not current_app.config.get('PRINT_NEW_TICKETS', False):
        return

    print_content = generate_ticket_print_content(ticket_data)
    path = None  # Initialiseer pad voor de finally-clausule

    try:
        # Creëer een veilig tijdelijk bestand.
        fd, path = tempfile.mkstemp(suffix=".txt", prefix="ticket-")
        with os.fdopen(fd, 'w', encoding='utf-8') as tmp_file:
            tmp_file.write(print_content)

        # Stuur het bestand naar de printer afhankelijk van het OS.
        if sys.platform.startswith('win'):
            os.startfile(path, "print")
        elif sys.platform.startswith('darwin') or sys.platform.startswith('linux'):
            subprocess.run(['lpr', path], check=True, capture_output=True, text=True)
        else:
            current_app.logger.warning(f"Printen wordt niet ondersteund op dit OS: {sys.platform}")
            return

        current_app.logger.info(f"Ticket #{ticket_data.get('id')} succesvol naar de printer gestuurd.")

    except FileNotFoundError:
        current_app.logger.error("Printen mislukt: 'lpr' commando niet gevonden. Is CUPS geïnstalleerd?")
    except subprocess.CalledProcessError as e:
        current_app.logger.error(f"Fout bij het aanroepen van 'lpr': {e.stderr}")
    except Exception as e:
        current_app.logger.error(f"Een onverwachte fout is opgetreden tijdens het printen: {e}")
    finally:
        # Zorg ervoor dat het tijdelijke bestand altijd wordt opgeruimd.
        if path and os.path.exists(path):
            os.remove(path)
