# HESK Lite - Standalone Helpdesk Applicatie

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python)![Flask](https://img.shields.io/badge/Flask-3.1-000000?logo=flask)![License](https://img.shields.io/badge/License-MIT-yellow.svg)![Status](https://img.shields.io/badge/Status-Actieve%20Ontwikkeling-blue)

**HESK Lite** is een op maat gemaakte, volledig op zichzelf staande en veilige helpdesk-applicatie. Dit project is ontworpen als een lichtgewicht, betrouwbaar en foolproof alternatief voor complexere systemen, specifiek gebouwd voor een gestroomlijnde, Nederlandstalige workflow.

---

## Inhoudsopgave
*   [Overzicht](#overzicht)
*   [Features](#features)
*   [Technische Hoogtepunten](#technische-hoogtepunten)
*   [Hoe te Gebruiken](#hoe-te-gebruiken)
*   [Licentie](#licentie)

---

## Overzicht

De applicatie draait als één enkel `.exe`-bestand op Windows, vereist geen installatie van externe software of databases, en slaat alle data lokaal op in een beveiligde database. De focus ligt op eenvoud, snelheid en veiligheid.

## Features

*   **Ticket Management:**
    *   Beheer de volledige levenscyclus van tickets: aanmaken, bekijken, toewijzen en bijwerken.
    *   **Geavanceerd Overzicht:** Zoek, filter en sorteer moeiteloos door alle actieve en gearchiveerde tickets.
    *   **Visuele Indicatoren:** Gekleurde randen tonen direct de prioriteit van een ticket.

*   **Workflow Versnellers:**
    *   **Sjablonen (Canned Responses):** Definieer en gebruik voorgedefinieerde antwoorden om de communicatie te versnellen.
    *   **Kennisbank-integratie:** Koppel tickets direct aan relevante artikelen en render de inhoud met **Markdown-ondersteuning** voor rijke opmaak.
    *   **Automatisch Printen:** Nieuwe tickets kunnen automatisch naar de standaardprinter worden gestuurd.

*   **Betrouwbaarheid & Veiligheid:**
    *   **Beveiligde Authenticatie:** Maakt gebruik van wachtwoord-hashing (`scrypt`) en veilig sessiebeheer.
    *   **Versleutelde Notities:** Gevoelige informatie wordt versleuteld met sterke AES-encryptie, beveiligd door uw hoofdwachtwoord.
    *   **Gedetailleerde Geschiedenis (Audit Trail):** Elke actie op een ticket wordt gelogd voor volledige transparantie.

*   **Inzicht & Rapportage:**
    *   **Visuele Rapporten:** Een dashboard met heldere grafieken toont statistieken over ticketstatussen, prioriteiten en meer.

*   **Moderne UI/UX:**
    *   Een volledig opnieuw ontworpen, consistente en intuïtieve gebruikersinterface.
    *   Duidelijke "empty states" die u begeleiden wanneer er nog geen data is.

## Technische Hoogtepunten

*   **Zero-Installatie:** Gebundeld in één enkel `.exe`-bestand met PyInstaller.
*   **Robuuste Dataopslag:** Maakt gebruik van een lokaal, geïndexeerd SQLite-databasebestand.
*   **Professionele Architectuur:** Opgezet met het "Application Factory" patroon en Blueprints van Flask.
*   **Geautomatiseerde Builds (CI/CD):** Een CI/CD-pijplijn met GitHub Actions bouwt en publiceert automatisch nieuwe releases.

## Hoe te Gebruiken

Voor maximale veiligheid wordt HESK Lite momenteel gedistribueerd als broncode. U dient de applicatie zelf te bouwen om uw eigen unieke en veilige hoofdwachtwoord in te stellen.

Gedetailleerde, stap-voor-stap instructies vindt u op onze **[Wiki: Zelf Bouwen](https://github.com/ChaoticML/Hesk-Lite/wiki/Zelf-Bouwen)**.

Het proces omvat in het kort:
1.  De repository klonen.
2.  De afhankelijkheden installeren.
3.  Uw eigen wachtwoord-hash genereren.
4.  Het `.exe`-bestand bouwen met PyInstaller.

## Licentie

Dit project is gelicenseerd onder de **MIT Licentie**. Zie het `LICENSE` bestand voor meer details.
