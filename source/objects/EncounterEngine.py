from dataclasses import dataclass
from hashlib import sha256
from random import Random


@dataclass
class EncounterResult:
    outcome: str
    title: str
    detail: str
    fuel_delta: int = 0
    credits_delta: int = 0
    shield_delta: int = 0
    structure_delta: int = 0


def resolve_travel_encounter(
    *,
    ship,
    travel_type: str,
    distance: float,
    destination_name: str,
    event_index: int,
) -> EncounterResult:
    seed_source = (
        f"{travel_type}|{distance:.2f}|{destination_name}|"
        f"{ship.get_current_system()}|{ship.get_current_location()}|{event_index}"
    )
    seed_int = int(sha256(seed_source.encode("utf-8")).hexdigest()[:16], 16)
    rng = Random(seed_int)

    base_risk = 28 if travel_type == "jump" else 12
    distance_risk = min(35, int(distance / (90.0 if travel_type == "jump" else 180.0)))
    encounter_threshold = min(85, base_risk + distance_risk)
    encounter_roll = rng.randint(1, 100)
    if encounter_roll > encounter_threshold:
        return EncounterResult(
            outcome="none",
            title="Transit stable",
            detail="No significant encounters detected en route.",
        )

    outcome_roll = rng.randint(1, 100)
    if outcome_roll <= 35:
        return _fuel_leak_result(rng, travel_type)
    if outcome_roll <= 65:
        return _micrometeor_result(rng)
    if outcome_roll <= 90:
        return _salvage_result(rng, travel_type)
    return EncounterResult(
        outcome="distress_ping",
        title="Distress signal intercepted",
        detail="A faint emergency beacon was logged to nav records.",
    )


def _fuel_leak_result(rng: Random, travel_type: str) -> EncounterResult:
    max_loss = 4 if travel_type == "jump" else 3
    loss = rng.randint(1, max_loss)
    return EncounterResult(
        outcome="fuel_leak",
        title="Micro fuel leak",
        detail=f"Fuel lines vented during transit. Fuel -{loss}.",
        fuel_delta=-loss,
    )


def _micrometeor_result(rng: Random) -> EncounterResult:
    shield_dmg = rng.randint(5, 14)
    structure_dmg = rng.randint(0, 4)
    return EncounterResult(
        outcome="micrometeor",
        title="Micrometeor impact",
        detail=f"Shield stress detected. Shields -{shield_dmg}, Structure -{structure_dmg}.",
        shield_delta=-shield_dmg,
        structure_delta=-structure_dmg,
    )


def _salvage_result(rng: Random, travel_type: str) -> EncounterResult:
    min_gain, max_gain = (80, 260) if travel_type == "jump" else (40, 140)
    gain = rng.randint(min_gain, max_gain)
    return EncounterResult(
        outcome="salvage",
        title="Salvage opportunity",
        detail=f"Recovered drifting cargo pods. Credits +{gain}.",
        credits_delta=gain,
    )
