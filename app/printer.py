import os
import sys
import tempfile
import subprocess
from flask import current_app
from . import utils

def generate_ticket_print_content(ticket_data: dict) -> str:
    """Formatteert ticket data naar een schone string voor de printer."""
    # Valideer dat het ticket_id bestaat voordat we proberen te printen
    if 'id' not in ticket_data or not ticket_data['id']:
        raise ValueError("Ticket ID ontbreekt of is ongeldig")

    created_at_formatted = utils.format_datetime(ticket_data.get('created_at'), '%Y-%m-%d %H:%M:%S')

    content = [
        "--- NIEUW HELPDESK TICKET ---",
        f"\nTicket ID:      #{ticket_data.get('id')}",
        f"Aangemaakt op:  {created_at_formatted}",
        f"Prioriteit:     {ticket_data.get('priority', 'Niet gespecificeerd')}",  # Default waarde
        "--------------------------------",
        f"Aanvrager:      {ticket_data.get('requester_name', 'Onbekend') if ticket_data.get('requester_name') else 'Onbekend'}",
        f"Telefoon:       {'-'.join(filter(None, [ticket_data['requester_phone'][i:i+3] for i in range(0,len(ticket_data['requester_phone']),3)])) if ticket_data.get('requester_phone') else 'Niet gespecificeerd'}",  # Formatteert telefoonnummer
        f"E-mail:         {ticket_data.get('requester_email', 'Onbekend')}",
        "--------------------------------",
        f"Onderwerp:      {ticket_data.get('title', 'Geen onderwerp gegeven')}\n",
        f"Beschrijving:\n{ticket_data.get('description', 'Geen beschrijving gegeven').strip() or '(Leeg)'}\n",  # Handle empty description
        "--------------------------------",
        "\n*** Om veiligheidsredenen worden vertrouwelijke notities NIET geprint. ***"
    ]
    return "\n".join(content)

def print_new_ticket(ticket_data: dict) -> None:
    """
    Creëert een tijdelijk bestand met ticketinfo en stuurt dit naar de standaardprinter,
    indien geconfigureerd.
    """
    # Controleer of de printfunctionaliteit is ingeschakeld in de configuratie
    if not current_app.config.get('PRINT_NEW_TICKETS', False):
        return

    try:
        ticket_id = ticket_data.get('id')
        if not ticket_id:  # Extra validatie voor het ticket ID
            raise ValueError("Ticket heeft geen geldig ID")

        print_content = generate_ticket_print_content(ticket_data)
        path = None  # Initialiseer pad voor de finally-clausule

        try:
            # Creëer een veilig tijdelijk bestand.
            fd, path = tempfile.mkstemp(suffix=".txt", prefix="ticket-")
            with os.fdopen(fd, 'w', encoding='utf-8') as tmp_file:
                tmp_file.write(print_content)

            # Stuur het bestand naar de printer afhankelijk van het OS.
            if sys.platform.startswith('win'):
                try:
                    os.startfile(path, "print")
                except Exception as e:
                    current_app.logger.error(f"Fout bij printen op Windows: {e}")
            elif sys.platform.startswith(('darwin', 'linux')):
                # Probeer eerst met lpr
                try:
                    subprocess.run(['lpr', path], check=True, capture_output=True, text=True)
                except (FileNotFoundError, subprocess.CalledProcessError):
                    # Als dat mislukt, probeer dan lp
                    try:
                        subprocess.run(['lp', '-d', 'default', path], check=True, capture_output=True, text=True)
                    except Exception as e:
                        current_app.logger.error(f"Fout bij printen op Unix: {e}")
            else:
                current_app.logger.warning(f"Printen wordt niet ondersteund op dit OS: {sys.platform}")
                return

        finally:
            # Zorg ervoor dat het tijdelijke bestand altijd wordt opgeruimd.
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except Exception as e:
                    current_app.logger.error(f"Fout bij verwijderen van tijdelijk printbestand: {e}")

        # Log success
        current_app.logger.info(f"Ticket #{ticket_data.get('id')} succesvol naar de printer gestuurd.")

    except ValueError as ve:
        current_app.logger.warning(f"Printen overslaan voor ticket: {ve}")
    except Exception as e:
        current_app.logger.error(f"Onverwachte fout bij printproces: {e}")

