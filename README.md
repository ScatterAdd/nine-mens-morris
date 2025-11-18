# Nine Men's Morris (Mühle) — Pygame

A Nine Men's Morris game written in Python using Pygame.

## License

    This project is licensed under the GNU General Public License 
    Version 3 (GPL-3.0). You are allowed to use, modify, and distribute 
    this project, provided that all modified versions are also released 
    under the GPL-3.0 license. See the LICENSE file for the full 
    license text.

## Features
- Human vs. AI with three difficulty levels (Easy, Medium, Hard)
- Two rulesets:
  - Classic (“relaxed”): no anti-pendulum / draw enforcement
  - Tournament: anti-pendulum, threefold repetition,
    100 half-move draw
- Network play (Host/Client) for two humans,
  including dice roll to decide who starts
- Best-of-3 match mode (singleplayer and network)
- Mouse and keyboard controls, scalable UI

## Requirements
- Python 3.9+ (recommended 3.10–3.12)
- Pygame 2.x
- Optional: tkinter (some input dialogs can use it; there is an
  in-game fallback)

## Installation
```bash
# (optional) virtual environment
python3 -m venv .venv
source .venv/bin/activate

# dependencies
pip install --upgrade pip
pip install pygame
```

## Run
```bash
python3 nine-mens-morris.py
```

## Controls (short)
- Menu:
   Arrow Up/Down to navigate,
   Enter/Space to confirm,
   ESC to go back.
   Mouse works, too.
- Game:
   Place/move stones with the mouse.
   ESC aborts.
   SPACE to roll/confirm where shown.
- Network:
   Choose Host/Client/IP/Port in the menu;
   “Connect” starts the connection.
   The host selects the ruleset and it’s transmitted 
   to the client.

## Network notes
- Defaults: 127.0.0.1:50007
- For LAN/Internet games, open the chosen port in your
  firewall/router as needed.
  ``Please remember that encryption is not implemented 
    for connections via the Internet.``
- The host starts a server;
  The client connects to the host’s IP/port.

## Language
- The UI supports English, German, French, Spanish.
- Toggle at runtime with the “L” key
  the menu shows the current language.
- Default language can be set by editing
  `CURRENT_LANG = "de"` or "en" in 
  `nine-mens-morris.py`
- Additional languages (e.g. French/Spanish)
  may be added in the future.

## Known notes
- Wayland/remote desktops can influence window/input
  handling depending on your setup.
- If tkinter is missing, the built-in Pygame dialog 
  is used for text input.

