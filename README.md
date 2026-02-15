# AutoSetCustomCSAFAP

A Python tool that generates and modifies CS2 configuration files (`.cfg`) and the language file (`platform_english.txt`) for custom lineup setups.

## Features

- Parse CS2 `getpos` console output to extract yaw/pitch angles
- Calculate mouse movement values using the formula `value = angle / 0.022`
- Generate unique 6-character alphanumeric IDs for each lineup
- Create/modify config files:
  - `main.cfg` – alias definitions for yaw/pitch mouse movements
  - `platform_english.txt` – custom radio wheel text
  - `{map}_{side}_labels.cfg` – radio wheel label assignments
  - `{map}_{side}_commands.cfg` – radio wheel command bindings
- Tkinter GUI for managing lineups with auto/manual slot selection
- JSON-based persistence for saved lineups and settings

## Supported Values

- **Sides**: T, CT
- **Maps**: ancient, anubis, dust2, inferno, mirage, nuke, vertigo, overpass, train
- **Grenades**: smoke, grenade, mollotov, decoy

## Requirements

- Python 3.10+
- tkinter (included with most Python installations)

## Usage

```bash
pip install -r requirements.txt
python -m src.main
```

## Running Tests

```bash
python -m pytest tests/ -v
```

## Project Structure

```
src/
├── __init__.py
├── main.py              # Entry point
├── core.py              # getpos parser, yaw/pitch calculator, ID generator
├── config_generator.py  # Config file read/write operations
├── constants.py         # Maps, sides, grenades, limits
├── gui.py               # Tkinter GUI
└── storage.py           # JSON persistence
tests/
├── test_core.py
├── test_config_generator.py
└── test_storage.py
```