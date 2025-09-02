import webbrowser
import threading
import time
from waitress import serve
from app import create_app
from config.settings import HOST, PORT

# Maak de Flask applicatie aan
app = create_app()

def open_browser():
    """Wacht even en open dan de webbrowser naar de applicatie-URL."""
    # De kleine vertraging zorgt ervoor dat de server tijd heeft om volledig op te starten.
    time.sleep(1.25)
    webbrowser.open(f"http://{HOST}:{PORT}/")

def run_app():
    """Start de applicatie met een productie-grade server en opent de browser."""
    print(f"PyDesk wordt gestart op http://{HOST}:{PORT}")

    # Start de browser in een aparte thread om de server niet te blokkeren.
    threading.Thread(target=open_browser).start()

    # Gebruik waitress als de WSGI-server in plaats van de Flask dev server.
    serve(app, host=HOST, port=PORT, threads=4)

if __name__ == '__main__':
    run_app()