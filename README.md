# SpaceTrader

Terminal-first space trading and navigation prototype built with Textual.

## Run

```bash
./.venv/bin/python source/SpaceTrader.py
```

## Current Controls

- `[J]` Open jump navigation / jump actions
- `[G]` Open local navigation / local actions
- `[Up/Down]` Move selected target (or menu row when a command menu is open)
- `[Enter]` Open/confirm action menu
- `[Esc]` Cancel active command menu
- `[T]` Toggle market sort mode (only while market list is open)
- `[Ctrl+S]` Save game (slot picker)
- `[Ctrl+L]` Load game (slot picker)

## UI Model

- Left panel:
  - `ViewPort`: long/local cartography and travel progress
  - `ShipLog`: event and result logging
- Right panel:
  - `ShipComms`: integrated command menu + action preview (replaces old popup menus)
  - `ShipControls`: keyboard hints and scan readiness
  - `ShipStats`: ship systems + credits/cargo/fuel

## Save System

- Save slots:
  - `saves/slot1.json`
  - `saves/slot2.json`
  - `saves/slot3.json`
- Slot picker is shown for both save and load.
- Legacy fallback: loading slot 1 will use `saves/savegame.json` if present.

## Market Flow

- Open local actions at a station and select `Open Trade Console`.
- Choose `Buy Cargo` or `Sell Cargo`.
- Commodity list supports sort modes:
  - `NAME ↑`
  - `PRICE ↑`
  - `STOCK ↓`
  - `OWNED ↓`
- Select a commodity, then choose quantity (`+1`, `+5`, `+10`).
- Returning from quantity picker keeps the previous commodity selection highlighted.

## Notes

- Starting system is pre-scanned (long + short range) for immediate visibility.
- Comms panel shows live action preview while moving through cartography targets.
