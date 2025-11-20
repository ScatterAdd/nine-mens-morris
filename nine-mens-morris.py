"""
Nine Men's Morris Game

Copyright (C) 2025 Uwe Kletscher (ScatterAdd)
This project is licensed under the GNU General Public License Version 3 (GPL-3.0).
You are allowed to use, modify, and distribute this project,
provided that all modified versions are also released under the GPL-3.0 license.

See LICENSE for the full license text.
"""

import warnings
warnings.filterwarnings("ignore", message="pkg_resources is deprecated")
import pygame
import sys
import random
import socket
import select
import math

# constant / Konstanten
# just in case 600x600 is too small, can be switched to 800x800.
# layout remains stable
# wenn 600, 600 zu klein, kann auf 800, 800 umgestellt werden. 
# layout bleibt stabil
WIDTH, HEIGHT = 600, 600
FPS = 60
FONT_SIZE = 40
MENU_OPTIONS = ["Mensch vs SL", "Netzwerkspiel", "Hilfe"]
DIFFICULTY_OPTIONS = ["Leicht", "Mittel", "Schwer"]
RULESET_OPTIONS = ["Entschärft", "Turnier"]

# Network defaults and menu dice herlper / 
# Netzwerk-Defaults und Menü-/Würfel-Helfer
DEFAULT_IP = "127.0.0.1"
DEFAULT_PORT = 50007

# Runtime language switching default de / 
# Laufzeit-Sprachumschaltung (de/en/fr/es)
CURRENT_LANG = "de"  # current language / Startsprache
LANG_ORDER = ["de", "en", "fr", "es"]

# debug overlay global toggle (key 'D') / 
# Debug-Overlay global toggeln (Taste 'D')
DEBUG_OVERLAY = False

def toggle_debug_overlay():
    global DEBUG_OVERLAY
    DEBUG_OVERLAY = not DEBUG_OVERLAY

def draw_debug_overlay(screen, lines, *, pos=(8, 8)):
    try:
        if not DEBUG_OVERLAY:
            return
        # Semi transparent background / 
        # Semi-transparenter Hintergrund
        bg = pygame.Surface((min(420, WIDTH-16), min(220, HEIGHT-16)), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 120))
        screen.blit(bg, pos)
        # Small font / 
        # Kleine Schrift
        f = pygame.font.SysFont("FreeMono", 14)
        y = pos[1] + 6
        x = pos[0] + 8
        for line in lines[:12]:
            try:
                surf = f.render(str(line), True, (220, 220, 180))
                screen.blit(surf, (x, y))
                y += surf.get_height() + 2
            except Exception:
                pass
    except Exception:
        pass

def toggle_language():
    """Wechselt die Sprache zyklisch durch LANG_ORDER."""
    global CURRENT_LANG
    try:
        i = LANG_ORDER.index(CURRENT_LANG)
    except ValueError:
        i = 0
    CURRENT_LANG = LANG_ORDER[(i + 1) % len(LANG_ORDER)]

def get_menu_options():
    # Base (german) as key;
    # displayed in render_fit_text->tr translation
    # Basis (Deutsch) als Schlüssel; 
    # Anzeige wird in render_fit_text->tr übersetzt
    lang_names = {"de": "Deutsch", "en": "English", "fr": "Français", "es": "Español"}
    cur = lang_names.get(CURRENT_LANG, CURRENT_LANG)
    return [
        "Mensch vs SL",
        "Netzwerkspiel",  # standardized without space to get translation
                          # vereinheitlicht ohne Leerzeichen, damit Übersetzung greift
        f"Sprache: {cur} (L)",
        "Hilfe",
    ]

# Translation strukture: list of (german string, translated string) / 
# Übersetzungen nachfolgender Struktur: Liste von (deutscher String, übersetzter String)
SUBS_EN = [
    # Spezified phrases first we sort later according to length/ 
    # Spezifische Phrasen zuerst (wir sortieren später zusätzlich nach Länge)
    ("Mühle! Wähle einen gegnerischen Stein zum Entfernen.", "Mill! Choose an opponent stone to remove."),
    ("Mühle! Entferne gegnerischen Stein.", "Mill! Remove an opponent stone."),
    ("Mühle", "Nine Men's Morris"),
    ("Mensch vs SL", "Human vs SL"),
    ("Netzwerkspiel", "Network Game"),
    ("Hilfe", "Help"),
    ("Hilfe / Steuerung", "Help / Controls"),
    ("Sprache", "Language"),
    ("Deutsch", "German"),
    ("English", "English"),
    ("Spiel wirklich beenden?", "Really quit the game?"),
    ("J/Enter = Ja,  N/ESC = Nein", "Y/Enter = Yes,  N/ESC = No"),
    ("Würfeln: Wer beginnt? Drücke SPACE!", "Roll: Who starts? Press SPACE!"),
    ("Spieler würfelt: ", "Player rolls: "),
    ("SL würfelt: ", "SL rolls: "),
    ("beginnt und spielt mit Weiß!", "starts and plays White!"),
    ("Drücke SPACE für das Spielfeld...", "Press SPACE to continue..."),
    ("setzt Stein ", "places stone "),
    ("Zugphase: ", "Move phase: "),
    ("ist am Zug", "to move"),
    ("hat eine Mühle gebildet! Wähle einen gegnerischen Stein.", "formed a mill! Choose an opponent stone."),
    ("hat eine Mühle gebildet! Gegnerischer Stein wird entfernt.", "formed a mill! Opponent stone will be removed."),
    ("Mühle! Wähle einen gegnerischen Stein zum Entfernen.", "Mill! Choose an opponent stone to remove."),
    ("Spielende!", "Game over!"),
    ("gewinnt!", "wins!"),
    ("(ESC für Menü)", "(ESC to menu)"),
    ("Remis nach Turnierregeln", "Draw by tournament rules"),
    ("Menü Navigation:", "Menu navigation:"),
    ("Auswahl wechseln", "Change selection"),
    ("Enter / Leertaste", "Enter / Space"),
    ("Auswahl bestätigen", "Confirm selection"),
    ("Zurück / Abbrechen", "Back / Cancel"),
    ("Maus: Klick auf Menüoption wählt diese aus", "Mouse: Click on option to select it"),
    ("Im Spiel:", "In game:"),
    ("Spiel abbrechen / zurück zum Menü", "Abort / back to menu"),
    ("Maus: Steine setzen und ziehen", "Mouse: Place and move stones"),
    ("SPACE : Würfeln und fortfahren (wo angezeigt)", "SPACE: Roll and continue (where shown)"),
    ("Netzwerk-Menü:", "Network menu:"),
    ("Host/Client/IP/Port/Bind auswählbar mit ↑/↓ und Enter", "Host/Client/IP/Port/Bind selectable with ↑/↓ and Enter"),
    ("IP/Port kann per Dialog geändert werden", "IP/Port can be changed via dialog"),
    ("Verbinden startet das Netzwerkspiel", "Connect starts the network game"),
    ("Regelsets:", "Rule sets:"),
    ("Entschärft:", "Relaxed:"),
    ("Klassische Regeln ohne zusätzliche Remis-/Sperrlogik", "Classic rules without extra draw/anti-repeat logic"),
    ("Kein Anti-Pendeln, keine 3-fach-Wiederholung,", "No anti-pendulum, no threefold repetition,"),
    ("kein 100-Halbzüge-Remis", "no 100-half-move draw"),
    ("Turnier:", "Tournament:"),
    ("Anti-Pendeln: Sofortiges Zurückziehen desselben", "Anti-pendulum: immediate back-and-forth move"),
    ("Steins ist verboten", "with the same stone is forbidden"),
    ("3-fach-Wiederholung derselben Stellung (mit gleichem", "Threefold repetition of the same position (with same"),
    ("Zugrecht) = Remis", "side to move) = draw"),
    ("100 Halbzüge ohne Schlagfall = Remis", "100 half-moves without capture = draw"),
    ("Drücke ESC um Zurückkehren", "Press ESC to go back"),
    ("Keine legalen Züge", "No legal moves"),
    ("Weiß", "White"),
    ("Schwarz", "Black"),
    ("Mensch", "Human"),
    ("Spieler", "Player"),
    ("SL", "SL"),
    ("Rep:", "Rep:"),
    ("HZ:", "HM:"),
    # selection dialogue / Auswahl-Dialoge
    ("Spielstärke wählen", "Choose difficulty"),
    ("Regelset wählen", "Choose ruleset"),
    ("Leicht", "Easy"),
    ("Mittel", "Medium"),
    ("Schwer", "Hard"),
    ("Entschärft", "Relaxed"),
    ("Turnier", "Tournament"),
    ("↑/↓ wählen, Enter bestätigen, ESC abbrechen", "↑/↓ to choose, Enter to confirm, ESC to cancel"),
    # networkstub / Netzwerkstub
    ("Netzwerkspiel kommt später.", "Network game coming soon."),
    ("Network Game wirklich beenden?", "Really quit the network game?"),
    # network UI / Netzwerk-UI
    ("Netzwerkspiel", "Network Game"),
    ("Netzwerkspiel wirklich beenden?", "Really quit the network game?"),
    ("Verbindung fehlgeschlagen", "Connection failed"),
    ("Warte auf Client", "Waiting for client"),
    ("Verbunden – warte auf Start", "Connected – waiting to start"),
    ("ESC zum Abbrechen", "ESC to cancel"),
    ("Netzwerk-Würfeln", "Network dice roll"),
    ("Würfelergebnis", "Dice result"),
    ("Host beginnt – Spieler 1 (Weiß)", "Host starts – Player 1 (White)"),
    ("Client beginnt – Spieler 1 (Weiß)", "Client starts – Player 1 (White)"),
    ("Host beginnt - Spieler 1 (Weiß)", "Host starts - Player 1 (White)"),
    ("Client beginnt - Spieler 1 (Weiß)", "Client starts - Player 1 (White)"),
    ("Spieler 1 (Weiß): Host", "Player 1 (White): Host"),
    ("Spieler 2 (Schwarz): Client", "Player 2 (Black): Client"),
    ("Spieler 1 (Weiß): Client", "Player 1 (White): Client"),
    ("Spieler 2 (Schwarz): Host", "Player 2 (Black): Host"),
    ("Spieler 1 (Weiß)", "Player 1 (White)"),
    ("Spieler 2 (Schwarz)", "Player 2 (Black)"),
    ("Spieler 1", "Player 1"),
    ("Spieler 2", "Player 2"),
    ("Du bist Spieler 1 (Weiß)", "You're Player 1 (White)"),
    ("Du bist Spieler 2 (Schwarz)", "You're Player 2 (Black)"),
    ("Drücke SPACE, um zu starten...", "Press SPACE to start..."),
    ("hat die Verbindung beendet.", "has left the connection."),
    ("Gegner entfernt einen Stein...", "Opponent removes a stone..."),
    ("Gegner", "Opponent"),
    (" (DU)", " (You)"),
    (" (Du)", " (You)"),
    ("Bind: Lokal", "Bind: Local"),
    ("Bind: LAN", "Bind: LAN"),
    ("Verbinden", "Connect"),
    ("Enter=OK, ESC=Abbrechen", "Enter=OK, ESC=Cancel"),
    ("Setzphase: Klicke auf einen freien Punkt", "Placement: Click on a free point"),
    ("Anti-Pendeln: mit demselben Stein sofort zurück ist verboten", "Anti-pendulum: immediate back with the same stone is forbidden"),
    # phases/action phrases / Phasen/Aktionsphrasen
    ("Setzphase:", "placing phase:"),
    ("Zugphase:", "move phase:"),
    ("setzt Stein ", "place a stone "),
    ("bewegt einen Stein", "move a stone"),
    ("entfernt einen Stein", "remove a stone"),
    # interim result/match end / Zwischenstand/Match-Ende
    ("Zwischenstand:", "Score:"),
    ("Spiel ", "Game "),
    ("Drücke SPACE für das nächste Spiel...", "Press SPACE for the next game..."),
    ("Drücke ESC für das Menü...", "Press ESC to menu..."),
    ("gewinnt das Match!", "wins the match!"),
    ("verliert das Match", "loses the match"),
    ("Unentschieden im Match!", "Draw in match!"),
    # menu/match selection / Menü/Match-Auswahl
    ("Auswahl", "Selection"),
    ("Einzelpartie", "Single game"),
    ("Match (Best of 3)", "Match (Best of 3)"),
    ("↑/↓ wählen, Enter bestätigen, ESC zurück", "↑/↓ to choose, Enter to confirm, ESC back"),
]

# french translations (important menu and game phrases) /
# französische Übersetzungen (wichtige Menü- und Spielphrasen)
SUBS_FR = [
    ("Mühle! Wähle einen gegnerischen Stein zum Entfernen.", "Moulin ! Choisissez une pierre adverse."),
    ("Mühle! Entferne gegnerischen Stein.", "Moulin ! Retirez une pierre adverse."),
    ("Mühle", "Jeu de moulin"),
    ("Mensch vs SL", "Humain vs SL"),
    ("Netzwerkspiel", "Jeu réseau"),
    ("Hilfe", "Aide"),
    ("Sprache", "Langue"),
    ("Mensch", "Humain"),
    ("Spielstärke wählen", "Choisir la difficulté"),
    ("Regelset wählen", "Choisir le jeu de règles"),
    ("Leicht", "Facile"),
    ("Mittel", "Moyen"),
    ("Schwer", "Difficile"),
    ("Entschärft", "Allégé"),
    ("Turnier", "Tournoi"),
    ("↑/↓ wählen, Enter bestätigen, ESC abbrechen", "↑/↓ choisir, Entrée valider, ESC annuler"),
    ("Spiel wirklich beenden?", "Quitter la partie ?"),
    ("Würfeln: Wer beginnt? Drücke SPACE!", "Dé lancer : qui commence ? Espace !"),
    ("Spieler würfelt: ", "Joueur lance : "),
    ("SL würfelt: ", "SL lance : "),
    ("beginnt und spielt mit Weiß!", "commence et joue avec les blancs !"),
    ("Drücke SPACE für das Spielfeld...", "Appuyez ESPACE pour le plateau..."),
    ("Setzphase:", "Phase de pose :"),
    ("Zugphase:", "Phase de déplacement :"),
    ("setzt Stein ", "pose une pierre "),
    ("bewegt einen Stein", "déplace une pierre"),
    ("entfernt einen Stein", "retire une pierre"),
    ("Spielende!", "Fin de partie !"),
    ("gewinnt!", "gagne !"),
    ("Remis nach Turnierregeln", "Nulle selon les règles tournoi"),
    ("Weiß", "Blanc"),
    ("Schwarz", "Noir"),
    ("Hilfe / Steuerung", "Aide / Commandes"),
]

# spanish translations (important menu and game phrases) /
# spanische Übersetzungen (wichtige Menü- und Spielphrasen)
SUBS_ES = [
    ("Mühle! Wähle einen gegnerischen Stein zum Entfernen.", "Molino! Elige una ficha enemiga."),
    ("Mühle! Entferne gegnerischen Stein.", "¡Molino! Quita una ficha enemiga."),
    ("Mühle", "Juego del molino"),
    ("Mensch vs SL", "Humano vs SL"),
    ("Netzwerkspiel", "Juego en red"),
    ("Hilfe", "Ayuda"),
    ("Sprache", "Idioma"),
    ("Mensch", "Humano"),
    ("Spielstärke wählen", "Elegir dificultad"),
    ("Regelset wählen", "Elegir reglas"),
    ("Leicht", "Fácil"),
    ("Mittel", "Medio"),
    ("Schwer", "Difícil"),
    ("Entschärft", "Suavizado"),
    ("Turnier", "Torneo"),
    ("↑/↓ wählen, Enter bestätigen, ESC abbrechen", "↑/↓ elegir, Enter confirmar, ESC cancelar"),
    ("Spiel wirklich beenden?", "¿Realmente salir del juego?"),
    ("Würfeln: Wer beginnt? Drücke SPACE!", "Tirar: ¿Quién empieza? Pulsa ESPACIO!"),
    ("Spieler würfelt: ", "Jugador tira: "),
    ("SL würfelt: ", "SL tira: "),
    ("beginnt und spielt mit Weiß!", "empieza y juega con blancas!"),
    ("Drücke SPACE für das Spielfeld...", "Pulsa ESPACIO para el tablero..."),
    ("Setzphase:", "Fase de colocación:"),
    ("Zugphase:", "Fase de movimiento:"),
    ("setzt Stein ", "coloca una ficha "),
    ("bewegt einen Stein", "mueve una ficha"),
    ("entfernt einen Stein", "retira una ficha"),
    ("Spielende!", "¡Fin de la partida!"),
    ("gewinnt!", "gana!"),
    ("Remis nach Turnierregeln", "Tablas según reglas de torneo"),
    ("Weiß", "Blancas"),
    ("Schwarz", "Negras"),
    ("Hilfe / Steuerung", "Ayuda / Controles"),
]

# add missing french translations (fallback: english phrase) /
# Ergänze fehlende FR-Übersetzungen (Fallback: englische Phrase)
SUBS_FR += [
    ("Deutsch", "German"),
    ("English", "English"),
    ("J/Enter = Ja,  N/ESC = Nein", "Y/Entrée = Oui, N/ESC = Non"),
    ("Zugphase: ", "phase de traction: "),
    ("ist am Zug", "est au tour"),
    ("hat eine Mühle gebildet! Wähle einen gegnerischen Stein.", "a formé un moulin ! Choisis une pierre adverse"),
    ("hat eine Mühle gebildet! Gegnerischer Stein wird entfernt.", "a formé un moulin ! La pierre adverse est retirée."),
    ("(ESC für Menü)", "(ESC au menu)"),
    ("Menü Navigation:", "navigation dans le menu:"),
    ("Auswahl wechseln", "Changer de sélection"),
    ("Enter / Leertaste", "Entrée / Espace"),
    ("Auswahl bestätigen", "Confirmer la sélection"),
    ("Zurück / Abbrechen", "Retour / Annuler"),
    ("Maus: Klick auf Menüoption wählt diese aus", "Mouse: Cliquez on option pour select it"),
    ("Im Spiel:", "Dans le jeu:"),
    ("Spiel abbrechen / zurück zum Menü", "Abort / Retour au menu"),
    ("Maus: Steine setzen und ziehen", "Mouse: Place and move spournes"),
    ("SPACE : Würfeln und fortfahren (wo angezeigt)", "SPACE : Lancer les dés et continuer (le cas échéant)"),
    ("Netzwerk-Menü:", "Menu réseau:"),
    ("Host/Client/IP/Port/Bind auswählbar mit ↑/↓ und Enter", "Hôte/client/IP/port/liaison sélectionnables avec ↑/↓ et Entrée."),
    ("IP/Port kann per Dialog geändert werden", "IP/Port peuvent être modifiés via la boîte de dialogue."),
    ("Verbinden startet das Netzwerkspiel", "Connecter lance le jeu en réseau"),
    ("Regelsets:", "ensembles de règles:"),
    ("Entschärft:", "Désamorcé:"),
    ("Klassische Regeln ohne zusätzliche Remis-/Sperrlogik", "Règles classiques sans logique supplémentaire de blocage/match nul."),
    ("Kein Anti-Pendeln, keine 3-fach-Wiederholung,", "Pas d'anti-oscillation, pas de répétition triple,"),
    ("kein 100-Halbzüge-Remis", "pas de match nul en 100 demi-coups"),
    ("Turnier:", "Tournoi:"),
    ("Anti-Pendeln: Sofortiges Zurückziehen desselben", "Anti-oscillation : retrait immédiat de celui-ci"),
    ("Steins ist verboten", "avec la même épée est interdit"),
    ("3-fach-Wiederholung derselben Stellung (mit gleichem", "Répétition 3 fois de la même position (avec le même"),
    ("Zugrecht) = Remis", "Égalité) = match nul"),
    ("100 Halbzüge ohne Schlagfall = Remis", "100 demi-coups sans coup = match nul"),
    ("Drücke ESC um Zurückkehren", "Appuyez ESC pour revenir"),
    ("Keine legalen Züge", "Pas de coups légaux"),
    ("Spieler", "Joueur"),
    ("SL", "SL"),
    ("Rep:", "Rep:"),
    ("HZ:", "HM:"),
    ("Netzwerkspiel kommt später.", "Le jeu en réseau sera disponible ultérieurement."),
    ("Network Game wirklich beenden?", "Vraiment quitter le jeu en réseau?"),
    ("Netzwerkspiel wirklich beenden?", "Vraiment quitter le jeu en réseau?"),
    ("Verbindung fehlgeschlagen", "Connexion échouée"),
    ("Warte auf Client", "En attente for client"),
    ("Verbunden – warte auf Start", "Connecté – en attente de démarrage"),
    ("ESC zum Abbrechen", "ESC pour annuler"),
    ("Netzwerk-Würfeln", "Réseau dice roll"),
    ("Würfelergebnis", "résultat du lancer de dés"),
    ("Host beginnt – Spieler 1 (Weiß)", "Host démarrers – Joueur 1 (Blanc)"),
    ("Client beginnt – Spieler 1 (Weiß)", "Client démarrers – Joueur 1 (Blanc)"),
    ("Host beginnt - Spieler 1 (Weiß)", "Host démarrers - Joueur 1 (Blanc)"),
    ("Client beginnt - Spieler 1 (Weiß)", "Client démarrers - Joueur 1 (Blanc)"),
    ("Spieler 1 (Weiß): Host", "Joueur 1 (Blanc): Host"),
    ("Spieler 2 (Schwarz): Client", "Joueur 2 (Noir): Client"),
    ("Spieler 1 (Weiß): Client", "Joueur 1 (Blanc): Client"),
    ("Spieler 2 (Schwarz): Host", "Joueur 2 (Noir): Host"),
    ("Spieler 1 (Weiß)", "Joueur 1 (Blanc)"),
    ("Spieler 2 (Schwarz)", "Joueur 2 (Noir)"),
    ("Spieler 1", "Joueur 1"),
    ("Spieler 2", "Joueur 2"),
    ("Du bist Spieler 1 (Weiß)", "Vous êtes Joueur 1 (Blanc)"),
    ("Du bist Spieler 2 (Schwarz)", "Vous êtes Joueur 2 (Noir)"),
    ("Drücke SPACE, um zu starten...", "Appuyez ESPACE pour démarrer..."),
    ("hat die Verbindung beendet.", "a mis fin à la connexion."),
    ("Gegner entfernt einen Stein...", "Adversaire removes a spourne..."),
    ("Gegner", "Adversaire"),
    (" (DU)", " (Tu)"),
    (" (Du)", " (Tu)"),
    ("Bind: Lokal", "Lier Localement"),
    ("Bind: LAN", "Lier: Réseau"),
    ("Verbinden", "Connecter"),
    ("Enter=OK, ESC=Abbrechen", "Entrée=OK, ESC=Annuler"),
    ("Setzphase: Klicke auf einen freien Punkt", "Placement : cliquez sur un point libre"),
    ("Anti-Pendeln: mit demselben Stein sofort zurück ist verboten", "Anti-pendule : il est interdit de revenir immédiatement avec la même pierre."),
    ("Zwischenstand:", "résultat intermédiaire:"),
    ("Spiel ", "Partie "),
    ("Drücke SPACE für das nächste Spiel...", "Appuie sur ESPACE pour passer au jeu suivant..."),
    ("Drücke ESC für das Menü...", "Appuyez ESC au menu..."),
    ("gewinnt das Match!", "remporte le match!"),
    ("verliert das Match", "perd le match"),
    ("Unentschieden im Match!", "Nulle in match!"),
    ("Auswahl", "Selection"),
    ("Einzelpartie", "lot unique"),
    ("Match (Best of 3)", "Match (au meilleur des 3 manches)"),
    ("↑/↓ wählen, Enter bestätigen, ESC zurück", "↑/↓ Sélectionner, confirmer avec Entrée, revenir avec ESC=Échap"),
]

# add missing spanish translations (fallback: english phrase) /
# Ergänze fehlende ES-Übersetzungen (Fallback: englische Phrase)
SUBS_ES += [
    ("Deutsch", "German"),
    ("English", "English"),
    ("J/Enter = Ja,  N/ESC = Nein", "Y/Entrar = Si, N/ESC = No"),
    ("Zugphase: ", "fase de tracción: "),
    ("ist am Zug", "para move"),
    ("hat eine Mühle gebildet! Wähle einen gegnerischen Stein.", "¡Ha formado un molino! Elige una ficha del adversario."),
    ("hat eine Mühle gebildet! Gegnerischer Stein wird entfernt.", "¡Ha formado un molino! Se elimina la ficha del adversario."),
    ("(ESC für Menü)", "(ESC al menú)"),
    ("Menü Navigation:", "Navegación por el Menú:"),
    ("Auswahl wechseln", "Cambiar selección"),
    ("Enter / Leertaste", "Entrar / Espacio"),
    ("Auswahl bestätigen", "Confirmar selección"),
    ("Zurück / Abbrechen", "Atrás / Cancelar"),
    ("Maus: Klick auf Menüoption wählt diese aus", "Ratón: al hacer clic en una opción del menú, se selecciona dicha opción."),
    ("Im Spiel:", "En juego:"),
    ("Spiel abbrechen / zurück zum Menü", "Cancelar juego / volver al menú"),
    ("Maus: Steine setzen und ziehen", "Ratón: colocar y mover piedras"),
    ("SPACE : Würfeln und fortfahren (wo angezeigt)", "ESPACIO: Lanzar y continuar (donde se indique)"),
    ("Netzwerk Menü:", "Menú de red:"),
    ("Host/Client/IP/Port/Bind auswählbar mit ↑/↓ und Enter", "Host/Cliente/IP/Puerto/Enlace seleccionables con ↑/↓ y Enter"),
    ("IP/Port kann per Dialog geändert werden", "El IP/puerto se puede cambiar mediante un cuadro de diálogo."),
    ("Verbinden startet das Netzwerkspiel", "Conectar inicia el juego en red."),
    ("Regelsets:", "conjuntos de reglas:"),
    ("Entschärft:", "desactivado:"),
    ("Klassische Regeln ohne zusätzliche Remis-/Sperrlogik", "Reglas clásicas sin lógica adicional de empate / bloqueo"),
    ("Kein Anti-Pendeln, keine 3-fach-Wiederholung,", "Sin antivibración, sin repetición triple,"),
    ("kein 100-Halbzüge-Remis", "No hay empate en 100 medias jugadas."),
    ("Turnier:", "Torneo:"),
    ("Anti-Pendeln: Sofortiges Zurückziehen desselben", "Antioscilación: retirada inmediata del mismo."),
    ("Steins ist verboten", "La piedra está prohibida."),
    ("3-fach-Wiederholung derselben Stellung (mit gleichem", "Repetición tres veces de la misma postura (con el mismo"),
    ("Zugrecht) = Remis", "correctamente) = Empate"),
    ("100 Halbzüge ohne Schlagfall = Remis", "100 medias jugadas sin jaque = empate"),
    ("Drücke ESC um Zurückkehren", "Pulsa ESC para volver atrás."),
    ("Keine legalen Züge", "No hay movimientos legales"),
    ("Spieler", "Jugador"),
    ("SL", "SL"),
    ("Rep:", "Rep:"),
    ("HZ:", "HM:"),
    ("Netzwerkspiel kommt später.", "Red game coming soon."),
    ("Network Game wirklich beenden?", "¿Quieres salir realmente del juego en red?"),
    ("Netzwerkspiel wirklich beenden?", "¿Desea realmente salir del juego en red?"),
    ("Verbindung fehlgeschlagen", "Error en la conexión"),
    ("Warte auf Client", "Esperando al cliente"),
    ("Verbunden – warte auf Start", "Conectado: esperando inicio"),
    ("ESC zum Abbrechen", "ESC para cancel"),
    ("Netzwerk-Würfeln", "Red dice roll"),
    ("Würfelergebnis", "Dice result"),
    ("Host beginnt – Spieler 1 (Weiß)", "Host iniciars – Jugador 1 (Blancas)"),
    ("Client beginnt – Spieler 1 (Weiß)", "Client iniciars – Jugador 1 (Blancas)"),
    ("Host beginnt - Spieler 1 (Weiß)", "Host iniciars - Jugador 1 (Blancas)"),
    ("Client beginnt - Spieler 1 (Weiß)", "Client iniciars - Jugador 1 (Blancas)"),
    ("Spieler 1 (Weiß): Host", "Jugador 1 (Blancas): Host"),
    ("Spieler 2 (Schwarz): Client", "Jugador 2 (Negras): Client"),
    ("Spieler 1 (Weiß): Client", "Jugador 1 (Blancas): Client"),
    ("Spieler 2 (Schwarz): Host", "Jugador 2 (Negras): Host"),
    ("Spieler 1 (Weiß)", "Jugador 1 (Blancas)"),
    ("Spieler 2 (Schwarz)", "Jugador 2 (Negras)"),
    ("Spieler 1", "Jugador 1"),
    ("Spieler 2", "Jugador 2"),
    ("Du bist Spieler 1 (Weiß)", "Eres Jugador 1 (Blancas)"),
    ("Du bist Spieler 2 (Schwarz)", "Eres Jugador 2 (Negras)"),
    ("Drücke SPACE, um zu starten...", "Pulsa ESPACIO para iniciar..."),
    ("hat die Verbindung beendet.", "ha finalizado la conexión."),
    ("Gegner entfernt einen Stein...", "Oponente retira una piedra..."),
    ("Gegner", "Oponente"),
    (" (DU)", " (You)"),
    (" (Du)", " (You)"),
    ("Bind: Lokal", "Encuadernación: Local"),
    ("Bind: LAN", "Encuadernación: LAN"),
    ("Verbinden", "Conectar"),
    ("Enter=OK, ESC=Abbrechen", "Entrar=OK, ESC=Cancelar"),
    ("Setzphase: Klicke auf einen freien Punkt", "Colocación: pulsa en un punpara libre"),
    ("Anti-Pendeln: mit demselben Stein sofort zurück ist verboten", "Anti-oscilación: está prohibido volver inmediatamente con la misma piedra."),
    ("Zwischenstand:", "Puntuación:"),
    ("Spiel ", "Partida "),
    ("Drücke SPACE für das nächste Spiel...", "Pulsa ESPACIO for the siguiente partida..."),
    ("Drücke ESC für das Menü...", "Pulsa ESC al menú..."),
    ("gewinnt das Match!", "gana el partido!"),
    ("verliert das Match", "pierde el partido"),
    ("Unentschieden im Match!", "Empate en el partido!"),
    ("Auswahl", "Selección"),
    ("Einzelpartie", "partida individual"),
    ("Match (Best of 3)", "Match (Best of 3)"),
    ("↑/↓ wählen, Enter bestätigen, ESC zurück", "↑/↓ para elegir, Entrar para confirmar, ESC para volver"),
]

SUBS_MAP = {"en": SUBS_EN, "fr": SUBS_FR, "es": SUBS_ES}

# retained name for backward-compatible usage in code (if referenced anywhere) /
# Beibehaltener Name für rückwärtskompatible Nutzung im Code (falls irgendwo referenziert)
TRANSLATION_SUBS = SUBS_EN

def tr(text: str) -> str:
    """Einfache Laufzeit-Übersetzung.
    Strategie:
      - Deutsch ist Quellsprache
      - Für en/fr/es gibt es separate Ersetzungslisten (Teilstrings)
      - Längste Phrasen zuerst, um Kollisionen zu minimieren
      - Fallback: Wenn keine passende Liste vorhanden, Original zurück
    
    """
    if not isinstance(text, str):
        return text
    if CURRENT_LANG == "de":
        return text
    # try to get substitution list for current language /
    # Versuche die substitutionsliste für die aktuelle Sprache
    subs = SUBS_MAP.get(CURRENT_LANG) or []

    # just in case: add english substitutions as fallback /
    # replace missing translations with english ones as fallback /
    # incomplete SUBS_FR/SUBS_ES are thus sensibly supplemented. /
    # Falls die aktuelle Sprache nicht Englisch ist, ergänze fehlende
    # Ersetzungen durch die englische Liste als Fallback. So werden
    # unvollständige SUBS_FR/SUBS_ES sinnvoll ergänzt.
    combined = list(subs)
    if CURRENT_LANG != "en":
        # add missing english pairs not available in subs /
        # existing pairs compared as pair; order later by length /
        # Füge nur solche englischen Paare hinzu, die nicht bereits in subs
        # vorhanden sind (Vergleich als Paar). Reihenfolge später nach Länge.
        for pair in SUBS_EN:
            if pair not in combined:
                combined.append(pair)

    if not combined:
        return text

    s = text
    for de_src, tgt in sorted(combined, key=lambda p: len(p[0]), reverse=True):
        s = s.replace(de_src, tgt)
    return s

# helper: text rendering that fits within a target width (font is scaled down) /
# Helfer: Text so rendern, dass er maximal eine Zielbreite nutzt (Schrift wird verkleinert)
def render_fit_text(text, color, max_width, base_size=FONT_SIZE, min_size=18, font_name="FreeSans"):
    # runtime translation applied /
    # Laufzeit-Übersetzung anwenden
    text = tr(text)
    size = base_size
    while size >= min_size:
        f = pygame.font.SysFont(font_name, size)
        surf = f.render(text, True, color)
        if surf.get_width() <= max_width:
            return surf
        size -= 2
    # fallback: minimum size
    # Fallback: minimale Größe
    f = pygame.font.SysFont(font_name, min_size)
    return f.render(text, True, color)

def confirm_abort(prompt="Spiel wirklich beenden?"):
    """Zeigt einen modalen Bestätigungsdialog (Ja/Nein) über dem aktuellen Screen.
    Rückgabe: True bei Ja/Enter, False bei Nein/ESC.
    """
    screen = pygame.display.get_surface()
    if screen is None:
        # if no active screen, abort safely
        # Falls kein aktiver Screen vorhanden ist, breche sicherheitshalber ab
        return False
    # half-transparent overlay with question /
    # Halbtransparenter Overlay mit Frage
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 140))
    screen.blit(overlay, (0, 0))
    q = render_fit_text(prompt, (255, 230, 180), max_width=WIDTH - 120, base_size=36, min_size=18)
    info = render_fit_text("J/Enter = Ja,  N/ESC = Nein", (220, 200, 150), max_width=WIDTH - 120, base_size=28, min_size=16)
    screen.blit(q, (WIDTH // 2 - q.get_width() // 2, HEIGHT // 2 - 30))
    screen.blit(info, (WIDTH // 2 - info.get_width() // 2, HEIGHT // 2 + 10))
    pygame.display.flip()
    clock = pygame.time.Clock()
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_y, pygame.K_j, pygame.K_RETURN):
                    return True
                if ev.key in (pygame.K_n, pygame.K_ESCAPE):
                    return False
        clock.tick(FPS)

def draw_menu(screen, font, selected_idx):
    screen.fill((30, 30, 30))
    title_font = pygame.font.SysFont("FreeSans", 64)
    title_surf = render_fit_text("Mühle", (255,255,255), max_width=WIDTH-60, base_size=64, min_size=28)
    screen.blit(title_surf, (WIDTH//2 - title_surf.get_width()//2, 60))
    options = get_menu_options()
    for i, option in enumerate(options):
        color = (0, 220, 0) if i == selected_idx else (255, 255, 255)
        surf = render_fit_text(option, color, max_width=WIDTH-100, base_size=FONT_SIZE)
        x = WIDTH//2 - surf.get_width()//2
        y = 200 + i * 80
        screen.blit(surf, (x, y))
    pygame.display.flip()

def get_menu_item_at_pos(pos, font):
    options = get_menu_options()
    for i, option in enumerate(options):
        surf = render_fit_text(option, (255,255,255), max_width=WIDTH-100, base_size=FONT_SIZE)
        x = WIDTH//2 - surf.get_width()//2
        y = 200 + i * 80
        rect = pygame.Rect(x, y, surf.get_width(), surf.get_height())
        if rect.collidepoint(pos):
            return i
    return None

def würfeln_view(screen, font, clock):
    info_font = pygame.font.SysFont("FreeSans", 36)
    result_font = pygame.font.SysFont("FreeSans", 54)
    mensch_wurf = None
    # keeps internal variable / 
    # bleibt interne Variable
    ki_wurf = None
    nachwurf = False
    rolling = True
    winner = None
    while rolling:
        screen.fill((240, 220, 180))
        text = render_fit_text("Würfeln: Wer beginnt? Drücke SPACE!", (60,40,20), max_width=WIDTH-60, base_size=36, min_size=18)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, 120))
        if mensch_wurf is not None and ki_wurf is not None:
            mensch_txt = render_fit_text(f"Spieler würfelt: {mensch_wurf}", (0,220,0), max_width=WIDTH-60, base_size=54, min_size=22)
            ki_txt = render_fit_text(f"SL würfelt: {ki_wurf}", (220,0,0), max_width=WIDTH-60, base_size=54, min_size=22)
            screen.blit(mensch_txt, (WIDTH//2 - mensch_txt.get_width()//2, 250))
            screen.blit(ki_txt, (WIDTH//2 - ki_txt.get_width()//2, 320))
            if winner:
                # winner label localize (player vs. AI) /
                # Gewinner-Bezeichnung lokalisieren ("Spieler" bzw. "SL")
                winner_label = winner
                if winner == "Spieler":
                    if CURRENT_LANG == "en":
                        winner_label = "Player"
                    elif CURRENT_LANG == "fr":
                        winner_label = "Joueur"
                    elif CURRENT_LANG == "es":
                        winner_label = "Jugador"
                # game set localize /
                # Satz lokalisieren
                if CURRENT_LANG == "de":
                    win_line = f"{winner_label} beginnt und spielt mit Weiß!"
                elif CURRENT_LANG == "en":
                    win_line = f"{winner_label} starts and plays White!"
                elif CURRENT_LANG == "fr":
                    win_line = f"{winner_label} commence et joue avec les blancs !"
                else:  # es
                    win_line = f"{winner_label} empieza y juega con blancas!"
                win_txt = render_fit_text(win_line, (255,180,0), max_width=WIDTH-60, base_size=36, min_size=18)
                screen.blit(win_txt, (WIDTH//2 - win_txt.get_width()//2, 420))
                # continue note localize
                # Continue-Hinweis lokalisieren
                if CURRENT_LANG == "de":
                    cont_line = "Drücke SPACE für das Spielfeld..."
                elif CURRENT_LANG == "en":
                    cont_line = "Press SPACE to continue to the board..."
                elif CURRENT_LANG == "fr":
                    cont_line = "Appuyez ESPACE pour le plateau..."
                else:
                    cont_line = "Pulsa ESPACIO para el tablero..."
                cont_txt = render_fit_text(cont_line, (120,100,80), max_width=WIDTH-60, base_size=36, min_size=18)
                screen.blit(cont_txt, (WIDTH//2 - cont_txt.get_width()//2, 500))
                nachwurf = True
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_l:
                    toggle_language()
                    # re-render then continue waiting /
                    # Neu rendern, dann weiter warten
                    break
                if mensch_wurf is None or ki_wurf is None:
                    if event.key == pygame.K_SPACE:
                        mensch_wurf = random.randint(1,6)
                        ki_wurf = random.randint(1,6)
                        if mensch_wurf > ki_wurf:
                            winner = "Spieler"
                        elif ki_wurf > mensch_wurf:
                            winner = "SL"
                        else:
                            winner = None
                            mensch_wurf = None
                            ki_wurf = None
                elif nachwurf and event.key == pygame.K_SPACE:
                    if winner in ("Spieler", "SL"):
                        return winner
        clock.tick(FPS)
    return None

def spielfeld_view(screen, font, clock, starter, state=None, stones_set=None):
    # note: SL difficulty is set from global state if present /
    # Hinweis: SL-Schwierigkeit wird aus globalem Zustand gesetzt, wenn vorhanden
    difficulty = globals().get("CURRENT_DIFFICULTY", "Leicht")
    ruleset = globals().get("CURRENT_RULESET", "Entschärft")
    # cancel flag for ESC confirmation /
    # Abbruch-Flag für ESC-Bestätigung
    aborted = False
    # scaling relative to base 800x800 /
    # Skalierung relativ zur Basis 800x800
    ui_scale = max(0.6, min(WIDTH, HEIGHT) / 800.0)
    # basic distances (adjustable as desired) /
    # infoline 15px higher, without moving top bearing and counter /
    # Grundabstände (anpassbar wie gewünscht)
    # Infozeile 15px weiter nach oben, ohne das obere Lager zu verschieben
    INFO_Y = max(10, int(30 * ui_scale) - 35)
    COUNTER_MARGIN = int(40 * ui_scale)
    # basepositions as before, then apply desired offsets /
    # Basispositionen wie zuvor, dann gewünschte Offsets anwenden
    base_top = max(INFO_Y + 40, int(90 * ui_scale) - 20)
    base_bot = min(HEIGHT - 20, HEIGHT - int(90 * ui_scale) + 50)
    # move: upper bearing +23px down (3px extra), lower bearing 25px up /
    # Verschiebung: oberes Lager +23px nach unten (3px extra), unteres Lager 25px nach oben
    COUNTER_Y_TOP = min(base_top + 23, HEIGHT - 100)
    COUNTER_Y_BOT = max(base_bot - 25, COUNTER_Y_TOP + 100)
    COUNTER_R = max(6, int(16 * ui_scale))
    # available area for board between counters /
    # Verfügbarer Bereich fürs Board zwischen den Countern
    top_free = COUNTER_Y_TOP + COUNTER_R + int(20 * ui_scale)
    bottom_free = COUNTER_Y_BOT - COUNTER_R - int(20 * ui_scale)
    # board scaling from height/width (base-outer=260) /
    # Board-Skalierung aus Höhe/Breite berechnen (Basis-Outer=260)
    margin_x = int(40 * ui_scale)
    board_scale_y = max(0.5, (bottom_free - top_free) / (2.0 * 260))
    board_scale_x = max(0.5, (WIDTH - 2.0 * margin_x) / (2.0 * 260))
    board_scale = min(ui_scale, board_scale_x, board_scale_y)
    # stone-/line sizes according to board scale /
    # - empty nodes keep old radius (~16)
    # - black/white stones ~1.5x larger (~24)
    # Stein-/Linienstärken passend zum Board skalieren:
    # - Leere Knoten behalten den alten Radius (~16)
    # - Schwarze/weiße Steine ~1.5x größer (~24)
    NODE_R = max(8, int(16 * board_scale))
    PIECE_R = max(12, int(24 * board_scale))
    # backward compatibility for existing uses / 
    # Backward-Kompatibilität für existierende Verwendungen
    STONE_R = PIECE_R
    HIT_R = max(14, int(27 * board_scale))
    SELECT_R = max(PIECE_R + 6, int(28 * board_scale))
    LINE_W = max(2, int(5 * board_scale))
    # definitions of all mills (each 3 positions) /
    # Definition aller Mühlen (jeweils 3 Felder)
    muhlen = [
        # rings: outer
        # Ringe: außen
        [0,1,2], [2,3,4], [4,5,6], [6,7,0],
        # middle
        # mitte
        [8,9,10], [10,11,12], [12,13,14], [14,15,8],
        # inner
        # innen
        [16,17,18], [18,19,20], [20,21,22], [22,23,16],
        # valid vertical and horizontal middle lines:
        # gültige Vertikale und Horizontale Mittellinien:
        [1,9,17], [3,11,19], [5,13,21], [7,15,23]
        # corners are invalid mill connections:
        # Eckpunkte sind ungültige mühle verbindungen:
        # [0,8,16], [2,10,18], [4,12,20], [6,14,22]
    ]

    # 0: empty, 1: white, 2: black /
    # 0: leer, 1: weiß, 2: schwarz
    if state is None:
        state = [0]*24
    if stones_set is None:
        stones_set = [0, 0]  # [white, black] / [weiß, schwarz]
    # here must be SL not ki or ai /
    # hier muss SL stehen nicht ki oder ai
    if starter == "SL":
        current_player = 1
        player_types = {1: "SL", 2: "Mensch"}
    elif starter == "Spieler":
        current_player = 1
        player_types = {1: "Mensch", 2: "SL"}
    else:
        current_player = 1
        player_types = {1: "Mensch", 2: "SL"}

    # label for player with color (e.g., "Mensch (Weiß)", "SL (Schwarz)") /
    # Label für Spieler mit Farbe (z. B. "Mensch (Weiß)", "SL (Schwarz)")
    def label_for(p):
        return f"{player_types[p]} ({'Weiß' if p==1 else 'Schwarz'})"

    # helper to draw the supply stones (top/bottom) /
    # Helfer zum Zeichnen der Vorratssteine (oben/unten)
    def draw_counters():
        # fixed borders: 50px left/right, 9 slots evenly spaced /
        # Feste Ränder: 50px links/rechts, 9 Slots gleichmäßig verteilt
            left_margin = 50
            right_margin = 50
            steps = 8  # 9 stones -> 8 gaps / 9 Steine -> 8 Abstände
            width_avail = max(1, WIDTH - left_margin - right_margin)
            spacing = max(PIECE_R*2 + 6, width_avail // steps)
            start_x = left_margin
            r = PIECE_R
            total = 9
            # upper: placeholder, then white stones /
            # oben: Platzhalter, dann weiße Steine
            remain_w = max(0, total - stones_set[0])
            y_top = COUNTER_Y_TOP
            for i in range(9):
                x = start_x + i*spacing
                pygame.draw.circle(screen, (185,180,160), (x, y_top), r, 0)
                pygame.draw.circle(screen, (140,130,110), (x, y_top), r, 1)
            for i in range(remain_w):
                x = start_x + i*spacing
                pygame.draw.circle(screen, (255,255,255), (x, y_top), r, 0)
                pygame.draw.circle(screen, (100,90,70), (x, y_top), r, 2)
            # bottom: placeholder, then black stones /
            # unten: Platzhalter, dann schwarze Steine
            remain_b = max(0, total - stones_set[1])
            y_bot = COUNTER_Y_BOT
            for i in range(9):
                x = start_x + i*spacing
                pygame.draw.circle(screen, (185,180,160), (x, y_bot), r, 0)
                pygame.draw.circle(screen, (140,130,110), (x, y_bot), r, 1)
            for i in range(remain_b):
                x = start_x + i*spacing
                pygame.draw.circle(screen, (0,0,0), (x, y_bot), r, 0)
                pygame.draw.circle(screen, (100,90,70), (x, y_bot), r, 2)

    # mill status tracking per player /
    # Mühlen-Status pro Spieler speichern
    last_mills = {1: set(), 2: set()}
    def check_muehle(pos, player):
        # check all actual mills for this player /
        # Ermittele alle aktuell bestehenden Mühlen dieses Spielers
        current = {i for i, m in enumerate(muhlen) if all(state[j] == player for j in m)}
        # new mills are those that were not there before and contain the last placed/moved position /
        # Neue Mühlen sind die, die vorher nicht da waren und die die zuletzt gesetzte/gezogene Position enthalten
        created = {i for i in current if pos in muhlen[i]} - last_mills[player]
        # update the stored mill state /
        # Update des gespeicherten Mühlenzustands
        last_mills[player] = current
        return len(created) > 0

    def remove_opponent_stone(player):
        nonlocal aborted
        opponent = 2 if player == 1 else 1
        candidates = [i for i in range(24) if state[i] == opponent and not any(all(state[j]==opponent for j in m) for m in muhlen if i in m)]
        if not candidates:
            candidates = [i for i in range(24) if state[i] == opponent]
        if player_types[player] == "Mensch":
            removing = True
            while removing:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit(); sys.exit()
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        if confirm_abort():
                            aborted = True
                            return False
                    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        mx, my = event.pos
                        for idx in candidates:
                            x, y = positions[idx]
                            if (mx-x)**2 + (my-y)**2 < HIT_R**2:
                                state[idx] = 0
                                removing = False
                                return True
                screen.fill((240, 220, 180))
                for a, b in lines:
                    pygame.draw.line(screen, (120, 100, 80), positions[a], positions[b], 5)
                for idx2, (x2, y2) in enumerate(positions):
                    color = (200, 180, 120)
                    if state[idx2] == 1:
                        color = (255, 255, 255)
                    elif state[idx2] == 2:
                        color = (0, 0, 0)
                    rad = PIECE_R if state[idx2] else NODE_R
                    pygame.draw.circle(screen, color, (x2, y2), rad, 0 if state[idx2] else 3)
                info = "Mühle! Wähle einen gegnerischen Stein zum Entfernen."
                info_surf = render_fit_text(info, (200,40,40), max_width=WIDTH-100, base_size=28, min_size=18)
                screen.blit(info_surf, (WIDTH//2 - info_surf.get_width()//2, INFO_Y))
                draw_counters()
                pygame.display.flip()
                clock.tick(FPS)
        else:
            non_mill = [i for i in range(24) if state[i] == opponent and not any(all(state[j]==opponent for j in m) for m in muhlen if i in m)]
            if non_mill:
                idx = random.choice(non_mill)
                state[idx] = 0
                return True
            all_opponent = [i for i in range(24) if state[i] == opponent]
            if all_opponent:
                idx = random.choice(all_opponent)
                state[idx] = 0
                return True
            return False

    cx = WIDTH // 2
    cy = int((top_free + bottom_free) // 2)
    # circles a bit tighter set, so larger pieces fit well /
    # Ringe etwas enger setzen, damit größere Steine gut passen
    compact = 0.9
    outer = int(260 * compact * board_scale)
    mid = int(180 * compact * board_scale)
    inner = int(100 * compact * board_scale)
    positions = [
        (cx-outer, cy-outer), (cx, cy-outer), (cx+outer, cy-outer),
        (cx+outer, cy), (cx+outer, cy+outer), (cx, cy+outer), (cx-outer, cy+outer), (cx-outer, cy),
        (cx-mid, cy-mid), (cx, cy-mid), (cx+mid, cy-mid),
        (cx+mid, cy), (cx+mid, cy+mid), (cx, cy+mid), (cx-mid, cy+mid), (cx-mid, cy),
        (cx-inner, cy-inner), (cx, cy-inner), (cx+inner, cy-inner),
        (cx+inner, cy), (cx+inner, cy+inner), (cx, cy+inner), (cx-inner, cy+inner), (cx-inner, cy)
    ]
    lines = [
        (0,1),(1,2),(2,3),(3,4),(4,5),(5,6),(6,7),(7,0),
        (8,9),(9,10),(10,11),(11,12),(12,13),(13,14),(14,15),(15,8),
        (16,17),(17,18),(18,19),(19,20),(20,21),(21,22),(22,23),(23,16),
        (1,9),(3,11),(5,13),(7,15),
        (9,17),(11,19),(13,21),(15,23)
    ]

    # helper functions for AI decisions /
    # Hilfsfunktionen für SL-Entscheidungen
    def line_forms_mill_if_place(idx, player):
        for m in muhlen:
            if idx in m and all((state[k] == player) for k in m if k != idx) and state[idx] == 0:
                return True
        return False
    def find_block_positions(player):
        opponent = 2 if player == 1 else 1
        blocks = []
        for m in muhlen:
            vals = [state[k] for k in m]
            if vals.count(opponent) == 2 and vals.count(0) == 1:
                empty_idx = m[vals.index(0)]
                blocks.append(empty_idx)
        return blocks
    def count_mills_for(player):
        return sum(1 for m in muhlen if all(state[k] == player for k in m))
    def count_open_twos(player):
        c = 0
        for m in muhlen:
            vals = [state[k] for k in m]
            if vals.count(player) == 2 and vals.count(0) == 1:
                c += 1
        return c
    def mobility(player):
        stones = [i for i, v in enumerate(state) if v == player]
        if len(stones) == 3:
            return sum(1 for v in state if v == 0)
        moves = 0
        for i in stones:
            for a, b in lines:
                if a == i and state[b] == 0:
                    moves += 1
                elif b == i and state[a] == 0:
                    moves += 1
        return moves
    def evaluate(player):
        opponent = 2 if player == 1 else 1
        return (
            50 * count_mills_for(player)
            + 12 * count_open_twos(player)
            + 2 * mobility(player)
            + 3 * sum(1 for v in state if v == player)
            - 45 * count_mills_for(opponent)
            - 12 * count_open_twos(opponent)
            - 2 * mobility(opponent)
            - 3 * sum(1 for v in state if v == opponent)
        )
    # setphase loop /
    # Setzphase
    setzphase = True
    while setzphase:
        # board drawing /
        # Brett zeichnen
        screen.fill((240, 220, 180))
        for a, b in lines:
            pygame.draw.line(screen, (120, 100, 80), positions[a], positions[b], LINE_W)
        for idx, (x, y) in enumerate(positions):
            color = (200, 180, 120)
            if state[idx] == 1:
                color = (255, 255, 255)
            elif state[idx] == 2:
                color = (0, 0, 0)
            rad = PIECE_R if state[idx] else NODE_R
            pygame.draw.circle(screen, color, (x, y), rad, 0 if state[idx] else 3)
        # Info
        info = f"Setzphase: {label_for(current_player)} setzt Stein ({stones_set[current_player-1]+1}/9)"
        info_surf = render_fit_text(info, (60,40,20), max_width=WIDTH-60, base_size=FONT_SIZE)
        screen.blit(info_surf, (WIDTH//2 - info_surf.get_width()//2, INFO_Y))
        draw_counters()
        # Debug-Overlay
        draw_debug_overlay(screen, [
            "Mode: Singleplayer",
            "Phase: Setzphase",
            f"Player: {current_player}",
            f"stones_set: W={stones_set[0]} S={stones_set[1]}",
        ])
        pygame.display.flip()
        # Input handling /
        # Eingabe
        if player_types[current_player] == "Mensch":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if confirm_abort():
                        return None
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_d:
                    toggle_debug_overlay()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos
                    for idx, (x, y) in enumerate(positions):
                        if (mx-x)**2 + (my-y)**2 < HIT_R**2 and state[idx] == 0:
                            state[idx] = current_player
                            stones_set[current_player-1] += 1
                            muehle_gebildet = check_muehle(idx, current_player)
                            if muehle_gebildet:
                                screen.fill((240, 220, 180))
                                for a, b in lines:
                                    pygame.draw.line(screen, (120, 100, 80), positions[a], positions[b], LINE_W)
                                for idx2, (x2, y2) in enumerate(positions):
                                    color = (200, 180, 120)
                                    if state[idx2] == 1:
                                        color = (255, 255, 255)
                                    elif state[idx2] == 2:
                                        color = (0, 0, 0)
                                    rad = PIECE_R if state[idx2] else NODE_R
                                    pygame.draw.circle(screen, color, (x2, y2), rad, 0 if state[idx2] else 3)
                                info2 = f"{label_for(current_player)} entfernt einen Stein"
                                info2_surf = render_fit_text(info2, (200,40,40), max_width=WIDTH-100, base_size=28, min_size=18)
                                screen.blit(info2_surf, (WIDTH//2 - info2_surf.get_width()//2, INFO_Y))
                                draw_counters()
                                pygame.display.flip()
                                remove_opponent_stone(current_player)
                                if aborted:
                                    return None
                                # note: at setting phase there is no win by <3 stones /
                                # after placing: always switch player; if both have 9, end setting phase and
                                # opponent starts moving phase.
                                # Hinweis: In der Setzphase gibt es keinen Sieg durch <3 Steine.
                            # Nach dem Setzen: immer Spieler wechseln; falls beide 9 haben, endet Setzphase und
                            # der Gegner beginnt die Zugphase.
                            if stones_set[0] == 9 and stones_set[1] == 9:
                                setzphase = False
                            current_player = 2 if current_player == 1 else 1
                            break
            clock.tick(FPS)
        else:
            if stones_set[current_player-1] < 9:
                freie = [i for i, v in enumerate(state) if v == 0]
                if freie:
                    # AI move at setting phase is dependent on difficulty
                    # SL-Zug in Setzphase abhängig von Schwierigkeit wählen
                    idx = None
                    if difficulty == "Leicht":
                        idx = random.choice(freie)
                    elif difficulty == "Mittel":
                        # 1) instantly form mill
                        # 1) Sofort Mühle bilden
                        mills_now = [p for p in freie if line_forms_mill_if_place(p, current_player)]
                        if mills_now:
                            idx = random.choice(mills_now)
                        else:
                            # 2) block opponent
                            # 2) Blocken
                            blocks = [p for p in find_block_positions(current_player) if p in freie]
                            if blocks:
                                idx = random.choice(blocks)
                            else:
                                idx = random.choice(freie)
                    else:  # "difficult" / "Schwer"
                        best_score = None
                        best_choices = []
                        for p in freie:
                            # simulate place
                            state[p] = current_player
                            s = evaluate(current_player)
                            state[p] = 0
                            if best_score is None or s > best_score:
                                best_score = s
                                best_choices = [p]
                            elif s == best_score:
                                best_choices.append(p)
                        idx = random.choice(best_choices) if best_choices else random.choice(freie)
                    state[idx] = current_player
                    stones_set[current_player-1] += 1
                    muehle_gebildet = check_muehle(idx, current_player)
                    if muehle_gebildet:
                        screen.fill((240, 220, 180))
                        for a, b in lines:
                            pygame.draw.line(screen, (120, 100, 80), positions[a], positions[b], LINE_W)
                        for idx2, (x2, y2) in enumerate(positions):
                            color = (200, 180, 120)
                            if state[idx2] == 1:
                                color = (255, 255, 255)
                            elif state[idx2] == 2:
                                color = (0, 0, 0)
                            rad = PIECE_R if state[idx2] else NODE_R
                            pygame.draw.circle(screen, color, (x2, y2), rad, 0 if state[idx2] else 3)
                        info2 = f"{label_for(current_player)} entfernt einen Stein"
                        info2_surf = render_fit_text(info2, (200,40,40), max_width=WIDTH-100, base_size=28, min_size=18)
                        screen.blit(info2_surf, (WIDTH//2 - info2_surf.get_width()//2, INFO_Y))
                        draw_counters()
                        pygame.display.flip()
                        pygame.time.wait(900)
                        remove_opponent_stone(current_player)
                        if aborted:
                            return None
                        # note: at setting phase there is no win by <3 stones /
                        # after placing: always switch player; if both have 9, end setting phase and
                        # opponent starts moving phase.
                        # Hinweis: In der Setzphase gibt es keinen Sieg durch <3 Steine.
                    # Nach dem Setzen: immer Spieler wechseln; falls beide 9 haben, endet Setzphase und
                    # der Gegner beginnt die Zugphase.
                    if stones_set[0] == 9 and stones_set[1] == 9:
                        setzphase = False
                    current_player = 2 if current_player == 1 else 1
                pygame.time.wait(400)
            else:
                current_player = 2 if current_player == 1 else 1
    # no win checking in setting phase - conditions for winning only apply in moving phase
    # moving phase /
    # Kein Sieg-Ende in der Setzphase – Siegbedingungen gelten erst in der Zugphase.
    # Zugphase
    zugphase = True
    selected = None
    winner = None
    is_draw = False
    # tournament add-ons: repetition, halfmove rule, anti-pendulum /
    # Turnier-Zusatz: Wiederholung, Halbzugregel, Anti-Pendeln
    position_counts = {}
    halfmove_clock = 0
    last_move_by = {1: (-1, -1), 2: (-1, -1)}  # per player (from, to) / pro Spieler (from, to)
    def update_draw_state(captured):
        nonlocal halfmove_clock, is_draw
        if ruleset != "Turnier":
            return
        if captured:
            halfmove_clock = 0
        else:
            halfmove_clock += 1
        key = (tuple(state), current_player)
        position_counts[key] = position_counts.get(key, 0) + 1
        if position_counts[key] >= 3 or halfmove_clock >= 100:
            is_draw = True
    def get_adjacent(pos):
        adj = []
        for a, b in lines:
            if a == pos:
                adj.append(b)
            elif b == pos:
                adj.append(a)
        return adj
    def has_moves(player):
        stones = [i for i, v in enumerate(state) if v == player]
        lm_from, lm_to = last_move_by.get(player, (-1, -1))
        if len(stones) == 3:
            # flying phase: any free field as target, except immediate pendulum back of same stone
            # Fliegen: jedes freie Feld als Ziel, außer sofortiges Zurückpendeln desselben Steins
            freie = [i for i, v in enumerate(state) if v == 0]
            for s in stones:
                for t in freie:
                    if ruleset == "Turnier" and s == lm_to and t == lm_from:
                        continue
                    return True
            return False
        for s in stones:
            for j in get_adjacent(s):
                if state[j] != 0:
                    continue
                if ruleset == "Turnier" and s == lm_to and j == lm_from:
                    # anti pendulum: immediate back of same stone forbidden
                    # Anti-Pendeln: gleicher Stein sofort zurück verboten
                    continue
                return True
        return False
    def check_win():
        if sum(1 for v in state if v == 1) < 3:
            return 2
        if sum(1 for v in state if v == 2) < 3:
            return 1
        if not has_moves(1):
            return 2
        if not has_moves(2):
            return 1
        return None
    while zugphase:
        screen.fill((240, 220, 180))
        for a, b in lines:
            pygame.draw.line(screen, (120, 100, 80), positions[a], positions[b], LINE_W)
        for idx, (x, y) in enumerate(positions):
            color = (200, 180, 120)
            if state[idx] == 1:
                color = (255, 255, 255)
            elif state[idx] == 2:
                color = (0, 0, 0)
            if selected == idx:
                pygame.draw.circle(screen, (0,220,0), (x, y), SELECT_R, 3)
            rad = PIECE_R if state[idx] else NODE_R
            pygame.draw.circle(screen, color, (x, y), rad, 0 if state[idx] else 3)
            # anti-pendulum: mark forbidden retreat target red /
            # only if last moved stone is currently selected
            # Anti-Pendeln: markiere nur das verbotene Rückzugs-Zielfeld rot,
            # und nur wenn der zuletzt gezogene Stein aktuell ausgewählt ist
            if ruleset == "Turnier" and selected is not None:
                mv = last_move_by.get(current_player, (-1, -1))
                # mv = (from, to) of current player /
                # mv = (from, to) des aktuellen Spielers
                if selected == mv[1] and idx == mv[0]:
                    pygame.draw.circle(screen, (220,40,40), (x, y), SELECT_R, 2)
        draw_counters()
        # tournament overlay: per side (white/black) with labels and highlight of active player /
        # Turnier-Overlay: pro Seite (Weiß/Schwarz) mit Labels und Hervorhebung des aktiven Spielers
        if ruleset == "Turnier":
            rep_w = position_counts.get((tuple(state), 1), 0)
            rep_s = position_counts.get((tuple(state), 2), 0)
            col_inactive = (80,60,40)
            col_active = (200,140,60)
            mid_y = HEIGHT//2
            # left: white
            # Links: Weiß
            color_w = col_active if current_player==1 else col_inactive
            left_x = 12
            label_w = render_fit_text("Weiß", color_w, max_width=120, base_size=16, min_size=12)
            rep_w_surf = render_fit_text(f"Rep: {rep_w}/3", color_w, max_width=140, base_size=16, min_size=12)
            hz_w_surf = render_fit_text(f"HZ: {halfmove_clock}", color_w, max_width=140, base_size=16, min_size=12)
            screen.blit(label_w, (left_x, mid_y - 28))
            screen.blit(rep_w_surf, (left_x, mid_y - 8))
            screen.blit(hz_w_surf, (left_x, mid_y + 10))
            # right: black
            # Rechts: Schwarz
            color_s = col_active if current_player==2 else col_inactive
            right_x = WIDTH - 12
            label_s = render_fit_text("Schwarz", color_s, max_width=120, base_size=16, min_size=12)
            rep_s_surf = render_fit_text(f"Rep: {rep_s}/3", color_s, max_width=140, base_size=16, min_size=12)
            hz_s_surf = render_fit_text(f"HZ: {halfmove_clock}", color_s, max_width=140, base_size=16, min_size=12)
            screen.blit(label_s, (right_x - label_s.get_width(), mid_y - 28))
            screen.blit(rep_s_surf, (right_x - rep_s_surf.get_width(), mid_y - 8))
            screen.blit(hz_s_surf, (right_x - hz_s_surf.get_width(), mid_y + 10))
        if winner or (ruleset=="Turnier" and is_draw):
            # first show final board frame /
            # Zuerst einen Frame nur mit dem finalen Brett zeigen
            pygame.display.flip()
            # Baselines
            base_hint_y = 10
            base_info_y = 30
            # offsets: hint -3px, info -8px (game-over 3px higher than before) /
            # Offsets: hint -3px, info -8px (Game-Over 3px höher als zuvor)
            y_hint = max(0, base_hint_y - 3)
            y_info = max(0, base_info_y - 8)
            hint_height = 0
            # note (tournament) optional /
            # Hinweis (Turnier) optional
            if ruleset == "Turnier" and winner:
                loser = 2 if winner == 1 else 1
                stones_loser = sum(1 for v in state if v == loser)
                try:
                    if stones_loser >= 3 and not has_moves(loser):
                        hint_surf = render_fit_text(tr("Keine legalen Züge"), (200,60,40), max_width=WIDTH-160, base_size=28, min_size=16)
                        screen.blit(hint_surf, (WIDTH//2 - hint_surf.get_width()//2, y_hint))
                        hint_height = hint_surf.get_height()
                except Exception:
                    pass
            # ensure: at least 5px distance if hint present /
            # Sicherstellen: mind. 5px Abstand, falls Hinweis vorhanden
            if hint_height > 0:
                y_info = max(y_info, y_hint + hint_height + 5)
            # Game-Over Overlay
            info = (f"Spielende! {'Weiß' if winner==1 else 'Schwarz'} gewinnt! (ESC für Menü)" if winner
                    else "Spielende! Remis nach Turnierregeln (ESC für Menü)")
            info_surf = render_fit_text(info, (60,40,20), max_width=WIDTH-160, base_size=36, min_size=18)
            screen.blit(info_surf, (WIDTH//2 - info_surf.get_width()//2, y_info))
            # Debug-Overlay
            draw_debug_overlay(screen, [
                "Mode: Singleplayer",
                "Phase: Zugende",
                f"Winner: {winner}",
                f"Draw: {is_draw}",
            ])
            pygame.display.flip()
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit(); sys.exit()
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        waiting = False
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_d:
                        toggle_debug_overlay()
                clock.tick(FPS)
            break
        else:
            info = f"Zugphase: {label_for(current_player)} bewegt einen Stein"
            info_surf = render_fit_text(info, (60,40,20), max_width=WIDTH-60, base_size=FONT_SIZE)
            screen.blit(info_surf, (WIDTH//2 - info_surf.get_width()//2, INFO_Y))
        # Debug-Overlay
        draw_debug_overlay(screen, [
            "Mode: Singleplayer",
            "Phase: Zugphase",
            f"Player: {current_player}",
            f"LastMove P1: {last_move_by.get(1)}",
            f"LastMove P2: {last_move_by.get(2)}",
            f"HalfMove: {halfmove_clock}",
            f"DrawRep: {position_counts.get((tuple(state), current_player), 0)}",
        ])
        pygame.display.flip()
        # play execute: SL or human / 
        # Zug ausführen: SL oder Mensch
        if player_types[current_player] == "SL":
            ai_player = current_player
            ai_opponent = 2 if ai_player == 1 else 1
            stones = [i for i, v in enumerate(state) if v == ai_player]
            moved = False
            cap = False
            if len(stones) == 3:
                freie = [i for i, v in enumerate(state) if v == 0]
                # sort by difficulty /
                # Sortierung je nach Schwierigkeit
                def pick_targets(i):
                    if difficulty == "Leicht":
                        return random.sample(freie, k=len(freie))
                    elif difficulty == "Mittel":
                        pri_now = [j for j in freie if line_forms_mill_if_place(j, ai_player)]
                        if pri_now:
                            return pri_now + [j for j in freie if j not in pri_now]
                        # block by flying possible
                        # Blocken durch Springen möglich
                        blocks = [j for j in find_block_positions(ai_player) if j in freie]
                        return blocks + [j for j in freie if j not in blocks]
                    else:
                        # difficult: sort by evaluation
                        # Schwer: nach Bewertung sortieren
                        scored = []
                        for j in freie:
                            state[i] = 0; state[j] = ai_player
                            s = evaluate(ai_player)
                            state[j] = 0; state[i] = ai_player
                            scored.append((s, j))
                        scored.sort(reverse=True)
                        return [j for _, j in scored]
                random.shuffle(stones)
                for i in stones:
                    for j in pick_targets(i):
                        if ruleset == "Turnier" and last_move_by.get(ai_player) == (j, i):
                            continue
                        if state[i] == ai_player and state[j] == 0:
                            state[i] = 0
                            state[j] = ai_player
                            muehle_gebildet = check_muehle(j, ai_player)
                            if muehle_gebildet:
                                screen.fill((240, 220, 180))
                                for a, b in lines:
                                    pygame.draw.line(screen, (120, 100, 80), positions[a], positions[b], 5)
                                for idx2, (x2, y2) in enumerate(positions):
                                    color = (200, 180, 120)
                                    if state[idx2] == 1:
                                        color = (255, 255, 255)
                                    elif state[idx2] == 2:
                                        color = (0, 0, 0)
                                    rad = PIECE_R if state[idx2] else NODE_R
                                    pygame.draw.circle(screen, color, (x2, y2), rad, 0 if state[idx2] else 3)
                                info2 = f"{label_for(ai_player)} entfernt einen Stein"
                                info2_surf = render_fit_text(info2, (200,40,40), max_width=WIDTH-100, base_size=28, min_size=18)
                                screen.blit(info2_surf, (WIDTH//2 - info2_surf.get_width()//2, INFO_Y))
                                draw_counters()
                                pygame.display.flip()
                                pygame.time.wait(600)
                                cap = remove_opponent_stone(ai_player)
                            else:
                                cap = False
                            moved = True
                            last_move_by[ai_player] = (i, j)
                            break
                    if moved:
                        break
            else:
                def pick_adjs(i):
                    adj = get_adjacent(i)
                    if difficulty == "Leicht":
                        random.shuffle(adj)
                        return adj
                    elif difficulty == "Mittel":
                        pri_now = [j for j in adj if state[j]==0 and line_forms_mill_if_place(j, ai_player)]
                        rest = [j for j in adj if j not in pri_now and state[j]==0]
                        # try to block: move to threatened empty point /
                        # Versuch zu blocken: ziehe an bedrohten leeren Punkt
                        blocks = [j for j in find_block_positions(ai_player) if j in rest]
                        ordered = pri_now + blocks + [j for j in rest if j not in blocks]
                        return ordered
                    else:
                        scored = []
                        for j in adj:
                            if state[j] != 0:
                                continue
                            state[i] = 0; state[j] = ai_player
                            s = evaluate(ai_player)
                            state[j] = 0; state[i] = ai_player
                            scored.append((s, j))
                        scored.sort(reverse=True)
                        return [j for _, j in scored]
                random.shuffle(stones)
                for i in stones:
                    for j in pick_adjs(i):
                        if ruleset == "Turnier" and last_move_by.get(ai_player) == (j, i):
                            continue
                        if state[i] == ai_player and state[j] == 0:
                            state[i] = 0
                            state[j] = ai_player
                            muehle_gebildet = check_muehle(j, ai_player)
                            if muehle_gebildet:
                                screen.fill((240, 220, 180))
                                for a, b in lines:
                                    pygame.draw.line(screen, (120, 100, 80), positions[a], positions[b], 5)
                                for idx2, (x2, y2) in enumerate(positions):
                                    color = (200, 180, 120)
                                    if state[idx2] == 1:
                                        color = (255, 255, 255)
                                    elif state[idx2] == 2:
                                        color = (0, 0, 0)
                                    rad = PIECE_R if state[idx2] else NODE_R
                                    pygame.draw.circle(screen, color, (x2, y2), rad, 0 if state[idx2] else 3)
                                info2 = f"{label_for(ai_player)} entfernt einen Stein"
                                info2_surf = render_fit_text(info2, (200,40,40), max_width=WIDTH-100, base_size=28, min_size=18)
                                screen.blit(info2_surf, (WIDTH//2 - info2_surf.get_width()//2, INFO_Y))
                                draw_counters()
                                pygame.display.flip()
                                pygame.time.wait(600)
                                cap = remove_opponent_stone(ai_player)
                            else:
                                cap = False
                            moved = True
                            last_move_by[ai_player] = (i, j)
                            break
                    if moved:
                        break
            winner = check_win()
            current_player = 2 if current_player == 1 else 1
            update_draw_state(captured=cap)
            pygame.time.wait(500)
        else:
            # Mensch-Zug
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if confirm_abort():
                        return None
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_d:
                    toggle_debug_overlay()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_l:
                    toggle_language()
                    break
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_d:
                    toggle_debug_overlay()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos
                    if selected is None:
                        for idx, (x, y) in enumerate(positions):
                            if (mx-x)**2 + (my-y)**2 < HIT_R**2 and state[idx] in (1,2):
                                if (current_player == 1 and state[idx] == 1) or (current_player == 2 and state[idx] == 2):
                                    selected = idx
                                    break
                    else:
                        stones = [i for i, v in enumerate(state) if v == current_player]
                        if len(stones) == 3:
                            moved_now = False
                            for idx, (x, y) in enumerate(positions):
                                if (mx-x)**2 + (my-y)**2 < HIT_R**2 and state[idx] == 0:
                                    if ruleset == "Turnier" and last_move_by.get(current_player) == (idx, selected):
                                        continue
                                    from_pos = selected
                                    state[selected] = 0
                                    state[idx] = current_player
                                    muehle_gebildet = check_muehle(idx, current_player)
                                    if muehle_gebildet:
                                        screen.fill((240, 220, 180))
                                        for a, b in lines:
                                            pygame.draw.line(screen, (120, 100, 80), positions[a], positions[b], 5)
                                        for idx2, (x2, y2) in enumerate(positions):
                                            color = (200, 180, 120)
                                            if state[idx2] == 1:
                                                color = (255, 255, 255)
                                            elif state[idx2] == 2:
                                                color = (0, 0, 0)
                                            rad = PIECE_R if state[idx2] else NODE_R
                                            pygame.draw.circle(screen, color, (x2, y2), rad, 0 if state[idx2] else 3)
                                        info2 = f"{label_for(current_player)} entfernt einen Stein"
                                        info2_surf = render_fit_text(info2, (200,40,40), max_width=WIDTH-100, base_size=28, min_size=18)
                                        screen.blit(info2_surf, (WIDTH//2 - info2_surf.get_width()//2, INFO_Y))
                                        draw_counters()
                                        pygame.display.flip()
                                        cap = remove_opponent_stone(current_player)
                                        if aborted:
                                            return None
                                    else:
                                        cap = False
                                    last_move_by[current_player] = (from_pos, idx)
                                    selected = None
                                    winner = check_win()
                                    current_player = 2 if current_player == 1 else 1
                                    update_draw_state(captured=cap)
                                    moved_now = True
                                    break
                            if not moved_now:
                                for idx, (x, y) in enumerate(positions):
                                    if (mx-x)**2 + (my-y)**2 < HIT_R**2 and state[idx] == current_player:
                                        selected = None if idx == selected else idx
                                        break
                        else:
                            adj = get_adjacent(selected)
                            moved_now = False
                            for idx in adj:
                                x, y = positions[idx]
                                if (mx-x)**2 + (my-y)**2 < HIT_R**2 and state[idx] == 0:
                                    if ruleset == "Turnier" and last_move_by.get(current_player) == (idx, selected):
                                        continue
                                    from_pos = selected
                                    state[selected] = 0
                                    state[idx] = current_player
                                    muehle_gebildet = check_muehle(idx, current_player)
                                    if muehle_gebildet:
                                        screen.fill((240, 220, 180))
                                        for a, b in lines:
                                            pygame.draw.line(screen, (120, 100, 80), positions[a], positions[b], 5)
                                        for idx2, (x2, y2) in enumerate(positions):
                                            color = (200, 180, 120)
                                            if state[idx2] == 1:
                                                color = (255, 255, 255)
                                            elif state[idx2] == 2:
                                                color = (0, 0, 0)
                                            rad = PIECE_R if state[idx2] else NODE_R
                                            pygame.draw.circle(screen, color, (x2, y2), rad, 0 if state[idx2] else 3)
                                        info2 = f"{label_for(current_player)} entfernt einen Stein"
                                        info2_surf = render_fit_text(info2, (200,40,40), max_width=WIDTH-100, base_size=28, min_size=18)
                                        screen.blit(info2_surf, (WIDTH//2 - info2_surf.get_width()//2, INFO_Y))
                                        draw_counters()
                                        pygame.display.flip()
                                        cap = remove_opponent_stone(current_player)
                                        if aborted:
                                            return None
                                    else:
                                        cap = False
                                    last_move_by[current_player] = (from_pos, idx)
                                    selected = None
                                    winner = check_win()
                                    current_player = 2 if current_player == 1 else 1
                                    update_draw_state(captured=cap)
                                    moved_now = True
                                    break
                            if not moved_now:
                                for idx, (x, y) in enumerate(positions):
                                    if (mx-x)**2 + (my-y)**2 < HIT_R**2 and state[idx] == current_player:
                                        selected = None if idx == selected else idx
                                        break
        # note: event loop ended – next frame / 
        # Hinweis: Event-Loop beendet – nächster Frame
        clock.tick(FPS)
    if 'winner' in locals():
        return winner
    return None

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Nine Men's Morris / Mühle")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("FreeSans", FONT_SIZE)
    selected_idx = 0
    running = True
    while running:
        draw_menu(screen, font, selected_idx)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.MOUSEMOTION:
                item = get_menu_item_at_pos(event.pos, font)
                if item is not None:
                    selected_idx = item
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_l:
                    toggle_language()
                    continue
                options_len = len(get_menu_options())
                if event.key == pygame.K_UP:
                    selected_idx = (selected_idx - 1) % options_len
                elif event.key == pygame.K_DOWN:
                    selected_idx = (selected_idx + 1) % options_len
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                    # Map aktuelle Optionsliste auf Aktionen
                    option = get_menu_options()[selected_idx]
                    if option.startswith("Mensch") or option.startswith("Human"):
                        diff = select_difficulty(screen, font, clock)
                        rules = select_ruleset(screen, font, clock) if diff else None
                        if diff and rules:
                            globals()["CURRENT_DIFFICULTY"] = diff
                            globals()["CURRENT_RULESET"] = rules
                            play_match_best_of_3(screen, font, clock)
                    elif option.startswith("Netzwerk") or option.startswith("Network"):
                        conn = run_network_menu(screen, font, clock)
                        if conn:
                            try:
                                # direct match mode (best of 3) /
                                # Direkt Matchmodus (Best of 3)
                                play_network_match_best_of_3(screen, font, clock, conn)
                            finally:
                                close_conn_state(conn)
                    elif option.startswith("Hilfe") or option.startswith("Help"):
                        show_help_menu(screen, font)
                    elif option.startswith("Sprache") or option.startswith("Language"):
                        toggle_language()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                item = get_menu_item_at_pos(event.pos, font)
                if item is not None:
                    selected_idx = item
                    # execute like Enter /
                    # Ausführen wie Enter
                    fake_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
                    pygame.event.post(fake_event)
        clock.tick(FPS)

def show_help_menu(screen, font):
    # helpersite scaled to window size and scrollable /
    # Hilfeseite skaliert an Fenstergröße und mit Scrollen
    screen.fill((30,30,30))
    ui_scale = max(0.6, min(WIDTH, HEIGHT) / 800.0)
    # sizes and spacings /
    # Größen und Abstände
    title_size = max(28, int(50 * ui_scale))
    help_size = max(16, int(28 * ui_scale))
    cont_size = max(14, int(24 * ui_scale))
    top_y = int(60 * ui_scale)
    left_margin = int(60 * ui_scale)
    view_top = int(150 * ui_scale)
    view_bottom = HEIGHT - int(90 * ui_scale)
    view_height = max(0, view_bottom - view_top)

    title = "Hilfe / Steuerung"
    title_surf = render_fit_text(title, (255,255,255), max_width=WIDTH-60, base_size=title_size, min_size=22)
    screen.blit(title_surf, (WIDTH//2 - title_surf.get_width()//2, top_y))

    if CURRENT_LANG == "de":
        sl_explain = [
            "SL = Skript Logic ersetzt die Ausdrücke KI",
            " - SL nutzt eine einfache Spiellogik in 3 Schwierigkeitsstufen.",
            ""
        ]
    elif CURRENT_LANG == "en":
        sl_explain = [
            "SL = Script Logic replaces the terms AI",
            " - SL uses a simple game logic with 3 difficulty levels.",         
            ""
        ]
    elif CURRENT_LANG == "fr":
        sl_explain = [
            "SL = Script Logic remplace les termes IA",
            " - SL utilise une logique de jeu simple en 3 niveaux de difficulté.",
            ""
        ]
    else:  # es
        sl_explain = [
            "SL = Script Logic reemplaza los términos IA",
            " - SL usa una lógica de juego sencilla con 3 niveles de dificultad.",
            ""
        ]

    if CURRENT_LANG == "fr":
        help_lines = [
            "Navigation du menu:",
            "  ↑ / ↓ : Changer la sélection",
            "  Entrée / Espace : Valider la sélection",
            "  ESC : Retour / Annuler",
            "  Souris : Cliquer sur une option du menu",
            "",
            *sl_explain,
            "En jeu:",
            "  ESC : Abandon / retour au menu",
            "  Souris : Placer et déplacer les pierres",
            "  ESPACE : Lancer et continuer (si indiqué)",
            "",
            "Menu réseau:",
            "  Host/Client/IP/Port/Bind sélection avec ↑/↓ et Entrée",
            "  IP/Port modifiables via dialogue",
            "  Connecter démarre la partie réseau",
            "",
            "Jeux de règles:",
            " Allégé:",
            "  - Règles classiques sans logique de nulles supplémentaire",
            "  - Pas d'anti-va-et-vient, pas de triple répétition,",
            "    pas de nulle 100 demi-coups",
            "",
            " Tournoi:",
            "  - Anti-va-et-vient : retour immédiat avec la même",
            "    pierre interdit",
            "  - Triple répétition de la même position (même",
            "    droit de jouer) = nulle",
            "  - 100 demi-coups sans capture = nulle",
        ]
    elif CURRENT_LANG == "es":
        help_lines = [
            "Navegación del menú:",
            "  ↑ / ↓ : Cambiar selección",
            "  Enter / Espacio : Confirmar selección",
            "  ESC : Volver / Cancelar",
            "  Ratón: Clic en opción del menú",
            "",
            *sl_explain,
            "En el juego:",
            "  ESC : Abortar / volver al menú",
            "  Ratón: Colocar y mover fichas",
            "  ESPACIO : Tirar y continuar (donde se indique)",
            "",
            "Menú de red:",
            "  Host/Cliente/IP/Puerto/Bind con ↑/↓ y Enter",
            "  IP/Puerto se pueden cambiar por diálogo",
            "  Conectar inicia la partida en red",
            "",
            "Conjuntos de reglas:",
            " Suavizado:",
            "  - Reglas clásicas sin lógica extra de tablas",
            "  - Sin anti-péndulo, sin triple repetición,",
            "    sin tablas por 100 medios-movimientos",
            "",
            " Torneo:",
            "  - Anti-péndulo: volver inmediatamente con la misma",
            "    ficha prohibido",
            "  - Triple repetición de la misma posición (mismo",
            "    derecho a mover) = tablas",
            "  - 100 medios-movimientos sin captura = tablas",
        ]
    else:
        help_lines = [
            "Menü-Navigation:",
            "  ↑ / ↓ : Auswahl wechseln",
            "  Enter / Leertaste : Auswahl bestätigen",          
            "  ESC : Zurück / Abbrechen",
            "  Maus: Klick auf Menüoption wählt diese aus",
            "",
            *sl_explain,
            "Im Spiel:",
            "  ESC : Spiel abbrechen / zurück zum Menü",
            "  Maus: Steine setzen und ziehen",
            "  SPACE : Würfeln und fortfahren (wo angezeigt)",
            "",
            "Netzwerk-Menü:",
            "  Host/Client/IP/Port/Bind auswählbar mit ↑/↓ und Enter",
            "  IP/Port kann per Dialog geändert werden",
            "  Verbinden startet das Netzwerkspiel",
            "",
            "Regelsets:",
            " Entschärft:",
            "  - Klassische Regeln ohne zusätzliche Remis-/Sperrlogik",
            "  - Kein Anti-Pendeln, keine 3-fach-Wiederholung,",
            "    kein 100-Halbzüge-Remis",
            "",
            " Turnier:",
            "  - Anti-Pendeln: Sofortiges Zurückziehen desselben",
            "    Steins ist verboten",
            "  - 3-fach-Wiederholung derselben Stellung (mit gleichem",
            "    Zugrecht) = Remis",
            "  - 100 Halbzüge ohne Schlagfall = Remis",
        ]
    # pre-render the content with width fitting /
    # Pre-Render der Inhalte mit Breitenanpassung
    line_surfs = [
        render_fit_text(line, (220,220,220), max_width=WIDTH - 2*left_margin, base_size=help_size, min_size=14)
        for line in help_lines
    ]
    line_heights = [surf.get_height() + int(6 * ui_scale) for surf in line_surfs]
    content_height = sum(line_heights)
    scroll = 0
    clock = pygame.time.Clock()
    running = True
    while running:
        screen.fill((30,30,30))
        # Titel
        title_surf = render_fit_text(title, (255,255,255), max_width=WIDTH-60, base_size=title_size, min_size=22)
        screen.blit(title_surf, (WIDTH//2 - title_surf.get_width()//2, top_y))
        # clip area for scroll text /
        # Clip-Bereich für Scroll-Text
        screen.set_clip(pygame.Rect(0, view_top, WIDTH, view_height))
        y = view_top - scroll
        for surf, h in zip(line_surfs, line_heights):
            if y + surf.get_height() >= view_top - 5 and y <= view_top + view_height + 5:
                screen.blit(surf, (left_margin, y))
            y += h
        screen.set_clip(None)
        # Scrollbar (optional)
        if content_height > view_height:
            bar_x = WIDTH - int(20 * ui_scale)
            bar_y = view_top
            bar_w = max(6, int(8 * ui_scale))
            bar_h = view_height
            radius = max(2, int(4 * ui_scale))
            pygame.draw.rect(screen, (70,70,70), (bar_x, bar_y, bar_w, bar_h), border_radius=radius)
            knob_h = int(max(24 * ui_scale, bar_h * (view_height / max(1, content_height))))
            max_scroll = max(1, content_height - view_height)
            knob_y = bar_y + int((scroll / max_scroll) * (bar_h - knob_h))
            pygame.draw.rect(screen, (180,180,180), (bar_x, knob_y, bar_w, knob_h), border_radius=radius)
        # esc note outside viewport (localized) /
        # ESC-Hinweis außerhalb des Viewports (lokalisiert)
        if CURRENT_LANG == "de":
            cont = "Drücke ESC um zurückzukehren"
        elif CURRENT_LANG == "en":
            cont = "Press ESC to return"
        elif CURRENT_LANG == "fr":
            cont = "Appuyez sur ESC pour revenir"
        else:  # es
            cont = "Pulsa ESC para volver"
        cont_surf = render_fit_text(cont, (200,200,100), max_width=WIDTH-60, base_size=cont_size, min_size=14)
        screen.blit(cont_surf, (WIDTH//2 - cont_surf.get_width()//2, HEIGHT - int(60 * ui_scale)))
        pygame.display.flip()
        # input handling /
        # Eingaben
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_UP:
                    scroll -= int(20 * ui_scale)
                elif event.key == pygame.K_DOWN:
                    scroll += int(20 * ui_scale)
                elif event.key == pygame.K_PAGEUP:
                    scroll -= int(view_height * 0.8)
                elif event.key == pygame.K_PAGEDOWN:
                    scroll += int(view_height * 0.8)
                elif event.key == pygame.K_HOME:
                    scroll = 0
                elif event.key == pygame.K_END:
                    scroll = content_height - view_height
            elif event.type == pygame.MOUSEWHEEL:
                scroll -= event.y * int(40 * ui_scale)
        # Clamp Scroll
        max_scroll = max(0, content_height - view_height)
        if scroll < 0:
            scroll = 0
        elif scroll > max_scroll:
            scroll = max_scroll
        clock.tick(FPS)

def draw_network_menu(screen, font, mode, ip, port, selected_idx, bind_mode="local"):
    screen.fill((30,30,30))
    title_surf = render_fit_text("Netzwerkspiel", (255,255,255), max_width=WIDTH-60, base_size=54, min_size=28)
    screen.blit(title_surf, (WIDTH//2 - title_surf.get_width()//2, 60))
    options = [
        ("Host", mode=="host"),
        ("Client", mode=="client"),
        (f"IP: {ip}", False),
        (f"Port: {port}", False),
        ("Bind: Lokal" if bind_mode=="local" else "Bind: LAN", False),
        ("Verbinden", False),
    ]
    base_y = 130
    spacing = 60
    for i, (text, active) in enumerate(options):
        x = WIDTH//2
        y = base_y + i*spacing
        # mode highlight as background capsule /
        # Modus-Highlight als hinterlegte Kapsel
        if (i == 0 and mode=="host") or (i==1 and mode=="client"):
            bg = pygame.Surface((int(WIDTH*0.7), 48), pygame.SRCALPHA)
            bg.fill((70,70,120,90) if i==0 else (120,100,60,90))
            screen.blit(bg, (WIDTH//2 - bg.get_width()//2, y-6))
        color = (0,220,0) if i == selected_idx else (255,255,255)
        text_surf = render_fit_text(text, color, max_width=WIDTH-100, base_size=FONT_SIZE)
        screen.blit(text_surf, (x - text_surf.get_width()//2, y))

def run_network_menu(screen, font, clock):
    # easy host/client selection with IP/Port and connect /
    # Einfache Host/Client-Auswahl mit IP/Port und Verbinden
    mode = "host"
    ip = DEFAULT_IP
    port = DEFAULT_PORT
    bind_mode = "local"
    sel = 0
    while True:
        draw_network_menu(screen, font, mode, ip, port, sel, bind_mode)
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    return None
                elif e.key == pygame.K_UP:
                    sel = (sel - 1) % 6
                elif e.key == pygame.K_DOWN:
                    sel = (sel + 1) % 6
                elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if sel == 0:
                        mode = "host"
                    elif sel == 1:
                        mode = "client"
                    elif sel == 2:
                        val = pygame_text_input(screen, font, tr("IP:"), ip)
                        if val:
                            ip = val
                    elif sel == 3:
                        val = pygame_text_input(screen, font, tr("Port:"), str(port), numeric=True)
                        if val:
                            try:
                                port = int(val)
                            except Exception:
                                pass
                    elif sel == 4:
                        bind_mode = "lan" if bind_mode == "local" else "local"
                    elif sel == 5:
                        # connect
                        # Verbinden
                        conn = start_network_connection(mode, ip, port, bind_mode)
                        if not conn:
                            # error message briefly shown / 
                            # Fehlermeldung kurz einblenden
                            screen.fill((30,30,30))
                            msg = render_fit_text("Verbindung fehlgeschlagen", (220,150,120), max_width=WIDTH-80, base_size=36, min_size=18)
                            screen.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2 - msg.get_height()//2))
                            pygame.display.flip(); pygame.time.wait(900)
                        else:
                            # host waits for client /
                            # Host wartet auf Client
                            if mode == "host":
                                waiting = True
                                buffer = ""
                                while waiting:
                                    draw_network_menu(screen, font, mode, ip, port, sel, bind_mode)
                                    hint = render_fit_text(f"{tr('Warte auf Client')}... {tr('ESC zum Abbrechen')}", (200,200,160), max_width=WIDTH-80, base_size=24, min_size=14)
                                    screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 80))
                                    pygame.display.flip()
                                    if accept_network_client(conn, screen, font):
                                        waiting = False
                                        break
                                    for ev in pygame.event.get():
                                        if ev.type == pygame.QUIT:
                                            pygame.quit(); sys.exit()
                                        elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                                            close_conn_state(conn)
                                            return None
                                    clock.tick(FPS)
                                # dice roll, ruleset selection, start color / 
                                # Würfeln, Regelset wählen und Startfarbe festlegen
                                h, c, host_starts = network_wuerfeln_host(screen, font, clock)
                                # ruleset selection (host decides) /
                                # Regelset-Auswahl (Host bestimmt)
                                chosen = select_ruleset(screen, font, clock)
                                if not chosen:
                                    close_conn_state(conn)
                                    return None
                                sock = conn["socket"]
                                try:
                                    # ordering: ROLL -> RULES -> START /
                                    # Reihenfolge: ROLL -> RULES -> START
                                    sock.sendall(f"ROLL {h} {c}\n".encode())
                                    rules_key = "RELAXED" if chosen.startswith("Ent") or chosen.lower().startswith("relax") else "TOURNAMENT"
                                    sock.sendall(f"RULES {rules_key}\n".encode())
                                    if host_starts:
                                        conn["color"] = 1
                                        sock.sendall(b"START WHITE\n")
                                    else:
                                        conn["color"] = 2
                                        sock.sendall(b"START BLACK\n")
                                except Exception:
                                    close_conn_state(conn)
                                    return None
                                conn["buffer"] = ""
                                conn["ruleset"] = "Entschärft" if rules_key == "RELAXED" else "Turnier"
                                return conn
                            else:
                                # client: wait for ROLL/START /
                                # Client: warte auf ROLL/START
                                sock = conn["socket"]
                                buffer = ""
                                du_roll = None; gegner_roll = None; du_beginnt = None
                                rules_key = None
                                waiting = True
                                while waiting:
                                    draw_network_menu(screen, font, mode, ip, port, sel, bind_mode)
                                    hint = render_fit_text(f"{tr('Verbunden – warte auf Start')}... {tr('ESC zum Abbrechen')}", (200,200,160), max_width=WIDTH-80, base_size=24, min_size=14)
                                    screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 80))
                                    pygame.display.flip()
                                    lines_in, buffer, closed = network_receive_lines(sock, buffer)
                                    if closed:
                                        close_conn_state(conn)
                                        return None
                                    for line in lines_in:
                                        parts = line.split()
                                        if parts and parts[0] == "ROLL" and len(parts) >= 3:
                                            try:
                                                gegner_roll = int(parts[1])
                                                du_roll = int(parts[2])
                                            except Exception:
                                                pass
                                        elif parts and parts[0] == "RULES" and len(parts) >= 2:
                                            rules_key = parts[1].upper()
                                        elif parts and parts[0] == "START" and len(parts) >= 2:
                                            if parts[1].upper() == "WHITE":
                                                conn["color"] = 2  # Host ist Weiß, Client ist Schwarz
                                                du_beginnt = False
                                            else:
                                                conn["color"] = 1
                                                du_beginnt = True
                                            waiting = False
                                            break
                                    for ev in pygame.event.get():
                                        if ev.type == pygame.QUIT:
                                            pygame.quit(); sys.exit()
                                        elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                                            close_conn_state(conn)
                                            return None
                                    clock.tick(FPS)
                                # result show /
                                # Ergebnis zeigen
                                if du_roll is not None and gegner_roll is not None and du_beginnt is not None:
                                    network_show_wuerfel_result(screen, font, clock, du_roll, gegner_roll, du_beginnt)
                                conn["buffer"] = buffer
                                conn["ruleset"] = ("Entschärft" if (rules_key or "RELAXED").upper().startswith("RELAX") else "Turnier")
                                return conn
            elif e.type == pygame.MOUSEMOTION:
                mx, my = e.pos
                base_y = 130
                spacing = 60
                for i in range(6):
                    y = base_y + i*spacing
                    rect = pygame.Rect(WIDTH//2 - int(WIDTH*0.35), y-10, int(WIDTH*0.7), 48)
                    if rect.collidepoint(mx, my):
                        sel = i
                        break
            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                mx, my = e.pos
                # click selects option and triggers Enter /
                # rough hitbox over all options /
                # Klicken wählt die Option und löst Enter aus
                # Grobe Hitbox über alle Optionen
                base_y = 130
                spacing = 60
                for i in range(6):
                    y = base_y + i*spacing
                    rect = pygame.Rect(WIDTH//2 - int(WIDTH*0.35), y-10, int(WIDTH*0.7), 48)
                    if rect.collidepoint(mx, my):
                        sel = i
                        fake = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
                        pygame.event.post(fake)
                        break
        clock.tick(FPS)

def network_game_simple(screen, font, clock, conn_state):
    # network game: 2 humans over TCP, 1 match /
    # Netzwerkspiel: 2 Menschen über TCP, 1 Partie
    sock = conn_state.get("socket")
    buffer = conn_state.get("buffer", "")
    local_color = conn_state.get("color", 1)  # 1=white, 2=black / 1=Weiß, 2=Schwarz
    ruleset = conn_state.get("ruleset", "Entschärft")
    is_tournament = str(ruleset).lower().startswith("turn") or str(ruleset).lower().startswith("tourn")
    is_match = bool(conn_state.get('match'))
    # board setup (like singleplayer) /
    # Board-Setup (wie Singleplayer)
    ui_scale = max(0.6, min(WIDTH, HEIGHT) / 800.0)
    # infoline 15px higher (not moving the top storage) /
    # Infozeile 15px weiter nach oben (nicht das obere Lager verschieben)
    INFO_Y = max(20, int(36 * ui_scale) - 25)
    COUNTER_MARGIN = int(40 * ui_scale)
    COUNTER_R = max(6, int(16 * ui_scale))
    COUNTER_Y_TOP = min(max(INFO_Y + 40, int(90 * ui_scale) - 20) + 20, HEIGHT - 100)
    COUNTER_Y_BOT = max(min(HEIGHT - 20, HEIGHT - int(90 * ui_scale) + 50) - 20, COUNTER_Y_TOP + 100)
    top_free = COUNTER_Y_TOP + COUNTER_R + int(20 * ui_scale)
    bottom_free = COUNTER_Y_BOT - COUNTER_R - int(20 * ui_scale)
    margin_x = int(40 * ui_scale)
    board_scale = min(ui_scale, max(0.5, (WIDTH - 2.0 * margin_x) / (2.0 * 260)), max(0.5, (bottom_free - top_free) / (2.0 * 260)))
    NODE_R = max(8, int(16 * board_scale))
    PIECE_R = max(12, int(24 * board_scale))
    HIT_R = max(14, int(27 * board_scale))
    LINE_W = max(2, int(5 * board_scale))
    cx = WIDTH // 2
    cy = int((top_free + bottom_free) // 2)
    compact = 0.9
    outer = int(260 * compact * board_scale)
    mid = int(180 * compact * board_scale)
    inner = int(100 * compact * board_scale)
    positions = [
        (cx-outer, cy-outer), (cx, cy-outer), (cx+outer, cy-outer),
        (cx+outer, cy), (cx+outer, cy+outer), (cx, cy+outer), (cx-outer, cy+outer), (cx-outer, cy),
        (cx-mid, cy-mid), (cx, cy-mid), (cx+mid, cy-mid),
        (cx+mid, cy), (cx+mid, cy+mid), (cx, cy+mid), (cx-mid, cy+mid), (cx-mid, cy),
        (cx-inner, cy-inner), (cx, cy-inner), (cx+inner, cy-inner),
        (cx+inner, cy), (cx+inner, cy+inner), (cx, cy+inner), (cx-inner, cy+inner), (cx-inner, cy)
    ]
    lines = [
        (0,1),(1,2),(2,3),(3,4),(4,5),(5,6),(6,7),(7,0),
        (8,9),(9,10),(10,11),(11,12),(12,13),(13,14),(14,15),(15,8),
        (16,17),(17,18),(18,19),(19,20),(20,21),(21,22),(22,23),(23,16),
        (1,9),(3,11),(5,13),(7,15),
        (9,17),(11,19),(13,21),(15,23)
    ]
    muhlen = [
        [0,1,2], [2,3,4], [4,5,6], [6,7,0],
        [8,9,10], [10,11,12], [12,13,14], [14,15,8],
        [16,17,18], [18,19,20], [20,21,22], [22,23,16],
        [1,9,17], [3,11,19], [5,13,21], [7,15,23]
    ]
    state = [0]*24
    stones_set = [0,0]
    last_mills = {1:set(), 2:set()}
    current_player = 1
    selected = None
    # anti pendulum: last moves per player (from,to) /
    # Anti-Pendeln: letzte Züge je Spieler (from,to)
    last_move_by_player = {1: (-1, -1), 2: (-1, -1)}
    # tounament remis: track repetitions and halfmove counter (only in moving phase) /
    # Turnier-Remis: Wiederholungen + Halbzugzähler (nur in Zugphase)
    rep_counts = {}
    halfmove_count = 0
    def draw_board(info_text=None):
        screen.fill((240, 220, 180))
        for a,b in lines:
            pygame.draw.line(screen, (120,100,80), positions[a], positions[b], LINE_W)
        for idx,(x,y) in enumerate(positions):
            color = (200,180,120)
            if state[idx]==1: color=(255,255,255)
            elif state[idx]==2: color=(0,0,0)
            if selected == idx:
                pygame.draw.circle(screen, (0,220,0), (x,y), max(PIECE_R+6, int(28*board_scale)), 3)
            pygame.draw.circle(screen, color, (x,y), PIECE_R if state[idx] else NODE_R, 0 if state[idx] else 3)
            # anti pendulum: mark only the forbidden retreat target red /
            # if the last moved own piece is currently selected /
            # Anti-Pendeln: markiere nur das verbotene Rückzugs-Zielfeld rot,
            # wenn der zuletzt gezogene eigene Stein aktuell ausgewählt ist
            if is_tournament and selected is not None:
                mv = last_move_by_player.get(current_player, (-1, -1))  # (from, to)
                if selected == mv[1] and idx == mv[0]:
                    pygame.draw.circle(screen, (220,40,40), (x, y), max(PIECE_R+6, int(28*board_scale)), 2)
        # reserve stones as storage rows - fixed 50px margins, 9 slots, nothing moves /
        # Reserve-Steine als Speicherreihen – feste 50px Ränder, 9 Slots, nichts verschiebt sich
        white_left = max(0, 9 - stones_set[0])
        black_left = max(0, 9 - stones_set[1])
        rr = PIECE_R
        left_margin, right_margin = 50, 50
        steps = 8  # 9 slots -> 8 gaps / 9 Slots -> 8 Abstände
        width_avail = max(2, WIDTH - left_margin - right_margin)
        spacing = width_avail / steps  # float für exakte Randtreue
        start_x = left_margin
        # top: first placeholders, then white stones on fixed slots /
        # oben: erst Platzhalter, dann weiße Steine auf festen Slots
        y_top = COUNTER_Y_TOP
        for i in range(9):
            x = int(round(start_x + i*spacing))
            pygame.draw.circle(screen, (185,180,160), (x, y_top), rr, 0)
            pygame.draw.circle(screen, (140,130,110), (x, y_top), rr, 1)
        for i in range(white_left):
            x = int(round(start_x + i*spacing))
            pygame.draw.circle(screen, (255,255,255), (x, y_top), rr, 0)
            pygame.draw.circle(screen, (100, 90, 70), (x, y_top), rr, 2)
        # bottom: first placeholders, then black stones on fixed slots /
        # unten: erst Platzhalter, dann schwarze Steine auf festen Slots
        y_bot = COUNTER_Y_BOT
        for i in range(9):
            x = int(round(start_x + i*spacing))
            pygame.draw.circle(screen, (185,180,160), (x, y_bot), rr, 0)
            pygame.draw.circle(screen, (140,130,110), (x, y_bot), rr, 1)
        for i in range(black_left):
            x = int(round(start_x + i*spacing))
            pygame.draw.circle(screen, (0,0,0), (x, y_bot), rr, 0)
            pygame.draw.circle(screen, (100, 90, 70), (x, y_bot), rr, 2)
        # tournament overlay: left white (player 1), right black (player 2) /
        # Turnier-Overlay: links Weiß (Spieler 1), rechts Schwarz (Spieler 2)
        if is_tournament and not setzphase:
            rep_w = rep_counts.get((tuple(state), 1), 0)
            rep_s = rep_counts.get((tuple(state), 2), 0)
            col_inactive = (80,60,40)
            col_active = (200,140,60)
            mid_y = HEIGHT//2
            color_w = col_active if current_player==1 else col_inactive
            color_s = col_active if current_player==2 else col_inactive
            left_x = 12
            right_x = WIDTH - 12
            label_w = render_fit_text(tr("Weiß (Spieler 1)"), color_w, max_width=160, base_size=16, min_size=12)
            rep_w_surf = render_fit_text(f"{tr('Rep:')} {rep_w}/3", color_w, max_width=160, base_size=16, min_size=12)
            hz_w_surf = render_fit_text(f"{tr('HZ:')} {halfmove_count}", color_w, max_width=160, base_size=16, min_size=12)
            screen.blit(label_w, (left_x, mid_y - 28))
            screen.blit(rep_w_surf, (left_x, mid_y - 8))
            screen.blit(hz_w_surf, (left_x, mid_y + 10))
            label_s = render_fit_text(tr("Schwarz (Spieler 2)"), color_s, max_width=160, base_size=16, min_size=12)
            rep_s_surf = render_fit_text(f"{tr('Rep:')} {rep_s}/3", color_s, max_width=160, base_size=16, min_size=12)
            hz_s_surf = render_fit_text(f"{tr('HZ:')} {halfmove_count}", color_s, max_width=160, base_size=16, min_size=12)
            screen.blit(label_s, (right_x - label_s.get_width(), mid_y - 28))
            screen.blit(rep_s_surf, (right_x - rep_s_surf.get_width(), mid_y - 8))
            screen.blit(hz_s_surf, (right_x - hz_s_surf.get_width(), mid_y + 10))
        # easy info line if not given /
        # einfache Infozeile
        if info_text is None:
            who = tr("Weiß") if current_player==1 else tr("Schwarz")
            # localized YOU/DU /
            # Lokalisiertes YOU/DU
            you = tr(" (DU)") if current_player==local_color else ""
            if setzphase:
                phase = tr("Setzphase:")
                action = tr("setzt Stein ")
                count = f"({stones_set[current_player-1]+1}/9)" if stones_set[current_player-1] < 9 else "(9/9)"
                info_text = f"{phase} {who}{you} {action}{count}"
            else:
                phase = tr("Zugphase:")
                action = tr("bewegt einen Stein")
                info_text = f"{phase} {who}{you} {action}"
        # safety: translate full line /
        # Sicherheit: Gesamtsatz übersetzen
        info_surf = render_fit_text(tr(info_text), (60,40,20), max_width=WIDTH-80, base_size=FONT_SIZE, min_size=16)
        screen.blit(info_surf, (WIDTH//2 - info_surf.get_width()//2, INFO_Y))
        pygame.display.flip()
    def update_mills(pos, player):
        cur = {i for i,m in enumerate(muhlen) if all(state[k]==player for k in m)}
        created = {i for i in cur if pos in muhlen[i]} - last_mills[player]
        last_mills[player] = cur
        return len(created)>0
    def get_adjacent(p):
        adj=[]
        for a,b in lines:
            if a==p: adj.append(b)
            elif b==p: adj.append(a)
        return adj
    def has_moves(player):
        stones = [i for i, v in enumerate(state) if v == player]
        lm_from, lm_to = last_move_by_player.get(player, (-1, -1))
        if len(stones) == 3:
            # flying: any free spot as target, except immediate return pendulum of same stone /
            # Fliegen: jedes freie Feld als Ziel, außer sofortiges Zurückpendeln desselben Steins
            freie = [i for i, v in enumerate(state) if v == 0]
            for s in stones:
                for t in freie:
                    if is_tournament and s == lm_to and t == lm_from:
                        continue
                    return True
            return False
        for s in stones:
            for j in get_adjacent(s):
                if state[j] != 0:
                    continue
                if is_tournament and s == lm_to and j == lm_from:
                    # anti pendulum: immediate return of same stone forbidden /
                    # Anti-Pendeln: gleicher Stein sofort zurück verboten
                    continue
                return True
        return False
    def check_win():
        if sum(1 for v in state if v==1)<3: return 2
        if sum(1 for v in state if v==2)<3: return 1
        if not has_moves(1): return 2
        if not has_moves(2): return 1
        return None
    def position_key():
        return (tuple(state), current_player)
    def wait_for_escape():
        waiting=True
        while waiting:
            for ev in pygame.event.get():
                if ev.type==pygame.QUIT:
                    pygame.quit(); sys.exit()
                elif ev.type==pygame.KEYDOWN and ev.key==pygame.K_ESCAPE:
                    waiting=False
            clock.tick(FPS)
    def update_repetition_and_draws(capture=False):
        nonlocal halfmove_count
        if setzphase:
            return False
        if capture:
            halfmove_count = 0
        else:
            halfmove_count += 1
        key = position_key()
        rep_counts[key] = rep_counts.get(key, 0) + 1
        if is_tournament and (rep_counts[key] >= 3 or halfmove_count >= 100):
            # tournament ending signal draw; actual display/query takes place centrally /
            # Turnierende durch Remis signalisieren; eigentliche Anzeige/Abfrage erfolgt zentral
            return True
        return False
    def prompt_end_and_return(win_color=None, is_draw=False):
        """Zeige Abschluss-Overlay und liefere Rückgabewert:
        - win_color in {1,2} für Sieger
        - is_draw=True für Remis
        - ESC im Match => None (Abbruch), SPACE => weiter (1/2/0)
        - außerhalb Match: ESC schließt, Rückgabe (1/2/0)
        """
        if not is_draw:
            # existing final rendering (show last frame), then prompt /
            # Bestehendes finales Rendern (letzten Frame zeigen), danach Prompt
            base_hint_y = 10
            base_info_y = 30
            y_hint = max(0, base_hint_y - 3)
            y_info = max(0, base_info_y - 8)
            screen.fill((240, 220, 180))
            for a,b in lines:
                pygame.draw.line(screen, (120,100,80), positions[a], positions[b], LINE_W)
            for idx,(x,y) in enumerate(positions):
                color = (200,180,120)
                if state[idx]==1: color=(255,255,255)
                elif state[idx]==2: color=(0,0,0)
                if selected == idx:
                    pygame.draw.circle(screen, (0,220,0), (x,y), max(PIECE_R+6, int(28*board_scale)), 3)
                pygame.draw.circle(screen, color, (x,y), PIECE_R if state[idx] else NODE_R, 0 if state[idx] else 3)
            # draw storage / 
            # Lager zeichnen
            white_left = max(0, 9 - stones_set[0]); black_left = max(0, 9 - stones_set[1])
            rr = PIECE_R; left_margin, right_margin = 50, 50; steps = 8
            width_avail = max(1, WIDTH - left_margin - right_margin)
            spacing = width_avail / steps; start_x = left_margin
            y_top = COUNTER_Y_TOP; y_bot = COUNTER_Y_BOT
            for i in range(9):
                x = int(round(start_x + i*spacing))
                pygame.draw.circle(screen, (185,180,160), (x, y_top), rr, 0)
                pygame.draw.circle(screen, (140,130,110), (x, y_top), rr, 1)
            for i in range(white_left):
                x = int(round(start_x + i*spacing))
                pygame.draw.circle(screen, (255,255,255), (x, y_top), rr, 0)
                pygame.draw.circle(screen, (100,90,70), (x, y_top), rr, 2)
            for i in range(9):
                x = int(round(start_x + i*spacing))
                pygame.draw.circle(screen, (185,180,160), (x, y_bot), rr, 0)
                pygame.draw.circle(screen, (140,130,110), (x, y_bot), rr, 1)
            for i in range(black_left):
                x = int(round(start_x + i*spacing))
                pygame.draw.circle(screen, (0,0,0), (x, y_bot), rr, 0)
                pygame.draw.circle(screen, (100,90,70), (x, y_bot), rr, 2)
            # optimized note for tournament end /
            # Optionaler Hinweis bei Zugnot
            if is_tournament and win_color in (1,2):
                loser = 2 if win_color == 1 else 1
                stones_loser = sum(1 for v in state if v == loser)
                if stones_loser >= 3 and not has_moves(loser):
                    hint_surf = render_fit_text(tr("Keine legalen Züge"), (200,60,40), max_width=WIDTH-160, base_size=28, min_size=16)
                    screen.blit(hint_surf, (WIDTH//2 - hint_surf.get_width()//2, y_hint))
                    y_info = max(y_info, y_hint + hint_surf.get_height() + 5)
            end = (f"{tr('Spielende!')} {tr('Weiß') if win_color==1 else tr('Schwarz')} {tr('gewinnt!')} "
                   + (tr('(SPACE=Weiter, ESC=Abbruch)') if is_match else tr('(ESC für Menü)')))
            end_surf = render_fit_text(end, (60,40,20), max_width=WIDTH-160, base_size=36, min_size=18)
            screen.blit(end_surf, (WIDTH//2 - end_surf.get_width()//2, y_info))
            pygame.display.flip()
        else:
            # remis overlay: simple via info line /
            # Remis-Overlay simpel über Infozeile
            prompt = tr("Spielende! Remis nach Turnierregeln") + "  " + (tr('(SPACE=Weiter, ESC=Abbruch)') if is_match else tr('(ESC für Menü)'))
            draw_board(prompt)
            pygame.display.flip()
        # waiting for input /
        # Eingabe abwarten
        aborted = False
        waiting = True
        while waiting:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                elif ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_ESCAPE:
                        aborted = True; waiting = False
                    elif ev.key == pygame.K_SPACE and is_match:
                        waiting = False
            clock.tick(FPS)
        if aborted and is_match:
            return None
        return (0 if is_draw else win_color)
    # setting phase / 
    # Setzphase
    setzphase = True
    running = True
    while running:
        # process receive (non-blocking) /
        # Empfang verarbeiten (nicht-blockierend)
        lines_in, buffer, closed = network_receive_lines(sock, buffer)
        if closed:
            show_peer_left("Gegner")
            return None
        for line in lines_in:
            parts = line.split()
            if not parts: continue
            cmd = parts[0]
            if cmd == "SET" and setzphase:
                # supported: SET pos  or  SET player pos /
                # Unterstützt: SET pos  oder  SET player pos
                if len(parts) >= 3:
                    try:
                        pl = int(parts[1]); pos = int(parts[2])
                    except Exception:
                        pl = current_player; pos = int(parts[-1])
                else:
                    pl = current_player; pos = int(parts[1])
                if 0 <= pos < len(state) and state[pos]==0 and pl in (1,2):
                    state[pos] = pl
                    stones_set[pl-1]+=1
                    mill = update_mills(pos, pl)
                    if not mill:
                        current_player = 2 if pl==1 else 1
                        update_repetition_and_draws(capture=False)
                    if stones_set[0]==9 and stones_set[1]==9:
                        setzphase = False
            elif cmd == "REM":
                # supported: REM pos  or  REM player pos /
                # Unterstützt: REM pos  oder  REM player pos
                if len(parts) >= 3:
                    try:
                        _pl = int(parts[1]); pos = int(parts[2])
                    except Exception:
                        pos = int(parts[-1])
                else:
                    pos = int(parts[1])
                if 0 <= pos < len(state) and state[pos] in (1,2):
                    state[pos]=0
                # after removal, turn changes /
                # Nach Entfernen wechselt die Seite
                current_player = 2 if current_player==1 else 1
                update_repetition_and_draws(capture=True)
            elif cmd == "MOVE" and not setzphase:
                # supported: MOVE from to  or  MOVE player from to /
                # Unterstützt: MOVE from to  oder  MOVE player from to
                if len(parts) >= 4:
                    try:
                        pl = int(parts[1]); frm = int(parts[2]); to = int(parts[3])
                    except Exception:
                        pl = current_player; frm = int(parts[-2]); to = int(parts[-1])
                else:
                    pl = current_player; frm = int(parts[1]); to = int(parts[2])
                if 0 <= frm < len(state) and 0 <= to < len(state) and state[frm] == pl and state[to]==0:
                    state[frm]=0; state[to]=pl
                    mill = update_mills(to, pl)
                    if not mill:
                        last_move_by_player[pl] = (frm, to)
                        current_player = 2 if pl==1 else 1
                        if update_repetition_and_draws(capture=False):
                            return prompt_end_and_return(is_draw=True)
        # Render
        draw_board()
        # victory check only after setting phase /
        # Siegprüfung erst nach Setzphase
        if not setzphase:
            w = check_win()
            if w:
                return prompt_end_and_return(win_color=w, is_draw=False)
        # input only if it's our turn /
        # Eingaben nur, wenn wir am Zug sind
        if current_player == local_color:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                    if confirm_abort(tr("Netzwerkspiel wirklich beenden?")):
                        running=False; break
                elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_d:
                    toggle_debug_overlay()
                elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    mx, my = ev.pos
                    if setzphase:
                        if stones_set[current_player-1] < 9:
                            for idx,(x,y) in enumerate(positions):
                                if (mx-x)**2 + (my-y)**2 < HIT_R**2 and state[idx]==0:
                                    state[idx]=current_player
                                    stones_set[current_player-1]+=1
                                    mill = update_mills(idx, current_player)
                                    try:
                                        sock.sendall(f"SET {current_player} {idx}\n".encode())
                                    except Exception:
                                        running=False; break
                                    if mill:
                                        # select removal /
                                        # entfernen wählen
                                        removing=True
                                        while removing:
                                            draw_board(tr("Mühle! Wähle einen gegnerischen Stein zum Entfernen."))
                                            for ev2 in pygame.event.get():
                                                if ev2.type==pygame.QUIT:
                                                    pygame.quit(); sys.exit()
                                                elif ev2.type==pygame.KEYDOWN and ev2.key==pygame.K_ESCAPE:
                                                    if confirm_abort(tr("Netzwerkspiel wirklich beenden?")):
                                                        running=False; removing=False; break
                                                elif ev2.type==pygame.MOUSEBUTTONDOWN and ev2.button==1:
                                                    mx2,my2 = ev2.pos
                                                    opp = 2 if current_player==1 else 1
                                                    for oi,(ox,oy) in enumerate(positions):
                                                        if state[oi]==opp and (mx2-ox)**2+(my2-oy)**2 < HIT_R**2:
                                                            state[oi]=0
                                                            try:
                                                                sock.sendall(f"REM {current_player} {oi}\n".encode())
                                                            except Exception:
                                                                running=False
                                                            # when own removal done: turn to opponent /
                                                            # Nach eigenem Entfernen: Zug an den Gegner
                                                            current_player = 2 if current_player==1 else 1
                                                            removing=False
                                                            break
                                            clock.tick(FPS)
                                    else:
                                        current_player = 2 if current_player==1 else 1
                                    if stones_set[0]==9 and stones_set[1]==9:
                                        setzphase=False
                                    break
                    else:
                        stones_local = [i for i,v in enumerate(state) if v==current_player]
                        if selected is None:
                            for i,(x,y) in enumerate(positions):
                                if state[i]==current_player and (mx-x)**2+(my-y)**2 < HIT_R**2:
                                    selected = i; break
                        else:
                            targets = []
                            if len(stones_local)==3:
                                targets = [i for i,v in enumerate(state) if v==0]
                            else:
                                targets = [j for j in get_adjacent(selected) if state[j]==0]
                            for idx in targets:
                                x,y = positions[idx]
                                if (mx-x)**2 + (my-y)**2 < HIT_R**2:
                                    frm = selected; to = idx
                                    # tournament: check anti-pendulum immediate retreat /
                                    # Turnier: Anti-Pendeln – kein sofortiges Zurückziehen
                                    if is_tournament:
                                        stones_local_now = [i for i,v in enumerate(state) if v==current_player]
                                        if len(stones_local_now) > 3:
                                            lm = last_move_by_player.get(current_player)
                                            if (lm is not None) and lm == (to, frm):
                                                draw_board(tr("Anti-Pendeln: mit demselben Stein sofort zurück ist verboten"))
                                                pygame.time.wait(700)
                                                break
                                    state[frm]=0; state[to]=current_player
                                    mill = update_mills(to, current_player)
                                    try:
                                        sock.sendall(f"MOVE {current_player} {frm} {to}\n".encode())
                                    except Exception:
                                        running=False; break
                                    if mill:
                                        removing=True
                                        while removing:
                                            draw_board(tr("Mühle! Wähle einen gegnerischen Stein zum Entfernen."))
                                            for ev2 in pygame.event.get():
                                                if ev2.type==pygame.QUIT:
                                                    pygame.quit(); sys.exit()
                                                elif ev2.type==pygame.KEYDOWN and ev2.key==pygame.K_ESCAPE:
                                                    if confirm_abort(tr("Netzwerkspiel wirklich beenden?")):
                                                        running=False; removing=False; break
                                                elif ev2.type==pygame.MOUSEBUTTONDOWN and ev2.button==1:
                                                    mx2,my2 = ev2.pos
                                                    opp = 2 if current_player==1 else 1
                                                    for oi,(ox,oy) in enumerate(positions):
                                                        if state[oi]==opp and (mx2-ox)**2+(my2-oy)**2 < HIT_R**2:
                                                            state[oi]=0
                                                            try:
                                                                sock.sendall(f"REM {current_player} {oi}\n".encode())
                                                            except Exception:
                                                                running=False
                                                            # when own removal done: turn to opponent: draw tracker reset /
                                                            # Nach eigenem Entfernen: Zug an den Gegner; Draw-Tracker resetten
                                                            current_player = 2 if current_player==1 else 1
                                                            last_move_by_player[current_player] = last_move_by_player.get(current_player, (-1,-1))
                                                            if update_repetition_and_draws(capture=True):
                                                                return prompt_end_and_return(is_draw=True)
                                                            removing=False
                                                            break
                                            clock.tick(FPS)
                                    else:
                                        last_move_by_player[current_player] = (frm, to)
                                        current_player = 2 if current_player==1 else 1
                                        if update_repetition_and_draws(capture=False):
                                            return prompt_end_and_return(is_draw=True)
                                    selected = None
                                    break
                            # selection change / 
                            # Auswahl wechseln
                            for i,(x,y) in enumerate(positions):
                                if state[i]==current_player and (mx-x)**2+(my-y)**2 < HIT_R**2:
                                    selected = None if selected==i else i
                                    break
        else:
            # not our turn: show escape/quit reactions anyway /
            # Nicht am Zug: Trotzdem ESC/QUIT reagieren
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                    if confirm_abort(tr("Netzwerkspiel wirklich beenden?")):
                        running=False; break
                elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_d:
                    toggle_debug_overlay()
        clock.tick(FPS)

def select_difficulty(screen, font, clock):
    # easy selection Easy/Medium/Hard /
    # Einfache Auswahl Leicht/Mittel/Schwer
    idx = 0
    running = True
    title_font = pygame.font.SysFont("FreeSans", 54)
    while running:
        screen.fill((30,30,30))
        title_surf = render_fit_text("Spielstärke wählen", (255,255,255), max_width=WIDTH-60, base_size=54, min_size=24)
        screen.blit(title_surf, (WIDTH//2 - title_surf.get_width()//2, 60))
        option_surfs = []
        for i, opt in enumerate(DIFFICULTY_OPTIONS):
            color = (0,220,0) if i==idx else (220,220,220)
            surf = render_fit_text(opt, color, max_width=WIDTH-120, base_size=FONT_SIZE, min_size=18)
            option_surfs.append(surf)
            x = WIDTH//2 - surf.get_width()//2
            y = 180 + i*70
            screen.blit(surf, (x,y))
        hint = render_fit_text("↑/↓ wählen, Enter bestätigen, ESC abbrechen", (180,180,140), max_width=WIDTH-80, base_size=24, min_size=14)
        screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT-80))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                elif event.key == pygame.K_UP:
                    idx = (idx - 1) % len(DIFFICULTY_OPTIONS)
                elif event.key == pygame.K_DOWN:
                    idx = (idx + 1) % len(DIFFICULTY_OPTIONS)
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                    return DIFFICULTY_OPTIONS[idx]
            elif event.type == pygame.MOUSEMOTION:
                mx, my = event.pos
                for i, surf in enumerate(option_surfs):
                    x = WIDTH//2 - surf.get_width()//2
                    y = 180 + i*70
                    rect = pygame.Rect(x, y, surf.get_width(), surf.get_height())
                    if rect.collidepoint(mx, my):
                        idx = i
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                for i, surf in enumerate(option_surfs):
                    x = WIDTH//2 - surf.get_width()//2
                    y = 180 + i*70
                    rect = pygame.Rect(x, y, surf.get_width(), surf.get_height())
                    if rect.collidepoint(mx, my):
                        return DIFFICULTY_OPTIONS[i]
        clock.tick(FPS)

def select_ruleset(screen, font, clock):
    idx = 0
    title_font = pygame.font.SysFont("FreeSans", 54)
    while True:
        screen.fill((30,30,30))
        title_surf = render_fit_text("Regelset wählen", (255,255,255), max_width=WIDTH-60, base_size=54, min_size=24)
        screen.blit(title_surf, (WIDTH//2 - title_surf.get_width()//2, 60))
        option_surfs = []
        for i, opt in enumerate(RULESET_OPTIONS):
            color = (0,220,0) if i==idx else (220,220,220)
            surf = render_fit_text(opt, color, max_width=WIDTH-120, base_size=FONT_SIZE, min_size=18)
            option_surfs.append(surf)
            x = WIDTH//2 - surf.get_width()//2
            y = 180 + i*70
            screen.blit(surf, (x,y))
        hint = render_fit_text("↑/↓ wählen, Enter bestätigen, ESC abbrechen", (180,180,140), max_width=WIDTH-80, base_size=24, min_size=14)
        screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT-80))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                elif event.key == pygame.K_UP:
                    idx = (idx - 1) % len(RULESET_OPTIONS)
                elif event.key == pygame.K_DOWN:
                    idx = (idx + 1) % len(RULESET_OPTIONS)
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                    return RULESET_OPTIONS[idx]
            elif event.type == pygame.MOUSEMOTION:
                mx, my = event.pos
                for i, surf in enumerate(option_surfs):
                    x = WIDTH//2 - surf.get_width()//2
                    y = 180 + i*70
                    rect = pygame.Rect(x, y, surf.get_width(), surf.get_height())
                    if rect.collidepoint(mx, my):
                        idx = i
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                for i, surf in enumerate(option_surfs):
                    x = WIDTH//2 - surf.get_width()//2
                    y = 180 + i*70
                    rect = pygame.Rect(x, y, surf.get_width(), surf.get_height())
                    if rect.collidepoint(mx, my):
                        return RULESET_OPTIONS[i]
        clock.tick(FPS)

def simple_menu(screen, font, clock, options):
    # easy selection, returns index (0..n-1), ESC -> 0 /
    # Einfache Auswahl, gibt Index zurück (0..n-1), ESC -> 0
    idx = 0
    while True:
        screen.fill((30,30,30))
        title_surf = render_fit_text(tr("Auswahl"), (240,240,240), max_width=WIDTH-60, base_size=42, min_size=22)
        screen.blit(title_surf, (WIDTH//2 - title_surf.get_width()//2, 60))
        base_y = 160; spacing = 60
        option_surfs = []
        for i, opt in enumerate(options):
            color = (0,220,0) if i==idx else (220,220,220)
            surf = render_fit_text(opt, color, max_width=WIDTH-120, base_size=FONT_SIZE, min_size=18)
            option_surfs.append(surf)
            x = WIDTH//2 - surf.get_width()//2
            y = base_y + i*spacing
            screen.blit(surf, (x,y))
        hint = render_fit_text(tr("↑/↓ wählen, Enter bestätigen, ESC zurück"), (180,180,140), max_width=WIDTH-80, base_size=22, min_size=14)
        screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT-80))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return 0
                elif event.key == pygame.K_UP:
                    idx = (idx - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    idx = (idx + 1) % len(options)
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                    return idx
            elif event.type == pygame.MOUSEMOTION:
                mx, my = event.pos
                for i, surf in enumerate(option_surfs):
                    x = WIDTH//2 - surf.get_width()//2
                    y = base_y + i*spacing
                    rect = pygame.Rect(x, y, surf.get_width(), surf.get_height())
                    if rect.collidepoint(mx, my):
                        idx = i
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                for i, surf in enumerate(option_surfs):
                    x = WIDTH//2 - surf.get_width()//2
                    y = base_y + i*spacing
                    rect = pygame.Rect(x, y, surf.get_width(), surf.get_height())
                    if rect.collidepoint(mx, my):
                        return i
        clock.tick(FPS)

def pygame_text_input(screen, font, prompt, initial_value="", numeric=False):
    # easy text input in pygame (fallback without OS dialog) /
    # Einfache Text-Eingabe in Pygame (Fallback ohne OS-Dialog)
    value = str(initial_value)
    input_font = pygame.font.SysFont("FreeSans", 28)
    active = True
    while active:
        screen.fill((30,30,30))
        prompt_surf = input_font.render(tr(prompt), True, (200,200,200))
        val_surf = input_font.render(value, True, (255,255,255))
        screen.blit(prompt_surf, (WIDTH//2 - prompt_surf.get_width()//2, HEIGHT//2 - 40))
        pygame.draw.rect(screen, (80,80,80), (WIDTH//2 - 200, HEIGHT//2, 400, 40), 0)
        screen.blit(val_surf, (WIDTH//2 - 190, HEIGHT//2 + 5))
        hint = tr("Enter=OK, ESC=Abbrechen")
        hint_surf = input_font.render(hint, True, (160,160,120))
        screen.blit(hint_surf, (WIDTH//2 - hint_surf.get_width()//2, HEIGHT//2 + 60))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if numeric and not value.isdigit():
                        break
                    return value
                elif event.key == pygame.K_BACKSPACE:
                    value = value[:-1]
                else:
                    ch = event.unicode
                    if numeric:
                        if ch.isdigit():
                            value += ch
                    else:
                        if ch and ch.isprintable():
                            value += ch
        pygame.time.Clock().tick(FPS)

def network_wuerfeln_host(screen, font, clock):
    info_font = pygame.font.SysFont("FreeSans", 36)
    result_font = pygame.font.SysFont("FreeSans", 54)
    host_roll = random.randint(1,6)
    client_roll = random.randint(1,6)
    while client_roll == host_roll:
        client_roll = random.randint(1,6)
    host_starts = host_roll > client_roll
    # display
    # Anzeige
    screen.fill((20,20,20))
    t1 = render_fit_text(tr("Netzwerk-Würfeln"), (220,220,220), max_width=WIDTH-60, base_size=36, min_size=18)
    screen.blit(t1, (WIDTH//2 - t1.get_width()//2, 100))
    htxt = render_fit_text(f"{tr('Host')}: {host_roll}", (0,220,0), max_width=WIDTH-60, base_size=54, min_size=22)
    ctxt = render_fit_text(f"{tr('Client')}: {client_roll}", (220,0,0), max_width=WIDTH-60, base_size=54, min_size=22)
    screen.blit(htxt, (WIDTH//2 - htxt.get_width()//2, 220))
    screen.blit(ctxt, (WIDTH//2 - ctxt.get_width()//2, 300))
    # clearer assignment: Player 1 = White starts /
    # Klarere Zuordnung: Spieler 1 = Weiß beginnt
    who_line = (tr("Host beginnt – Spieler 1 (Weiß)") if host_starts else tr("Client beginnt – Spieler 1 (Weiß)"))
    who = render_fit_text(who_line, (255,200,80), max_width=WIDTH-60, base_size=36, min_size=18)
    screen.blit(who, (WIDTH//2 - who.get_width()//2, 400))
    left = tr("Spieler 1 (Weiß): Host") if host_starts else tr("Spieler 1 (Weiß): Client")
    right = tr("Spieler 2 (Schwarz): Client") if host_starts else tr("Spieler 2 (Schwarz): Host")
    assign_line = f"{left}   |   {right}"
    assign = render_fit_text(assign_line, (220,200,140), max_width=WIDTH-60, base_size=28, min_size=16)
    screen.blit(assign, (WIDTH//2 - assign.get_width()//2, 445))
    cont = render_fit_text(tr("Drücke SPACE, um zu starten..."), (160,160,120), max_width=WIDTH-60, base_size=36, min_size=18)
    screen.blit(cont, (WIDTH//2 - cont.get_width()//2, 470))
    pygame.display.flip()
    waiting=True
    while waiting:
        for e in pygame.event.get():
            if e.type==pygame.QUIT: pygame.quit(); sys.exit()
            elif e.type==pygame.KEYDOWN and e.key==pygame.K_SPACE: waiting=False
        clock.tick(FPS)
    return host_roll, client_roll, host_starts

def network_show_wuerfel_result(screen, font, clock, du_roll, gegner_roll, du_beginnt):
    info_font = pygame.font.SysFont("FreeSans", 36)
    result_font = pygame.font.SysFont("FreeSans", 54)
    screen.fill((20,20,20))
    t1 = render_fit_text(tr("Würfelergebnis"), (220,220,220), max_width=WIDTH-60, base_size=36, min_size=18)
    screen.blit(t1, (WIDTH//2 - t1.get_width()//2, 100))
    # at the client: gegner_roll belongs to host, du_roll to client /
    # Auf dem Client: gegner_roll gehört zum Host, du_roll zum Client
    host_txt = render_fit_text(f"{tr('Host')}: {gegner_roll}", (220,0,0), max_width=WIDTH-60, base_size=54, min_size=22)
    client_txt = render_fit_text(f"{tr('Client')}: {du_roll}", (0,220,0), max_width=WIDTH-60, base_size=54, min_size=22)
    screen.blit(host_txt, (WIDTH//2 - host_txt.get_width()//2, 220))
    screen.blit(client_txt, (WIDTH//2 - client_txt.get_width()//2, 300))
    # player assignment: White (Player 1) starts /
    # Spieler-Zuordnung: Weiß (Spieler 1) beginnt
    left = tr("Spieler 1 (Weiß): Client") if du_beginnt else tr("Spieler 1 (Weiß): Host")
    right = tr("Spieler 2 (Schwarz): Host") if du_beginnt else tr("Spieler 2 (Schwarz): Client")
    assign_line = f"{left}   |   {right}"
    assign = render_fit_text(assign_line, (255,200,80), max_width=WIDTH-60, base_size=30, min_size=16)
    screen.blit(assign, (WIDTH//2 - assign.get_width()//2, 400))
    you_line = tr("Du bist Spieler 1 (Weiß)") if du_beginnt else tr("Du bist Spieler 2 (Schwarz)")
    you = render_fit_text(you_line, (200,200,160), max_width=WIDTH-60, base_size=28, min_size=16)
    screen.blit(you, (WIDTH//2 - you.get_width()//2, 440))
    cont = render_fit_text(tr("Drücke SPACE, um zu starten..."), (160,160,120), max_width=WIDTH-60, base_size=32, min_size=16)
    screen.blit(cont, (WIDTH//2 - cont.get_width()//2, 490))
    pygame.display.flip()
    waiting=True
    while waiting:
        for e in pygame.event.get():
            if e.type==pygame.QUIT: pygame.quit(); sys.exit()
            elif e.type==pygame.KEYDOWN and e.key==pygame.K_SPACE: waiting=False
        clock.tick(FPS)
# ---------------- network game (easy host/client, both humans) -----------------
# ---------------- Netzwerk-Spiel (einfacher Host/Client, beide Menschen) -----------------
def start_network_connection(mode, ip, port, bind_mode="local"):
    if mode == "host":
        srv = None
        try:
            srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            bind_host = "127.0.0.1" if bind_mode == "local" else "0.0.0.0"
            srv.bind((bind_host, port))
            srv.listen(1)
            srv.setblocking(False)
            # waiting for client (with UI update task of caller) /
            # Warten auf Client (mit UI Aktualisierung Aufgabe des Aufrufers)
            return {"server": srv, "client": None, "socket": None, "mode": mode, "color": None, "bind_mode": bind_mode}
        except Exception:
            # on error, clean up and signal error to caller /
            # Bei Fehler sauber schließen und dem Aufrufer Fehler signalisieren
            try:
                if srv is not None:
                    srv.close()
            except Exception:
                pass
            return None
    else:  # client
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((ip, port))
        except Exception:
            return None
        sock.setblocking(False)
        return {"server": None, "client": None, "socket": sock, "mode": mode, "color": None, "bind_mode": bind_mode}

def close_conn_state(conn_state):
    """Sockets sauber schließen und Referenzen löschen."""
    if not conn_state:
        return
    # Peer/Client-Socket
    s = conn_state.get("socket")
    if s is not None:
        try:
            try:
                s.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass
            s.close()
        except Exception:
            pass
        conn_state["socket"] = None
    # Server-Socket
    srv = conn_state.get("server")
    if srv is not None:
        try:
            try:
                srv.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass
            srv.close()
        except Exception:
            pass
        conn_state["server"] = None

def accept_network_client(conn_state, screen, font):
    """Nicht-blockierendes Accept für Host-Mode. Liefert True, wenn ein Client verbunden wurde."""
    if conn_state.get("mode") != "host":
        return False
    srv = conn_state.get("server")
    if not srv:
        return False
    try:
        r, _, _ = select.select([srv], [], [], 0)
        if srv in r:
            client, addr = srv.accept()
            client.setblocking(False)
            conn_state["client"] = client
            conn_state["socket"] = client
            return True
    except Exception:
        return False
    return False

def network_receive_lines(sock, buffer):
    """Nicht-blockierendes Lesen zeilenorientierter Nachrichten. Liefert (lines, new_buffer, closed)."""
    lines = []
    closed = False
    try:
        while True:
            try:
                data = sock.recv(4096)
                if not data:
                    closed = True
                    break
                buffer += data.decode(errors='ignore')
            except BlockingIOError:
                break
    except Exception:
        closed = True
    while True:
        if '\n' in buffer:
            line, buffer = buffer.split('\n', 1)
            if line:
                lines.append(line.strip())
        else:
            break
    return lines, buffer, closed

def show_peer_left(peer_label="Gegner"):
    """Kleine Einblendung, dass der Peer die Verbindung verlassen hat."""
    try:
        screen = pygame.display.get_surface()
        if not screen:
            return
        screen.fill((30,30,30))
        msg = render_fit_text(f"{tr(peer_label)} {tr('hat die Verbindung beendet.')}", (220,180,120), max_width=WIDTH-60, base_size=32, min_size=18)
        screen.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2 - msg.get_height()//2))
        pygame.display.flip()
        pygame.time.wait(1200)
    except Exception:
        pass

def network_spiel_view(screen, font, clock, conn_state):
    # alias for the real network game; kept for compatibility /
    # Alias für das echte Netzwerkspiel; behalten für Kompatibilität
    return network_game_simple(screen, font, clock, conn_state)
    # when handshake rules/start, local ruleset from conn_state übernehmen
    # Nach Handshake RULES/START: lokales ruleset aus conn_state übernehmen
    ruleset = conn_state.get('ruleset', ruleset)
    local_color = conn_state["color"] or 1
    mode = conn_state.get('mode', 'host')
    # identities host/client -> player number/color /
    # host color depends on dice; for client side derived in handshake /
    # Identität Host/Client -> Spieler-Nummer/Farbe
    # Host-Farbe hängt vom Würfeln ab. Für Client-Seite wird sie im Handshake abgeleitet.
    host_color = local_color if mode == 'host' else (1 if local_color == 2 else 2)
    client_color = 2 if host_color == 1 else 1
    def net_label(player):
        ident = "Host" if player == host_color else "Client"
        num = "Spieler 1" if player == 1 else "Spieler 2"
        col = "Weiß" if player == 1 else "Schwarz"
        you = " (DU)" if player == local_color else ""
        return f"{ident} / {num} ({col}){you}"
    current_player = 1  # Weiß beginnt
    setzphase = True
    selected = None
    winner = None
    # layout-/scaling parameters like in singleplayer /
    # Layout-/Skalierungsparameter analog zum Einzelspieler
    ui_scale = max(0.6, min(WIDTH, HEIGHT) / 800.0)
    INFO_Y = max(10, int(30 * ui_scale) - 20)
    COUNTER_MARGIN = int(40 * ui_scale)
    COUNTER_R = max(6, int(16 * ui_scale))
    COUNTER_Y_TOP = max(INFO_Y + 40, int(90 * ui_scale) - 20)
    COUNTER_Y_BOT = min(HEIGHT - 20, HEIGHT - int(90 * ui_scale) + 50)
    # fine-tuning: analog: white down 20px, black up 20px /
    # Feinanpassung analog: Weiß 20px nach unten, Schwarz 20px nach oben
    COUNTER_Y_TOP = min(COUNTER_Y_TOP + 20, HEIGHT - 100)
    COUNTER_Y_BOT = max(COUNTER_Y_BOT - 20, COUNTER_Y_TOP + 100)
    top_free = (COUNTER_Y_TOP) + COUNTER_R + int(20 * ui_scale)
    bottom_free = COUNTER_Y_BOT - COUNTER_R - int(20 * ui_scale)
    margin_x = int(40 * ui_scale)
    board_scale_y = max(0.5, (bottom_free - top_free) / (2.0 * 260))
    board_scale_x = max(0.5, (WIDTH - 2.0 * margin_x) / (2.0 * 260))
    board_scale = min(ui_scale, board_scale_x, board_scale_y)
    cx = WIDTH//2
    cy = int((top_free + bottom_free)//2)
    compact = 0.9
    outer, mid, inner = int(260*compact*board_scale), int(180*compact*board_scale), int(100*compact*board_scale)
    positions = [
        (cx-outer, cy-outer), (cx, cy-outer), (cx+outer, cy-outer), (cx+outer, cy), (cx+outer, cy+outer), (cx, cy+outer), (cx-outer, cy+outer), (cx-outer, cy),
        (cx-mid, cy-mid), (cx, cy-mid), (cx+mid, cy-mid), (cx+mid, cy), (cx+mid, cy+mid), (cx, cy+mid), (cx-mid, cy+mid), (cx-mid, cy),
        (cx-inner, cy-inner), (cx, cy-inner), (cx+inner, cy-inner), (cx+inner, cy), (cx+inner, cy+inner), (cx, cy+inner), (cx-inner, cy+inner), (cx-inner, cy)
    ]
    lines_draw = [
        (0,1),(1,2),(2,3),(3,4),(4,5),(5,6),(6,7),(7,0),
        (8,9),(9,10),(10,11),(11,12),(12,13),(13,14),(14,15),(15,8),
        (16,17),(17,18),(18,19),(19,20),(20,21),(21,22),(22,23),(23,16),
        (1,9),(3,11),(5,13),(7,15),(9,17),(11,19),(13,21),(15,23)
    ]
    def check_muehle(pos, player):
        neue = False
        for idx, m in enumerate(muhlen):
            if sorted(m) in diagonale_blacklist: continue
            if pos in m and all(state[i]==player for i in m):
                if idx not in last_mills[player]:
                    last_mills[player].add(idx); neue = True
            else:
                if idx in last_mills[player]:
                    last_mills[player].remove(idx)
        return neue
    def has_moves(player):
        stones = [i for i,v in enumerate(state) if v==player]
        if len(stones)==3:
            return any(v==0 for v in state)
        for s in stones:
            for a,b in lines_draw:
                if a==s and state[b]==0: return True
                if b==s and state[a]==0: return True
        return False
    def check_win():
        if sum(1 for v in state if v==1)<3: return 2
        if sum(1 for v in state if v==2)<3: return 1
        if not has_moves(1): return 2
        if not has_moves(2): return 1
        return None
    def draw_board(info_line=""):
        screen.fill((240,220,180))
        for a,b in lines_draw:
            pygame.draw.line(screen, (120,100,80), positions[a], positions[b], max(2, int(5*board_scale)))
        node_r = max(8, int(16*board_scale))
        piece_r = max(12, int(24*board_scale))
        for idx,(x,y) in enumerate(positions):
            color=(200,180,120)
            if state[idx]==1: color=(255,255,255)
            elif state[idx]==2: color=(0,0,0)
            sel_r = max(30, int(28*board_scale))
            if selected == idx:
                # selection highlight like in human-vs-AI mode /
                # Auswahl hervorheben wie im Mensch-vs-SL-Modus
                pygame.draw.circle(screen, (0,220,0), (x, y), sel_r, 3)
            rad = piece_r if state[idx] else node_r
            pygame.draw.circle(screen, color,(x,y), rad, 0 if state[idx] else 3)
            # anti pendulum: if last own moved piece is selected,
            # mark only the forbidden retreat target field in red /
            # Anti-Pendeln: wenn der zuletzt gezogene eigene Stein ausgewählt ist,
            # markiere nur das verbotene Rückzugs-Zielfeld rot
            if ruleset == 'Turnier' and selected is not None:
                mv = last_move_by.get(current_player, (-1, -1))  # (from, to)
                if selected == mv[1] and idx == mv[0]:
                    pygame.draw.circle(screen, (220,40,40), (x, y), sel_r, 2)
        # stone counters top/bottom (white top, black bottom) – full 9 slots, gray placeholders first /
        # Stein-Counter oben/unten (oben Weiß, unten Schwarz) – volle 9 Slots, graue Platzhalter zuerst
        margin_lr = 50
        steps = 8  # 9 Slots -> 8 Abstände
        width_avail = max(1, WIDTH - 2*margin_lr)
        spacing = max(piece_r*2 + 6, width_avail // steps)
        start_x = margin_lr
        r = piece_r
        total = 9
        # top: first all placeholders, then remaining white stones on top /
        # Oben: zuerst alle Platzhalter, dann verbleibende weiße Steine drüber
        remain_w = max(0, total - stones_set[0])
        y_top = COUNTER_Y_TOP + 20
        for i in range(9):
            x = start_x + i*spacing
            pygame.draw.circle(screen, (185,180,160), (x, y_top), r, 0)
            pygame.draw.circle(screen, (140,130,110), (x, y_top), r, 1)
        for i in range(remain_w):
            x = start_x + i*spacing
            pygame.draw.circle(screen, (255,255,255), (x, y_top), r, 0)
            pygame.draw.circle(screen, (100,90,70), (x, y_top), r, 2)
        # bottom: same for black /
        # Unten: analog für Schwarz
        remain_b = max(0, total - stones_set[1])
        y_bot = COUNTER_Y_BOT - 20
        for i in range(9):
            x = start_x + i*spacing
            pygame.draw.circle(screen, (185,180,160), (x, y_bot), r, 0)
            pygame.draw.circle(screen, (140,130,110), (x, y_bot), r, 1)
        for i in range(remain_b):
            x = start_x + i*spacing
            pygame.draw.circle(screen, (0,0,0), (x, y_bot), r, 0)
            pygame.draw.circle(screen, (100,90,70), (x, y_bot), r, 2)
        if info_line:
            # somewhat smaller max_width for nice margins in network mode /
            # Etwas kleineres max_width für angenehme Ränder im Netzwerkmodus
            surf = render_fit_text(info_line, (60,40,20), max_width=WIDTH-160, base_size=FONT_SIZE, min_size=18)
            screen.blit(surf,(WIDTH//2 - surf.get_width()//2, INFO_Y))
        # tournament overlay with clear left/right assignment (two-line without '|') /
        # Turnier-Overlay mit klarer Zuordnung links/rechts (zweizeilig ohne '|')
        if ruleset == 'Turnier':
            tiny_font = pygame.font.SysFont('FreeSans', 16)
            rep_w = position_counts.get((tuple(state), 1), 0)
            rep_s = position_counts.get((tuple(state), 2), 0)
            col_inactive = (80,60,40)
            col_active = (200,140,60)
            mid_y = HEIGHT//2
            # left: white /
            # Links: Weiß
            color_w = col_active if current_player==1 else col_inactive
            label_w = tiny_font.render('Weiß', True, color_w)
            rep_w_surf = tiny_font.render(f'Rep: {rep_w}/3', True, color_w)
            hz_w_surf = tiny_font.render(f'HZ: {halfmove_clock}', True, color_w)
            left_x = 12
            screen.blit(label_w, (left_x, mid_y - 28))
            screen.blit(rep_w_surf, (left_x, mid_y - 8))
            screen.blit(hz_w_surf, (left_x, mid_y + 10))
            # right: black /
            # Rechts: Schwarz
            color_s = col_active if current_player==2 else col_inactive
            label_s = tiny_font.render('Schwarz', True, color_s)
            rep_s_surf = tiny_font.render(f'Rep: {rep_s}/3', True, color_s)
            hz_s_surf = tiny_font.render(f'HZ: {halfmove_clock}', True, color_s)
            right_x = WIDTH - 12
            screen.blit(label_s, (right_x - label_s.get_width(), mid_y - 28))
            screen.blit(rep_s_surf, (right_x - rep_s_surf.get_width(), mid_y - 8))
            screen.blit(hz_s_surf, (right_x - hz_s_surf.get_width(), mid_y + 10))
        pygame.display.flip()
    # send securely; on error, report peer left and exit game /
    # Sicher senden; bei Fehler Peer-Abbruch melden und Spiel verlassen
    def send_safe(msg: str):
        try:
            sock.sendall(msg.encode())
            return True
        except Exception:
            peer = "Client" if conn_state.get("mode") == "host" else "Host"
            close_conn_state(conn_state)
            show_peer_left(peer)
            return False
    # barrier: after mill, opponent must remove a stone / 
    # Sperre: Nach Mühlenbildung muss der entsprechende Spieler einen gegnerischen Stein entfernen
    removal_pending = False
    pending_remover = None  # 1 oder 2
    running = True
    while running:
        # incoming messages processing /
        # Eingehende Nachrichten verarbeiten
        lines_in, buffer, closed = network_receive_lines(sock, buffer)
        if closed:
            # determine peer role: from host view, peer is client, else host /
            # Bestimme Peer-Rolle: aus Sicht Host ist Peer der Client, sonst der Host
            peer = "Client" if conn_state.get("mode") == "host" else "Host"
            close_conn_state(conn_state)
            show_peer_left(peer)
            return
        for line in lines_in:
            parts = line.split()
            if parts[0]=="SET":
                # SET pos  or  SET player pos
                # SET pos  oder  SET player pos
                if len(parts) >= 3:
                    try:
                        pl = int(parts[1]); pos = int(parts[2])
                    except Exception:
                        pl = current_player; pos = int(parts[-1])
                else:
                    pl = current_player; pos = int(parts[1])
                if not removal_pending and setzphase and 0 <= pos < len(state) and state[pos]==0 and stones_set[pl-1] < 9:
                    state[pos]=pl
                    stones_set[pl-1]+=1
                    mill = check_muehle(pos,pl)
                    if mill:
                        removal_pending = True
                        pending_remover = pl
                    else:
                        current_player = 2 if pl==1 else 1
                    if stones_set[0]==9 and stones_set[1]==9:
                        setzphase=False
            elif parts[0]=="REM":
                # REM pos  or  REM player pos
                # REM pos  oder  REM player pos
                if len(parts) >= 3:
                    try:
                        _pl = int(parts[1]); pos = int(parts[2])
                    except Exception:
                        pos = int(parts[-1])
                else:
                    pos=int(parts[1])
                if 0<=pos<len(state) and state[pos] in (1,2):
                    state[pos]=0
                if removal_pending:
                    # when removal done, switch turn to opponent /
                    # Nach Entfernen: Zug an den Gegner
                    removal_pending = False
                    if pending_remover is not None:
                        current_player = 2 if pending_remover==1 else 1
                        pending_remover = None
                if ruleset == 'Turnier':
                    update_draw_state(captured=True)
            elif parts[0]=="MOVE":
                # move from to  or  MOVE player from to
                # MOVE from to  oder  MOVE player from to
                if len(parts) >= 4:
                    try:
                        pl = int(parts[1]); frm = int(parts[2]); to = int(parts[3])
                    except Exception:
                        pl = current_player; frm = int(parts[-2]); to = int(parts[-1])
                else:
                    pl = current_player; frm=int(parts[1]); to=int(parts[2])
                if not removal_pending and not setzphase and 0<=frm<len(state) and 0<=to<len(state) and state[frm] == pl and state[to]==0:
                    state[frm]=0; state[to]=pl
                    mill = check_muehle(to,pl)
                    if mill:
                        removal_pending = True
                        pending_remover = pl
                    else:
                        current_player = 2 if pl==1 else 1
                    # Merke letzte Bewegung des Gegners für Anti-Pendeln
                    if ruleset == 'Turnier':
                        last_move_by[pl] = (frm, to)
                        if not mill:
                            update_draw_state(captured=False)
            elif parts[0]=="WIN":
                winner = int(parts[1]); running=False
            elif parts[0]=="DRAW":
                is_draw = True; running=False
        info = ("Setzphase" if setzphase else "Zugphase") + " - " + net_label(current_player) \
            + ("  |  Turnierregeln" if ruleset=='Turnier' else "")
        draw_board(info)
        if winner or (ruleset=='Turnier' and is_draw):
            if conn_state.get('match'):
                prompt = (f"Spielende! {net_label(winner)} gewinnt  (SPACE=Weiter, ESC=Abbruch)" if winner
                          else "Spielende! Remis nach Turnierregeln  (SPACE=Weiter, ESC=Abbruch)")
                draw_board(prompt)
                wait=True
                aborted = False
                while wait:
                    for e in pygame.event.get():
                        if e.type==pygame.QUIT:
                            pygame.quit(); sys.exit()
                        elif e.type==pygame.KEYDOWN and e.key==pygame.K_ESCAPE:
                            aborted = True; wait=False
                        elif e.type==pygame.KEYDOWN and e.key==pygame.K_SPACE:
                            wait=False
                    clock.tick(FPS)
                if aborted:
                    winner = None
                break
            else:
                end = (f"Spielende! {'Weiß' if winner==1 else 'Schwarz'} gewinnt (ESC)" if winner \
                       else "Spielende! Remis nach Turnierregeln (ESC)")
                draw_board(end)
                wait=True
                while wait:
                    for e in pygame.event.get():
                        if e.type==pygame.QUIT: pygame.quit(); sys.exit()
                        elif e.type==pygame.KEYDOWN and e.key==pygame.K_ESCAPE: wait=False
                    clock.tick(FPS)
                break
        # local player on turn? /
        # Lokaler Spieler am Zug?
        if current_player == local_color:
            # when opponent must remove, no input allowed /
            # Wenn Gegner entfernen muss, keine Eingabe zulassen
            if removal_pending and pending_remover != local_color:
                draw_board(tr("Gegner entfernt einen Stein..."))
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit(); sys.exit()
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        if confirm_abort("Netzwerkspiel wirklich beenden?"):
                            close_conn_state(conn_state)
                            return None
                clock.tick(FPS)
                continue
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if confirm_abort("Netzwerkspiel wirklich beenden?"):
                        close_conn_state(conn_state)
                        return None
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button==1:
                    mx,my = event.pos
                    if setzphase:
                        if stones_set[current_player-1] <9 and not removal_pending:
                            for idx,(x,y) in enumerate(positions):
                                if (mx-x)**2+(my-y)**2 < 22**2 and state[idx]==0 and stones_set[current_player-1] < 9:
                                    state[idx]=current_player
                                    stones_set[current_player-1]+=1
                                    mill = check_muehle(idx,current_player)
                                    # Senden
                                    if not send_safe(f"SET {current_player} {idx}\n"):
                                        running=False; break
                                    if mill:
                                        # select removal
                                        # Entfernen wählen
                                        removing=True
                                        while removing:
                                            for ev2 in pygame.event.get():
                                                if ev2.type==pygame.QUIT: pygame.quit(); sys.exit()
                                                elif ev2.type==pygame.KEYDOWN and ev2.key==pygame.K_ESCAPE:
                                                    if confirm_abort("Netzwerkspiel wirklich beenden?"):
                                                        close_conn_state(conn_state)
                                                        return None
                                                elif ev2.type==pygame.MOUSEBUTTONDOWN and ev2.button==1:
                                                    mx2,my2=ev2.pos
                                                    opponents=[i for i,v in enumerate(state) if v==(2 if current_player==1 else 1)]
                                                    for oi in opponents:
                                                        ox,oy=positions[oi]
                                                        if (mx2-ox)**2+(my2-oy)**2<22**2:
                                                            state[oi]=0
                                                            if not send_safe(f"REM {current_player} {oi}\n"):
                                                                removing=False; running=False; break
                                                            # when own removal done, switch turn to opponent /
                                                            # Nach eigenem Entfernen: Zug an den Gegner
                                                            current_player = 2 if current_player==1 else 1
                                                            if ruleset=='Turnier':
                                                                update_draw_state(captured=True)
                                                            removing=False
                                                            break
                                            draw_board(tr("Mühle! Entferne gegnerischen Stein."))
                                            clock.tick(FPS)
                                    # setting phase over / player switch
                                    # Setzphase Ende / Spielerwechsel
                                    if stones_set[0]==9 and stones_set[1]==9:
                                        setzphase=False
                                    if not mill:
                                        current_player = 2 if current_player==1 else 1
                                        if ruleset=='Turnier':
                                            update_draw_state(captured=False)
                                    break
                    else:  # moving phase / Zugphase
                        stones_local=[i for i,v in enumerate(state) if v==current_player]
                        if len(stones_local)==3:
                            # Springen
                            for idx,(x,y) in enumerate(positions):
                                if (mx-x)**2+(my-y)**2<22**2:
                                    if state[idx]==0 and selected is not None:
                                        # anti pendulum immediate retreat prevention /
                                        # Anti-Pendeln unmittelbares Zurückziehen verhindern
                                        if ruleset=='Turnier' and last_move_by.get(current_player) == (idx, selected):
                                            continue
                                        state[selected]=0; state[idx]=current_player
                                        mill = check_muehle(idx,current_player)
                                        if not send_safe(f"MOVE {current_player} {selected} {idx}\n"):
                                            running=False; break
                                        if mill:
                                            # Entfernen
                                            removing=True
                                            while removing:
                                                for ev2 in pygame.event.get():
                                                    if ev2.type==pygame.QUIT: pygame.quit(); sys.exit()
                                                    elif ev2.type==pygame.KEYDOWN and ev2.key==pygame.K_ESCAPE:
                                                        if confirm_abort("Netzwerkspiel wirklich beenden?"):
                                                            close_conn_state(conn_state)
                                                            return None
                                                    elif ev2.type==pygame.MOUSEBUTTONDOWN and ev2.button==1:
                                                        mx2,my2=ev2.pos
                                                        opponents=[i for i,v in enumerate(state) if v==(2 if current_player==1 else 1)]
                                                        for oi in opponents:
                                                            ox,oy=positions[oi]
                                                            if (mx2-ox)**2+(my2-oy)**2<22**2:
                                                                state[oi]=0
                                                                if not send_safe(f"REM {current_player} {oi}\n"):
                                                                    removing=False; running=False; break
                                                                removing=False
                                                                break
                                                draw_board(tr("Mühle! Entferne gegnerischen Stein."))
                                                clock.tick(FPS)
                                        last_move = (current_player, selected, idx)
                                        selected=None
                                        current_player = 2 if current_player==1 else 1
                                        if ruleset=='Turnier' and not mill:
                                            update_draw_state(captured=False)
                                        break
                                    elif state[idx]==current_player:
                                        selected=idx
                                        break
                        else:
                            # normal move along lines /
                            # Normales Ziehen entlang Linien
                            if selected is None:
                                for idx,(x,y) in enumerate(positions):
                                    if (mx-x)**2+(my-y)**2<22**2 and state[idx]==current_player:
                                        selected=idx; break
                            else:
                                # neighbor? / Nachbar?
                                neigh = []
                                for a,b in lines_draw:
                                    if a==selected: neigh.append(b)
                                    elif b==selected: neigh.append(a)
                                for idx,(x,y) in enumerate(positions):
                                    if (mx-x)**2+(my-y)**2<22**2 and idx in neigh and state[idx]==0:
                                        if ruleset=='Turnier' and last_move_by.get(current_player) == (idx, selected):
                                            continue
                                        state[selected]=0; state[idx]=current_player
                                        mill = check_muehle(idx,current_player)
                                        if not send_safe(f"MOVE {current_player} {selected} {idx}\n"):
                                            running=False; break
                                        if mill:
                                            removing=True
                                            while removing:
                                                for ev2 in pygame.event.get():
                                                    if ev2.type==pygame.QUIT: pygame.quit(); sys.exit()
                                                    elif ev2.type==pygame.KEYDOWN and ev2.key==pygame.K_ESCAPE:
                                                        if confirm_abort("Netzwerkspiel wirklich beenden?"):
                                                            removing=False; running=False; break
                                                    elif ev2.type==pygame.MOUSEBUTTONDOWN and ev2.button==1:
                                                        mx2,my2=ev2.pos
                                                        opponents=[i for i,v in enumerate(state) if v==(2 if current_player==1 else 1)]
                                                        for oi in opponents:
                                                            ox,oy=positions[oi]
                                                            if (mx2-ox)**2+(my2-oy)**2<22**2:
                                                                state[oi]=0
                                                                if not send_safe(f"REM {current_player} {oi}\n"):
                                                                    removing=False; running=False; break
                                                                removing=False
                                                                break
                                                draw_board(tr("Mühle! Entferne gegnerischen Stein."))
                                                clock.tick(FPS)
                                        last_move_by[current_player] = (selected, idx)
                                        selected=None
                                        current_player = 2 if current_player==1 else 1
                                        if ruleset=='Turnier' and not mill:
                                            update_draw_state(captured=False)
                                        break
                                # possibility to change selection /
                                # Möglichkeit Auswahl wechseln
                                for idx,(x,y) in enumerate(positions):
                                    if (mx-x)**2+(my-y)**2<22**2 and state[idx]==current_player:
                                        selected=idx; break
        else:
            # if not on turn: still process events like QUIT /
            # Wenn nicht am Zug: trotzdem Events wie QUIT verarbeiten
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if confirm_abort("Netzwerkspiel wirklich beenden?"):
                        close_conn_state(conn_state)
                        return None
    # check win/draw only when setting phase is over
    # Sieg prüfen erst nach der Setzphase
        if not setzphase:
            w = check_win()
            if w:
                winner = w
                send_safe(f"WIN {w}\n")
            elif ruleset=='Turnier' and is_draw:
                send_safe("DRAW\n")
                # display at the beginning of next loop /
                # Anzeige erfolgt zu Beginn der nächsten Schleife
        clock.tick(FPS)
    return winner


def spielfeld_view_rematch(screen, font, clock, starter):
    # wrapper for spielfeld_view, returns winner (1=white, 2=black) back /
    # Wrapper für spielfeld_view, gibt Gewinner (1=Weiß, 2=Schwarz) zurück
    result = {'winner': None}
    def spielfeld_view_with_result(*args, **kwargs):
        nonlocal result
        # ...existing code...
        # we use the existing spielfeld_view, but with return trick:
        # we copy the function and add return winner at the end
        # the function is too long, so we use a workaround:
        # we copy the code from spielfeld_view and add return winner at the end of the move phase
        # Wir nutzen die bestehende spielfeld_view, aber mit Rückgabe
        # Trick: Wir kopieren die Funktion und fügen am Ende return winner ein
        # Da die Funktion zu lang ist, nutzen wir einen Workaround:
        # Wir kopieren den Code von spielfeld_view und fügen return winner am Ende der Zugphase ein
        # ...existing code...
    
    result = spielfeld_view(screen, font, clock, starter)
    if result not in (1, 2):
        return None
    return result

def show_rematch_score(screen, font, siege, spiele):
    # shows current score after each game / 
    # Zeigt den aktuellen Stand nach jedem Spiel
    screen.fill((30,30,30))
    info = f"{tr('Zwischenstand:')} {tr('Weiß')} {siege[1]} - {tr('Schwarz')} {siege[2]}  ({tr('Spiel ')}{spiele}/3)"
    info_surf = render_fit_text(info, (255,255,255), max_width=WIDTH-80, base_size=36, min_size=18)
    screen.blit(info_surf, (WIDTH//2 - info_surf.get_width()//2, HEIGHT//2-40))
    cont = "Drücke SPACE für das nächste Spiel..."
    cont_surf = render_fit_text(cont, (200,200,100), max_width=WIDTH-80, base_size=28, min_size=14)
    screen.blit(cont_surf, (WIDTH//2 - cont_surf.get_width()//2, HEIGHT//2+40))
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False
        pygame.time.Clock().tick(FPS)

def show_rematch_end(screen, font, siege):
    # shows final result and waits for ESC /
    # Zeigt das Endergebnis und wartet auf ESC
    screen.fill((30,30,30))
    if siege[1] > siege[2]:
        msg = f"{tr('Weiß')} {tr('gewinnt das Match!')}"
    elif siege[2] > siege[1]:
        msg = f"{tr('Schwarz')} {tr('gewinnt das Match!')}"
    else:
        msg = tr("Unentschieden im Match!")
    msg_surf = render_fit_text(msg, (255,255,255), max_width=WIDTH-80, base_size=36, min_size=18)
    screen.blit(msg_surf, (WIDTH//2 - msg_surf.get_width()//2, HEIGHT//2-40))
    cont = "Drücke ESC für das Menü..."
    cont_surf = render_fit_text(cont, (200,200,100), max_width=WIDTH-80, base_size=28, min_size=14)
    screen.blit(cont_surf, (WIDTH//2 - cont_surf.get_width()//2, HEIGHT//2+40))
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                waiting = False
        pygame.time.Clock().tick(FPS)

def show_rematch_score_custom(screen, font, left_label, right_label, left_score, right_score, spiele):
    # multi lines: label1, label2, game info each below the other /
    # Mehrzeilig: Label1, Label2, Spielinfo jeweils untereinander
    screen.fill((30,30,30))
    line1 = f"{left_label}: {left_score}"
    line2 = f"{right_label}: {right_score}"
    line3 = f"{tr('Spiel ')}{spiele}/3"
    s1 = render_fit_text(line1, (255,255,255), max_width=WIDTH-80, base_size=36, min_size=18)
    s2 = render_fit_text(line2, (255,255,255), max_width=WIDTH-80, base_size=36, min_size=18)
    s3 = render_fit_text(line3, (200,200,180), max_width=WIDTH-80, base_size=30, min_size=16)
    total_h = s1.get_height() + s2.get_height() + s3.get_height() + 16
    y = HEIGHT//2 - total_h//2
    screen.blit(s1, (WIDTH//2 - s1.get_width()//2, y))
    y += s1.get_height() + 6
    screen.blit(s2, (WIDTH//2 - s2.get_width()//2, y))
    y += s2.get_height() + 6
    screen.blit(s3, (WIDTH//2 - s3.get_width()//2, y))
    cont = tr("Drücke SPACE für das nächste Spiel...")
    cont_surf = render_fit_text(cont, (200,200,100), max_width=WIDTH-80, base_size=28, min_size=14)
    screen.blit(cont_surf, (WIDTH//2 - cont_surf.get_width()//2, HEIGHT//2 + total_h//2 + 24))
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False
        pygame.time.Clock().tick(FPS)

def show_rematch_end_custom(screen, font, left_label, right_label, left_score, right_score):
    # like show_rematch_end, but with custom labels /
    # Wie show_rematch_end, aber mit frei wählbaren Labels
    screen.fill((30,30,30))
    if left_score > right_score:
        msg = f"{left_label} {tr('gewinnt das Match!')}"
    elif right_score > left_score:
        msg = f"{right_label} {tr('gewinnt das Match!')}"
    else:
        msg = tr("Unentschieden im Match!")
    msg_surf = render_fit_text(msg, (255,255,255), max_width=WIDTH-80, base_size=36, min_size=18)
    screen.blit(msg_surf, (WIDTH//2 - msg_surf.get_width()//2, HEIGHT//2-40))
    # small fireworks for the winner (singleplayer or network)
    # Kleines Feuerwerk für den Gewinner (egal ob Singleplayer oder Netzwerk)
    is_draw = (left_score == right_score)
    if left_score > right_score:
        winner_label, loser_label = left_label, right_label
    elif right_score > left_score:
        winner_label, loser_label = right_label, left_label
    else:
        winner_label, loser_label = None, None
    fireworks_enabled = not is_draw
    fireworks = []
    if fireworks_enabled:
        # creates some initial explosions /
        # Erzeuge anfangs einige Explosionen
        for _ in range(6):
            cx = random.randint(WIDTH//4, 3*WIDTH//4)
            cy = random.randint(HEIGHT//4, HEIGHT//2)
            color = random.choice([(255,120,120),(255,220,120),(160,255,160),(160,200,255),(255,160,230)])
            particles = []
            for _ in range(60):
                angle = random.random() * 6.283
                speed = random.uniform(1.2, 3.0)
                vx = speed * math.cos(angle)
                vy = speed * math.sin(angle)
                life = random.randint(30, 60)
                particles.append([cx, cy, vx, vy, life, color])
            fireworks.append(particles)
    # note text / 
    # Hinweistext
    cont = tr("Drücke ESC für das Menü...")
    cont_surf = render_fit_text(cont, (200,200,100), max_width=WIDTH-80, base_size=28, min_size=14)
    screen.blit(cont_surf, (WIDTH//2 - cont_surf.get_width()//2, HEIGHT//2+40))
    # looser line (red) /
    # Verlierer-Zeile (rot)
    if not is_draw and loser_label:
        loser_surf = render_fit_text(f"{loser_label} {tr('verliert das Match')}", (220,90,90), max_width=WIDTH-80, base_size=28, min_size=14)
        screen.blit(loser_surf, (WIDTH//2 - loser_surf.get_width()//2, HEIGHT//2))
    pygame.display.flip()
    waiting = True
    tclock = pygame.time.Clock()
    gravity = 0.04
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                waiting = False
        if fireworks_enabled:
            # update and render fireworks over dark background /
            # Update und Render Feuerwerk über dunklem Hintergrund
            screen.fill((30,30,30))
            # reset text and hints /
            # Re-render Text und Hinweis
            if left_score > right_score:
                msg = f"{left_label} {tr('gewinnt das Match!')}"
            elif right_score > left_score:
                msg = f"{right_label} {tr('gewinnt das Match!')}"
            else:
                msg = tr("Unentschieden im Match!")
            msg_surf = render_fit_text(msg, (255,255,255), max_width=WIDTH-80, base_size=36, min_size=18)
            screen.blit(msg_surf, (WIDTH//2 - msg_surf.get_width()//2, HEIGHT//2-40))
            # looser line (red) /
            # Verlierer-Hinweis in Rot
            if loser_label and not is_draw:
                loser_surf = render_fit_text(f"{loser_label} {tr('verliert das Match')}", (220,90,90), max_width=WIDTH-80, base_size=28, min_size=14)
                screen.blit(loser_surf, (WIDTH//2 - loser_surf.get_width()//2, HEIGHT//2))
            cont_surf = render_fit_text(cont, (200,200,100), max_width=WIDTH-80, base_size=28, min_size=14)
            screen.blit(cont_surf, (WIDTH//2 - cont_surf.get_width()//2, HEIGHT//2+40))
            # particle physics /
            # Partikel aktualisieren
            alive_fireworks = []
            for particles in fireworks:
                alive_particles = []
                for p in particles:
                    p[0] += p[2]
                    p[1] += p[3]
                    p[3] += gravity
                    p[4] -= 1
                    if p[4] > 0:
                        alive_particles.append(p)
                        pygame.draw.circle(screen, p[5], (int(p[0]), int(p[1])), 2)
                if alive_particles:
                    alive_fireworks.append(alive_particles)
            fireworks = alive_fireworks
            # new explosion occasionally /
            # Neue Explosion gelegentlich hinzufügen
            if random.random() < 0.04:
                cx = random.randint(WIDTH//6, 5*WIDTH//6)
                cy = random.randint(HEIGHT//5, HEIGHT//2)
                color = random.choice([(255,120,120),(255,220,120),(160,255,160),(160,200,255),(255,160,230)])
                particles = []
                for _ in range(60):
                    angle = random.random() * 6.283
                    speed = random.uniform(1.2, 3.0)
                    vx = speed * math.cos(angle)
                    vy = speed * math.sin(angle)
                    life = random.randint(30, 60)
                    particles.append([cx, cy, vx, vy, life, color])
                fireworks.append(particles)
            pygame.display.flip()
            tclock.tick(60)

def play_match_best_of_3(screen, font, clock):
    # best-of-3 match vs. AI: first to 2 wins or leading after 3 games /
    # we count wins by identity: human vs. AI
    # Best-of-3 Match: erster, der 2 Siege hat oder nach 3 Spielen vorn liegt
    # Wir zählen Siege nach Identität: Mensch vs SL
    mensch_wins = 0
    ki_wins = 0  # internal variable remains so named / interne Variable bleibt so benannt
    spiel_nr = 0
    match_ende = False
    # alternating start: re-roll before each game /
    # Alternierender Start: vor jedem Spiel neu würfeln
    while not match_ende:
        spiel_nr += 1
        # starting player determine /
        # Startspieler ermitteln
        while True:
            starter = würfeln_view(screen, font, clock)
            if starter is not None:
                break
        winner = spielfeld_view(screen, font, clock, starter)
        if winner is None:
            # cancel via ESC -> back to menu immediately /
            # Abbruch per ESC bestätigt -> sofort zurück ins Menü
            return
        # winner: 1=white, 2=black. sort white/black to identity /
        # winner: 1=Weiß, 2=Schwarz. Ordne Weiß/Schwarz zur Identität zu:
        if winner in (1,2):
            if starter == "Spieler":
                # player is white, AI is black /
                # Spieler ist Weiß, SL ist Schwarz
                if winner == 1:
                    mensch_wins += 1
                else:
                    ki_wins += 1
            else:  
                # starter == AI / starter == "SL"
                # SL ist Weiß, Spieler ist Schwarz
                if winner == 1:
                    ki_wins += 1
                else:
                    mensch_wins += 1
        # show interim score if match not over /
        # Zwischenstand anzeigen, falls Match nicht vorbei
        if mensch_wins == 2 or ki_wins == 2 or spiel_nr == 3:
            # Match Ende
            show_rematch_end_custom(screen, font, "Mensch", "SL", mensch_wins, ki_wins)
            match_ende = True
        else:
            # interim score (ascending: 1/3, 2/3, ...)
            # Zwischenstand (aufsteigend: 1/3, 2/3, ...)
            show_rematch_score_custom(screen, font, "Mensch", "SL", mensch_wins, ki_wins, spiel_nr)

def play_network_match_best_of_3(screen, font, clock, base_conn_state):
    # best-of-3 over network: first to 2 wins or 3 games /
    # we count wins by identity: host vs. client
    # Best-of-3 übers Netzwerk: bis 2 Siege oder 3 Spiele
    # Zähle Siege nach Identität: Host vs Client
    host_wins = 0
    client_wins = 0
    spiel_nr = 0
    mode = base_conn_state.get('mode')
    while True:
            spiel_nr += 1
            conn = dict(base_conn_state)  # easy copy; socket remains the same / leichte Kopie; Socket bleibt gleich
            conn['match'] = True
            sock = conn['socket']
            # ruleset is already set/agreed /
            # per game re-roll and set START/color
            # # Regelset ist bereits gesetzt/abgeglichen
            # Pro Partie neu würfeln und START/Farbe setzen
            if mode == 'host':
                h, c, host_starts = network_wuerfeln_host(screen, font, clock)
                try:
                    sock.sendall(f"ROLL {h} {c}\n".encode())
                except Exception:
                    pass
                if host_starts:
                    conn['color'] = 1
                    try: sock.sendall("START WHITE\n".encode())
                    except Exception: pass
                else:
                    conn['color'] = 2
                    try: sock.sendall("START BLACK\n".encode())
                    except Exception: pass
            else:
                # client: wait for ROLL/START and set local color
                # Client: auf ROLL/START warten und lokale Farbe setzen
                buffer = conn.get('buffer', '')
                du_roll = None; gegner_roll = None; du_beginnt = None
                waiting = True
                while waiting:
                    lines_in, buffer, closed = network_receive_lines(sock, buffer)
                    if closed:
                        close_conn_state(base_conn_state)
                        return
                    for line in lines_in:
                        parts = line.split()
                        if parts and parts[0] == 'ROLL' and len(parts) >= 3:
                            try:
                                gegner_roll = int(parts[1]); du_roll = int(parts[2])
                            except Exception:
                                pass
                        elif parts and parts[0] == 'START' and len(parts) >= 2:
                            if parts[1].upper() == 'WHITE':
                                conn['color'] = 2  # Host ist Weiß -> Client Schwarz
                                du_beginnt = False
                            else:
                                conn['color'] = 1  # Host ist Schwarz -> Client Weiß
                                du_beginnt = True
                            waiting = False
                            break
                    # small ui: 
                    # kurze UI: Ergebnis anzeigen, wenn beide Würfe da sind
                    if du_roll is not None and gegner_roll is not None and du_beginnt is not None:
                        network_show_wuerfel_result(screen, font, clock, du_roll, gegner_roll, du_beginnt)
                conn['buffer'] = buffer
            # Starte die Partie
            result = network_game_simple(screen, font, clock, conn)
            if result is None:
                # cancel via ESC – close connection
                # Abbruch via ESC – Verbindung schließen
                close_conn_state(base_conn_state)
                break
            # result: 1/2 is winning COLOR (white/black). map to identity /
            # result 1/2 ist Gewinner-FARBE (Weiß/Schwarz). Ordne zur Identität zu:
            if result in (1,2):
                # conn['color'] contains local color (1=white, 2=black)
                # host is white if host_starts was True (sent via START WHITE), else black.
                # in network_spiel_view, 'color' is set for client in handshake.
                # conn['color'] enthält die lokale Farbe (1=Weiß, 2=Schwarz)
                # Host ist Weiß wenn host_starts True war (per START WHITE gesendet), sonst Schwarz.
                # In network_spiel_view wird 'color' für Client im Handshake gesetzt.
                host_color = conn['color'] if mode == 'host' else (1 if (conn.get('color') == 2) else 2)
                # explanation: if we are host, host_color is our local color.
                # Erklärung: Wenn wir Client sind, dann ist Host die Gegenfarbe unserer lokalen Farbe.
                if result == host_color:
                    host_wins += 1
                else:
                    client_wins += 1
            if host_wins == 2 or client_wins == 2 or spiel_nr == 3:
                left_label = 'Host' if mode == 'host' else 'Client'
                right_label = 'Client' if mode == 'host' else 'Host'
                left_score = host_wins if mode == 'host' else client_wins
                right_score = client_wins if mode == 'host' else host_wins
                show_rematch_end_custom(screen, font, left_label, right_label, left_score, right_score)
                # match over – close connection /
                # Match fertig – Verbindung schließen
                close_conn_state(base_conn_state)
                break
            else:
                left_label = 'Host' if mode == 'host' else 'Client'
                right_label = 'Client' if mode == 'host' else 'Host'
                left_score = host_wins if mode == 'host' else client_wins
                right_score = client_wins if mode == 'host' else host_wins
                # interim score (ascending: 1/3, 2/3, ...)
                # Zwischenstand (aufsteigend: 1/3, 2/3, ...)
                show_rematch_score_custom(screen, font, left_label, right_label, left_score, right_score, spiel_nr)

if __name__ == "__main__":
    main()
