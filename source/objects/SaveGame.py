import json
from datetime import datetime, timezone
from pathlib import Path


SAVE_VERSION = 1
SAVE_SLOT_COUNT = 3
DEFAULT_SAVE_DIR = Path("saves")
LEGACY_SAVE_PATH = Path("saves/savegame.json")


def get_slot_path(slot: int, save_dir: str | Path = DEFAULT_SAVE_DIR) -> Path:
    if slot < 1:
        raise ValueError("Slot must be 1 or greater.")
    return Path(save_dir) / f"slot{slot}.json"


def get_save_slot_summaries(
    slot_count: int = SAVE_SLOT_COUNT,
    save_dir: str | Path = DEFAULT_SAVE_DIR,
) -> list[dict]:
    summaries = []
    for slot in range(1, slot_count + 1):
        slot_path = get_slot_path(slot, save_dir=save_dir)
        exists = slot_path.exists()
        summary = {
            "slot": slot,
            "path": slot_path,
            "exists": exists,
            "saved_at": None,
            "size_bytes": 0,
        }
        if exists:
            summary["size_bytes"] = slot_path.stat().st_size
            try:
                with slot_path.open("r", encoding="utf-8") as handle:
                    payload = json.load(handle)
                if isinstance(payload, dict):
                    saved_at = payload.get("saved_at")
                    if isinstance(saved_at, str):
                        summary["saved_at"] = saved_at
            except (OSError, json.JSONDecodeError):
                pass
        summaries.append(summary)
    return summaries


def save_game(ship, slot: int = 1, path: str | Path | None = None) -> Path:
    save_path = Path(path) if path is not None else get_slot_path(slot)
    save_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "save_version": SAVE_VERSION,
        "saved_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "slot": slot,
        "galaxy": ship.galaxy.to_dict(),
        "ship": ship.to_dict(),
    }
    with save_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
    return save_path


def load_game(ship, slot: int = 1, path: str | Path | None = None) -> Path:
    save_path = Path(path) if path is not None else get_slot_path(slot)
    if path is None and slot == 1 and not save_path.exists() and LEGACY_SAVE_PATH.exists():
        save_path = LEGACY_SAVE_PATH
    with save_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    if not isinstance(payload, dict):
        raise ValueError("Save file is invalid.")

    save_version = int(payload.get("save_version", 0))
    if save_version != SAVE_VERSION:
        raise ValueError(f"Unsupported save version: {save_version}.")

    galaxy_state = payload.get("galaxy")
    ship_state = payload.get("ship")
    if not isinstance(galaxy_state, dict) or not isinstance(ship_state, dict):
        raise ValueError("Save file missing galaxy/ship state.")

    ship.galaxy.apply_state(galaxy_state)
    ship.apply_state(ship_state)
    return save_path
