# HESK Lite - Standalone Helpdesk Applicatie

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python)
![Flask](https://img.shields.io/badge/Flask-2.0-000000?logo=flask)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite)
![Status](https://img.shields.io/badge/Status-Actieve%20Ontwikkeling-blue)

## Overzicht

**HESK Lite** is een op maat gemaakte, volledig op zichzelf staande en veilige helpdesk-applicatie. Dit project is geïnspireerd op de functionaliteit van HESK en is ontworpen als een lichtgewicht, betrouwbaar en foolproof alternatief, specifiek gebouwd voor een gestroomlijnde, Nederlandstalige workflow.

De applicatie draait als één enkel `.exe`-bestand op Windows (en kan met enige aanpassing ook voor andere OS'en gebundeld worden), vereist geen installatie van externe software, databases of complexe configuraties, en slaat alle data lokaal op in een beveiligde, versleutelde database.

## Kernfunctionaliteiten

HESK Lite focust op de essentiële functionaliteiten van een modern helpdesk-systeem:

*   **Ticket Management:**
    *   Beheer de volledige levenscyclus van tickets: aanmaken, bekijken, toewijzen en bijwerken met statussen (Nieuw, In Behandeling, Opgelost, Gesloten).
    *   **Geavanceerd Overzicht:** Zoek, filter (op toewijzing) en sorteer (op datum, prioriteit, status) moeiteloos door alle tickets.
    *   **Visuele Indicatoren:** Gekleurde randen in de ticketlijst tonen direct de prioriteit van een ticket.

*   **Workflow Versnellers:**
    *   **Sjablonen (Canned Responses):** Definieer en gebruik voorgedefinieerde antwoorden om repetitieve taken te versnellen en consistentie in communicatie te garanderen.
    *   **Kennisbank-integratie:** Koppel tickets direct aan relevante artikelen in de geïntegreerde Kennisbank voor snelle referentie en oplossing.
    *   **Automatisch Printen:** Nieuw aangemaakte tickets kunnen automatisch naar de standaardprinter worden gestuurd voor fysieke archivering of verwerking.

*   **Betrouwbaarheid & Veiligheid:**
    *   **Beveiligde Authenticatie:** Gebruikt robuuste wachtwoord-hashing (via `scrypt` of `pbkdf2`) en veilig sessiebeheer, wat het onveilig doorgeven van inloggegevens via URL's elimineert en de applicatie beschermt tegen ongeautoriseerde toegang.
    *   **Versleutelde Notities:** Een speciaal veld voor vertrouwelijke informatie (bijv. wachtwoorden, IP-adressen) wordt versleuteld met sterke AES-encryptie, beveiligd door uw hoofdwachtwoord.
    *   **Gedetailleerde Geschiedenis (Audit Trail):** Elke actie en commentaar op een ticket wordt gelogd, wat zorgt voor een complete en transparante tijdlijn van de ticketafhandeling.
    *   **Data Privacy:** Gevoelige notities worden automatisch verborgen wanneer tickets gearchiveerd zijn om privacy te waarborgen.

*   **Inzicht & Rapportage:**
    *   **Visuele Rapporten:** Een intuïtief dashboard toont in één oogopslag heldere grafieken met statistieken over ticketstatussen, prioriteiten, toewijzingen en kennisbankcategorieën, voor betere besluitvorming.

## Technische Hoogtepunten

*   **Zero-Installatie:** De applicatie wordt gebundeld in één enkel `.exe`-bestand met PyInstaller. Dit betekent dat er geen Python-runtime, bibliotheken of database-drivers op de hostcomputer geïnstalleerd hoeven te zijn.
*   **Robuuste Dataopslag:** Maakt gebruik van een lokaal, geïndexeerd SQLite-databasebestand, ontworpen om snel en betrouwbaar te blijven, zelfs met een grote hoeveelheid tickets.
*   **Professionele Architectuur:** De codebase is opgezet met het "Application Factory" patroon en Blueprints van Flask voor maximale modulariteit, onderhoudbaarheid en schaalbaarheid.
*   **Geautomatiseerde Builds (CI/CD):** Een complete CI/CD-pijplijn met GitHub Actions automatiseert het bouwproces en publiceert nieuwe versies, wat zorgt voor consistentie en eenvoudige updates.

## Hoe te Gebruiken

HESK Lite is ontworpen om uiterst gebruiksvriendelijk en foolproof te zijn:

1.  **Download de Applicatie:** Ga naar de [**Releases**](https://github.com/ChaoticML/Hesk-Lite/releases) pagina en download het `.exe`-bestand van de laatste versie.
2.  **Start de Applicatie:** Plaats de `.exe` in een eigen, lege map (bijv. `C:\HESK-Lite`) en start het. De applicatie zal automatisch een `data`-map aanmaken waarin de database wordt opgeslagen.
3.  **Inloggen bij de Applicatie:**
    *   De applicatie opent automatisch in uw standaard webbrowser met een inlogscherm.
    *   **Eerste keer:** Gebruik de standaard gebruikersnaam "admin" (tenzij u deze handmatig in `config/settings.py` heeft gewijzigd). Het wachtwoord is het **hoofdwachtwoord** dat u in de vorige ontwikkelingsstap heeft gehasht. Dit wachtwoord dient tevens als de sleutel voor het versleutelen en ontsleutelen van vertrouwelijke notities. **Het is cruciaal om dit hoofdwachtwoord te onthouden, aangezien versleutelde gegevens zonder dit wachtwoord onherstelbaar zijn!**
    *   **Volgende keren:** Voer uw gebruikersnaam en het eerder ingestelde hoofdwachtwoord in om veilig toegang te krijgen tot de applicatie.
4.  **Gebruik de Interface:** Na succesvol inloggen kunt u de applicatie eenvoudig bedienen via de navigatiebalk en de intuïtieve interface.
5.  **Afsluiten:** Klik op de rode "Afsluiten"-knop in de navigatiebalk om de applicatie veilig en gecontroleerd te stoppen.
6.  **Backup:** Maak regelmatig een kopie van de gehele `data`-map op een veilige locatie om uw ticketgegevens te beschermen.
