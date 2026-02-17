from random import choice, randint


GALAXY_ROOTS = [
    "Andromeda",
    "Orion",
    "Cygnus",
    "Draco",
    "Perseus",
    "Carina",
    "Vela",
    "Lyra",
    "Aquila",
    "Sagan",
    "Serenity",
    "Nexus",
    "Arrakis",
    "Helios",
]

GALAXY_SUFFIXES = [
    "Expanse",
    "Reach",
    "Arm",
    "Veil",
    "Drift",
    "Cluster",
    "Spiral",
    "Marches",
    "Quadrant",
]

SYSTEM_PREFIXES = [
    "Alpha",
    "Beta",
    "Gamma",
    "Delta",
    "Epsilon",
    "Zeta",
    "Theta",
    "Lambda",
    "Sigma",
    "Omega",
    "Tau",
    "Iota",
    "Kappa",
]

SYSTEM_STARS = [
    "Sirius",
    "Vega",
    "Rigel",
    "Deneb",
    "Altair",
    "Arcturus",
    "Antares",
    "Capella",
    "Bellatrix",
    "Polaris",
    "Procyon",
]

SYSTEM_SERIES = [
    "Nova",
    "Horizon",
    "Frontier",
    "Citadel",
    "Aegis",
    "Nebula",
    "Odyssey",
    "Bastion",
    "Echo",
    "Zenith",
]

WORLD_ROOTS = [
    "Astra",
    "Krynn",
    "Erebus",
    "Rhea",
    "Talos",
    "Vesper",
    "Nereid",
    "Boreal",
    "Helion",
    "Cyrene",
    "Auron",
    "Meridian",
    "Cinder",
    "Haven",
    "Arcadia",
]

WORLD_TITLES = [
    "Prime",
    "Station",
    "Outpost",
    "Colony",
    "Harbor",
    "Point",
    "Gate",
]

ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX"]
LETTERS = ["A", "B", "C", "D", "E", "F"]
ASTEROID_CODES = ["AX", "KT", "RX", "CN", "VB", "TR"]
STATION_PREFIXES = ["Trade", "Orbital", "Freeport", "Guild", "Dock"]

BODY_TYPES = [
    "Planet",
    "Moon",
    "Asteroid",
    "Gas Giant",
    "Dwarf Planet",
    "Comet",
    "Star",
    "Neutron Star",
]


def generate_galaxy_name() -> str:
    return f"{choice(GALAXY_ROOTS)} {choice(GALAXY_SUFFIXES)}"


def generate_system_name() -> str:
    style = randint(1, 4)
    if style == 1:
        return f"{choice(SYSTEM_PREFIXES)}-{randint(100, 999)}"
    if style == 2:
        return f"{choice(SYSTEM_STARS)} {choice(ROMAN)}"
    if style == 3:
        return f"{choice(SYSTEM_SERIES)} {randint(1, 99)}"
    return f"{choice(SYSTEM_STARS)}-{choice(LETTERS)}"


def generate_body_name(system_name: str, body_type: str = "Planet") -> str:
    if body_type == "Star":
        return f"{choice(SYSTEM_STARS)} {choice(ROMAN)}"
    if body_type == "Neutron Star":
        return f"{choice(SYSTEM_STARS)}-{choice(LETTERS)} NS"
    if body_type == "Moon":
        return f"{system_name} {choice(LETTERS)}-{randint(1, 9)}"
    if body_type == "Asteroid":
        return f"{choice(ASTEROID_CODES)}-{randint(100, 999)}"
    if body_type == "Comet":
        return f"Comet {choice(WORLD_ROOTS)}-{randint(1, 30)}"
    if body_type == "Gas Giant":
        return f"{choice(WORLD_ROOTS)} Major"
    if body_type == "Dwarf Planet":
        return f"{choice(WORLD_ROOTS)} Minor"
    if body_type == "Station":
        return f"{choice(STATION_PREFIXES)} {choice(WORLD_TITLES)} {choice(LETTERS)}-{randint(1, 9)}"

    style = randint(1, 4)
    if style == 1:
        return f"{system_name} {choice(ROMAN)}"
    if style == 2:
        return f"{choice(WORLD_ROOTS)} {choice(WORLD_TITLES)}"
    if style == 3:
        return f"{choice(WORLD_ROOTS)}-{randint(1, 12)}"
    return f"New {choice(WORLD_ROOTS)}"


def generate_body_type(index: int) -> str:
    # Guarantee each system has at least one star-like primary.
    if index == 1:
        return "Star"

    roll = randint(1, 100)
    if roll <= 38:
        return "Planet"
    if roll <= 56:
        return "Moon"
    if roll <= 72:
        return "Asteroid"
    if roll <= 82:
        return "Gas Giant"
    if roll <= 90:
        return "Dwarf Planet"
    if roll <= 97:
        return "Comet"
    if roll <= 99:
        return "Neutron Star"
    return "Star"
