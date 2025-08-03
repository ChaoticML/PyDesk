import webbrowser
import threading
from waitress import serve
from app import create_app
from config.settings import HOST, PORT

# Maak de Flask applicatie aan
app = create_app()

def open_browser():
    """Wacht even en open dan de webbrowser naar de applicatie-URL."""
    # De kleine vertraging zorgt ervoor dat de server tijd heeft om volledig op te starten.
    threading.Timer(1.25, lambda: webbrowser.open(f"http://{HOST}:{PORT}/")).start()

def run_app():
    """Start de applicatie met een productie-grade server en opent de browser."""
    print(f"HESK Lite wordt gestart op http://{HOST}:{PORT}")
    
    # Start de browser in een aparte thread om de server niet te blokkeren.
    open_browser()
    
    # Gebruik waitress als de WSGI-server in plaats van de Flask dev server.
    serve(app, host=HOST, port=PORT, threads=4)

if __name__ == '__main__':
    run_app()