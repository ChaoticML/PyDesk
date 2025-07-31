# HESK Lite - Draagbare Helpdesk Applicatie

## Overzicht

**HESK Lite** is een op maat gemaakte, volledig op zichzelf staande en draagbare helpdesk-applicatie, geïnspireerd op de functionaliteit van HESK maar ontworpen voor maximale eenvoud en portabiliteit. vereist geen installatie op een computer, en slaat alle data lokaal op in een beveiligde, versleutelde database.

## Kernfunctionaliteiten

Deze applicatie is gebouwd met een focus op de essentie van een helpdesk-systeem:

*   **Ticket Management:** Maak, bekijk, wijs toe en beheer de volledige levenscyclus van supporttickets (Nieuw, In Behandeling, Opgelost, Gesloten).
*   **Geautomatiseerd Printen:** Bij het aanmaken van een nieuw ticket wordt automatisch een fysieke kopie naar de standaardprinter gestuurd.
*   **Archief:** Gesloten en opgeloste tickets worden automatisch verplaatst naar een overzichtelijk archief met Kritische informatie weggevallen.
*   **Geïntegreerde Kennisbank:** Documenteer oplossingen, handleidingen en veelvoorkomende problemen in een eenvoudig te beheren kennisbank, gecategoriseerd voor snel terugvinden.
*   **Visuele Rapporten:** Een dashboard met heldere grafieken en diagrammen toont in één oogopslag statistieken over ticketstatussen, prioriteiten en meer.
*   **Beveiligde Notities:** Een speciaal veld voor vertrouwelijke informatie (zoals wachtwoorden) wordt versleuteld met sterke, industriestandaard AES-encryptie.

## Technische Hoogtepunten & Ontwerpkeuzes

De applicatie is gebouwd met duurzaamheid en prestaties in gedachten:

*   **Volledig Draagbaar:** Gebundeld in één enkel .exe-bestand met PyInstaller.
*   **Zero-Installatie:** Vereist geen installatie van Python, bibliotheken of database-drivers op de hostcomputer.
*   **Robuuste Dataopslag:** Maakt gebruik van een SQLite-database, die zeer betrouwbaar is voor langdurig gebruik. Database-indexes zijn geïmplementeerd om de applicatie snel te houden, zelfs met duizenden tickets.
*   **Veiligheid Eerst:** Gevoelige data wordt versleuteld met een hoofdwachtwoord dat alleen in het geheugen bestaat en **nooit** op de schijf wordt opgeslagen. Dit garandeert dat de data veilig is, zelfs als de USB-stick verloren raakt.
*   **Gebruiksvriendelijke Interface:** Een schone, web-gebaseerde interface (dankzij Flask) die intuïtief en volledig in het Nederlands is. Inclusief directe feedback via flash-berichten en een gecontroleerde "Afsluiten"-knop.

## Hoe te Gebruiken (Workflow)

De applicatie is ontworpen om foolproof te zijn:

1.  **Start de Applicatie:** Due the run.py en het bat bestand op een usb. of run het locaal op je computer met windows 10 of 11
2.  **Ontgrendel de Database:**
    *   **Eerste keer:** Voer uw naam in en kies een sterk **hoofdwachtwoord**. Dit wachtwoord moet u voortaan altijd gebruiken. **Vergeet dit wachtwoord niet, want het is onherstelbaar!**
    *   **Volgende keren:** Voer uw naam en het ingestelde hoofdwachtwoord in om toegang te krijgen.
3.  **Navigeer:** Gebruik de navigatiebalk bovenaan om tickets te beheren, de kennisbank te raadplegen of rapporten te bekijken.
4.  **Afsluiten:** Klik op de rode "Afsluiten"-knop in de navigatiebalk om de applicatie veilig te stoppen.
5.  **Backup:** Kopieer periodiek de gehele `HelpDesk`-map van de USB-stick naar een veilige locatie als backup.

Dit project demonstreert hoe moderne tools kunnen worden ingezet om een krachtige, op maat gemaakte en veilige oplossing te bouwen die perfect is afgestemd op specifieke workflow-eisen.
