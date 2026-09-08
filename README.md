# SpaceTrader

Terminal-first space trading and navigation prototype built with Textual.

## Run

```bash
./.venv/bin/python source/SpaceTrader.py
```

## Current Controls

- `[J]` Open jump navigation / jump actions
- `[G]` Open local navigation / local actions
- `[C]` Open cargo manifest / cargo actions
- `[Up/Down]` Move selected target (or menu row when a command menu is open)
- `[Enter]` Open/confirm action menu
- `[Esc]` Cancel active command menu
- `[T]` Toggle market sort mode (only while market list is open)
- `[Ctrl+S]` Save game (slot picker)
- `[Ctrl+L]` Load game (slot picker)

## UI Model

- Left panel:
  - `ViewPort`: long/local cartography, cargo manifest, and travel progress
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
- Mined resources are market commodities too (`iron`, `nickel`, `silver`, `gold`, `diamond`).
- Commodity list supports sort modes:
  - `NAME ↑`
  - `PRICE ↑`
  - `STOCK ↓`
  - `OWNED ↓`
- Select a commodity, then choose quantity (`+1`, `+5`, `+10`).
- Returning from quantity picker keeps the previous commodity selection highlighted.

## Extraction Flow

- `Extract Resources` is available at current location only on `Asteroid` and `Comet`.
- First use performs a resource survey progress pass and logs color-coded composition descriptors (`Rich`, `Medium`, `Low`, `Traces`).
- Subsequent uses harvest random batches into cargo hold, limited by:
  - remaining body deposits
  - ship cargo capacity
- Deposits persist per body and can be depleted.

## Cargo Manifest

- Press `[C]` to open the cargo manifest in the `ViewPort`.
- Use `[Up/Down]` to select cargo items.
- Press `[Enter]` for cargo actions.
- `Eject Cargo` flow:
  - choose quantity (`1`, `5`, `10`, based on available units)
  - confirm ejection
  - selected quantity is removed from cargo hold

## Notes

- Starting system is pre-scanned (long + short range) for immediate visibility.
- Comms panel shows live action preview while moving through cartography targets.

## Travel Encounters

- Jump and local travel now run a deterministic encounter roll on completion.
- Current placeholder outcomes:
  - stable transit (no effect)
  - fuel leak (fuel loss)
  - micrometeor impact (shield/structure damage)
  - salvage opportunity (credit gain)
  - distress signal (narrative event)
- Non-trivial encounter outcomes raise a red-highlighted `Encounter Alert` menu in `ShipComms` and require acknowledgement.

## Proto2: Cinder Reach (local branch)

Proto2 is a new shared-world prototype on the local `proto2` branch. It is deliberately separate from the Proto1 app.

Run it with:

```bash
./.venv/bin/python source/Proto2.py
```

Controls:
- `[S]` queue a scan order
- `[B]` queue a purchase of two fuel units
- `[R]` resolve a simultaneous turn (the AI trader submits through the same order model)
- `[Q]` quit

The vertical slice demonstrates deterministic seeded-sector generation, shared markets, a server-style event log, an AI captain using the same command contract, and persistent shortage situations triggered by market depletion.
