import os
import sys
import tempfile
import subprocess
from datetime import datetime

def generate_ticket_print_content(ticket_data):
    """Formats ticket data into a clean string for printing."""
    ticket = dict(ticket_data)
    content = [
        "--- NIEUW HELPDESK TICKET ---",
        f"\nTicket ID:   #{ticket.get('id')}",
        f"Aangemaakt op:  {datetime.fromisoformat(ticket['created_at']).strftime('%Y-%m-%d %H:%M:%S')}",
        f"Prioriteit:    {ticket.get('priority')}",
        "--------------------------------",
        f"Aanvrager:   {ticket.get('requester_name')}",
        f"Telefoon:       {ticket.get('requester_phone')}",
        f"E-mail:       {ticket.get('requester_email')}",
        "--------------------------------",
        f"Onderwerp: {ticket.get('title')}\n",
        f"Beschrijving:\n{ticket.get('description')}\n",
        "--------------------------------",
        "\n*** Om veiligheidsredenen worden vertrouwelijke notities NIET geprint en zijn ze alleen zichtbaar in de app. ***"
    ]
    return "\n".join(content)

def print_new_ticket(ticket_data):
    """Creates a temporary file with ticket info and sends it to the default printer."""
    print_content = generate_ticket_print_content(ticket_data)

    try:
        fd, path = tempfile.mkstemp(suffix=".txt", prefix="ticket-")
        with os.fdopen(fd, 'w', encoding='utf-8') as tmp_file:
            tmp_file.write(print_content)

        if sys.platform.startswith('win'):
            os.startfile(path, "print")
        elif sys.platform.startswith('darwin'):
            subprocess.run(['lpr', path], check=True)
        elif sys.platform.startswith('linux'):
            subprocess.run(['lpr', path], check=True)
        else:
            print(f"Printen wordt niet ondersteund op dit OS: {sys.platform}")
            return

        print(f"Ticket #{ticket_data['id']} succesvol naar de printer gestuurd.")

    except Exception as e:
        print(f"Er is een fout opgetreden tijdens het printen: {e}")