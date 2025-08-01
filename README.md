# HESK Lite - Standalone Helpdesk Applicatie

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python)
![Flask](https://img.shields.io/badge/Flask-2.0-000000?logo=flask)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite)
![Status](https://img.shields.io/badge/Status-Actieve%20Ontwikkeling-blue)

## Overzicht

**HESK Lite** is een op maat gemaakte, volledig op zichzelf staande helpdesk-applicatie. Geïnspireerd op de functionaliteit van HESK, is dit project ontworpen als een lichtgewicht, betrouwbaar en foolproof alternatief, specifiek gebouwd voor een gestroomlijnde workflow.

De applicatie draait als één enkel `.exe`-bestand op Windows, vereist geen installatie van externe software of databases, en slaat alle data lokaal op in een beveiligde, versleutelde database.

## Kernfunctionaliteiten

Deze applicatie is gebouwd met een focus op de essentie van een modern helpdesk-systeem:

*   **Ticket Management:**
    *   Volledige levenscyclus van tickets: aanmaken, bekijken, toewijzen en beheren (Nieuw, In Behandeling, Opgelost, Gesloten).
    *   **Geavanceerd Overzicht:** Zoek, filter (op toewijzing) en sorteer (op datum, prioriteit, status) door alle tickets.
    *   **Visuele Indicatoren:** Gekleurde randen geven de prioriteit van een ticket direct weer in de lijst.

*   **Workflow Versnellers:**
    *   **Sjablonen (Canned Responses):** Definieer en gebruik voorgedefinieerde antwoorden om repetitieve taken te versnellen en consistentie te garanderen.
    *   **Kennisbank-integratie:** Koppel tickets direct aan oplossingen in de geïntegreerde Kennisbank voor snelle referentie.
    *   **Automatisch Printen:** Nieuw aangemaakte tickets worden automatisch naar de standaardprinter gestuurd.

*   **Betrouwbaarheid & Veiligheid:**
    *   **Gedetailleerde Geschiedenis (Audit Trail):** Elke actie op een ticket wordt gelogd, wat zorgt voor een complete en transparante tijdlijn.
    *   **Versleutelde Notities:** Een speciaal veld voor vertrouwelijke informatie wordt versleuteld met sterke AES-encryptie, beveiligd door een hoofdwachtwoord.
    *   **Data Veiligheid:** Gevoelige informatie wordt automatisch verborgen in gearchiveerde tickets.

*   **Inzicht & Rapportage:**
    *   **Visuele Rapporten:** Een dashboard met heldere grafieken toont in één oogopslag statistieken over ticketstatussen, prioriteiten en meer.

## Technische Hoogtepunten

*   **Zero-Installatie:** Gebundeld in één enkel `.exe`-bestand met PyInstaller. Vereist geen installatie van Python, bibliotheken of database-drivers op de hostcomputer.
*   **Robuuste Dataopslag:** Maakt gebruik van een geïndexeerde SQLite-database, ontworpen om snel en betrouwbaar te blijven, zelfs met duizenden tickets.
*   **Professionele Architectuur:** Opgezet met de "Application Factory" structuur en Blueprints voor maximale onderhoudbaarheid en schaalbaarheid.
*   **Geautomatiseerde Builds (CI/CD):** Een volledige CI/CD-pijplijn met GitHub Actions bouwt en publiceert automatisch nieuwe versies.

## Hoe te Gebruiken

De applicatie is ontworpen om foolproof te zijn:

1.  **Download de Applicatie:** Ga naar de [**Releases**](https://github.com/ChaoticML/Hesk-Lite/releases) pagina en download het `.exe`-bestand van de laatste versie.
2.  **Start de Applicatie:** Plaats de `.exe` in een eigen map (bijv. `C:\HESK-Lite`) en start het. De applicatie zal automatisch een `data`-map aanmaken voor de database.
3.  **Ontgrendel de Database:**
    *   **Eerste keer:** Voer uw naam in en kies een sterk **hoofdwachtwoord**. Dit wachtwoord is essentieel. **Vergeet dit wachtwoord niet, want het is onherstelbaar!**
    *   **Volgende keren:** Voer uw naam en het ingestelde hoofdwachtwoord in om toegang te krijgen.
4.  **Gebruik de Interface:** De applicatie opent in uw webbrowser. Gebruik de navigatiebalk om alle functies te gebruiken.
5.  **Afsluiten:** Klik op de rode "Afsluiten"-knop in de navigatiebalk om de applicatie veilig te stoppen.
6.  **Backup:** Maak regelmatig een kopie van de `data`-map op een veilige locatie.
