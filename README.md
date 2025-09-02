# PyDesk - Standalone Helpdesk Applicatie

[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/ChaoticML/PyDesk/development-build.yml?branch=main)](https://github.com/ChaoticML/PyDesk/actions)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/ChaoticML/PyDesk)](https://github.com/ChaoticML/PyDesk/releases)
[![GitHub last commit](https://img.shields.io/github/last-commit/ChaoticML/PyDesk)](https://github.com/ChaoticML/PyDesk/commits/main)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.1-000000?logo=flask)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

**PyDesk** is een op maat gemaakte, volledig op zichzelf staande en veilige helpdesk-applicatie. Dit project is ontworpen als een lichtgewicht, betrouwbaar en foolproof alternatief voor complexere systemen, specifiek gebouwd voor een gestroomlijnde, Nederlandstalige workflow.

---

## Inhoudsopgave

1.  [**Principes**](#-principes)
2.  [**Features**](#-features)
3.  [**Aan de Slag (Installatie)**](#-aan-de-slag-installatie)
4.  [**Technische Hoogtepunten**](#-technische-hoogtepunten)
5.  [**Bijdragen**](#-bijdragen)
6.  [**Licentie**](#-licentie)

---

## 🚀 Principes

Dit project is gebouwd met drie kernprincipes in gedachten:

-   ✅ **Lichtgewicht & Foolproof:** De applicatie moet eenvoudig te begrijpen, snel en betrouwbaar zijn, zonder onnodige complexiteit of externe afhankelijkheden.
-   🔒 **Veiligheid Eerst:** Alle data, met name gevoelige informatie, wordt lokaal opgeslagen en beschermd met moderne, robuuste beveiligingspraktijken.
-   🔧 **Modulair & Onderhoudbaar:** De codebase is schoon, goed gedocumenteerd en gestructureerd op een manier die toekomstige uitbreidingen en onderhoud eenvoudig maakt.

---

## ✨ Features

*   **🎫 Ticket Management:**
    *   Beheer de volledige levenscyclus van tickets: aanmaken, bekijken, toewijzen en bijwerken.
    *   **Geavanceerd Overzicht:** Zoek, filter en sorteer moeiteloos door alle actieve en gearchiveerde tickets.
    *   **Visuele Indicatoren:** Gekleurde randen tonen direct de prioriteit van een ticket.

*   **⚡ Workflow Versnellers:**
    *   **Sjablonen (Canned Responses):** Definieer en gebruik voorgedefinieerde antwoorden om de communicatie te versnellen.
    *   **Kennisbank-integratie:** Koppel tickets direct aan relevante artikelen en render de inhoud met volledige **Markdown-ondersteuning** voor rijke opmaak.
    *   **Automatisch Printen:** Nieuwe tickets kunnen automatisch naar de standaardprinter worden gestuurd.

*   **🛡️ Betrouwbaarheid & Veiligheid:**
    *   **Beveiligde Authenticatie:** Maakt gebruik van wachtwoord-hashing (scrypt) en veilig sessiebeheer.
    *   **Versleutelde Notities:** Gevoelige informatie wordt versleuteld met sterke AES-encryptie.
    *   **Gedetailleerde Geschiedenis (Audit Trail):** Elke actie op een ticket wordt gelogd voor volledige transparantie.

*   **📊 Inzicht & Rapportage:**
    *   Een dashboard met heldere grafieken toont statistieken over ticketstatussen, prioriteiten en meer.

*   **🎨 Moderne UI/UX:**
    *   Een volledig opnieuw ontworpen, consistente en intuïtieve gebruikersinterface.
    *   Duidelijke "empty states" die u begeleiden wanneer er nog geen data is.

---

## 🛠️ Aan de Slag (Installatie)

Voor maximale veiligheid wordt **PyDesk** momenteel gedistribueerd als broncode. U dient de applicatie zelf te bouwen om uw eigen unieke en veilige hoofdwachtwoord in te stellen.

Gedetailleerde, stap-voor-stap instructies vindt u op onze **[Wiki: Zelf Bouwen](https://github.com/ChaoticML/PyDesk/wiki/Zelf-Bouwen)**.

Het proces omvat in het kort:
1.  De repository klonen.
2.  De afhankelijkheden installeren met `uv` (een snellere Python package manager. Installeer met `pip install uv`).
3.  Uw eigen, unieke wachtwoord-hash genereren.
4.  Het `.exe`-bestand bouwen met PyInstaller.

---

## 💡 Technische Hoogtepunten

*   **Zero-Installatie:** Gebundeld in één enkel `.exe`-bestand met PyInstaller.
*   **Robuuste Dataopslag:** Maakt gebruik van een lokaal, geïndexeerd SQLite-databasebestand.
*   **Professionele Architectuur:** Opgezet met het "Application Factory" patroon en Blueprints van Flask.
*   **Beveiliging:** Gebruikt scrypt voor wachtwoord hashing en AES voor data encryptie.
*   **Geautomatiseerde Builds (CI/CD):** Een CI/CD-pijplijn met GitHub Actions bouwt en publiceert automatisch nieuwe releases.

---

## 🙌 Bijdragen

Pull Requests zijn welkom! Fork de repo, maak een feature branch aan, en dien een PR in met een duidelijke beschrijving van je wijzigingen. Voor grote veranderingen, open eerst een issue om te bespreken wat je zou willen veranderen.

---

## 📜 Licentie

Dit project is gelicenseerd onder de MIT Licentie - zie het [LICENSE](LICENSE) bestand voor details.
