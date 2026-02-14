from random import Random
from textual.widgets import Static
from rich.text import Text


TYPE_GLYPHS = {
    "Star": "*",
    "Neutron Star": "#",
    "Planet": "o",
    "Gas Giant": "O",
    "Moon": "m",
    "Asteroid": ".",
    "Dwarf Planet": "d",
    "Comet": "~",
}

TYPE_COLORS = {
    "Star": "bold yellow",
    "Neutron Star": "bold magenta",
    "Planet": "bold cyan",
    "Gas Giant": "bold blue",
    "Moon": "bold white",
    "Asteroid": "bright_black",
    "Dwarf Planet": "bold green",
    "Comet": "bold bright_white",
}


class SystemVisualizer(Static):
    def __init__(self, ship, galaxy, id=None):
        self.ship = ship
        self.galaxy = galaxy
        super().__init__(id=id)

    def on_mount(self) -> None:
        self.refresh_visual()

    def refresh_visual(self) -> None:
        system_id = self.ship.get_current_system()
        local_id = self.ship.get_current_location()
        system = self.galaxy.get_celestial_system(system_id)
        members = list(system.members)

        if not members:
            self.update("SYSTEM CARTOGRAPHY OFFLINE\nNo objects found in this system.")
            return

        ship_body = members[max(0, min(local_id - 1, len(members) - 1))]
        distances = [
            member.coordinates.get_distance(ship_body.coordinates) for member in members
        ]
        max_distance = max(max(distances), 1.0)
        track_width = 30
        rng = Random(system_id * 9973 + len(members))

        header = "=" * 56
        noise = "".join(rng.choice(".:*+") for _ in range(56))
        visited_locations = self.ship.visited_locations_by_system.get(system_id, set())

        output = Text()
        output.append(f"{header}\n", style="green")
        output.append("SYSTEM CARTOGRAPHY // ", style="bold green")
        output.append(f"{system.name}\n", style="bold cyan")
        output.append(f"Objects detected: {len(members)}\n", style="white")
        output.append("Ship anchor: ", style="white")
        output.append(f"{ship_body.name}", style="bold cyan")
        output.append(f" [{ship_body.type}]\n", style=TYPE_COLORS.get(ship_body.type, "white"))
        output.append(
            f"Range scale: 0 to {self.ship.format_local_distance(max_distance)}\n",
            style="white",
        )
        output.append(f"{noise}\n\n", style="bright_black")

        for member in members:
            is_current = member.id == ship_body.id
            is_visited = member.id in visited_locations
            distance = member.coordinates.get_distance(ship_body.coordinates)
            position = int((distance / max_distance) * (track_width - 1))
            glyph = TYPE_GLYPHS.get(member.type, "?")
            row = Text()
            row_marker = "▶" if is_current else " "
            row.append(f"{row_marker}[{member.id:02d}] |", style="cyan" if is_current else "white")

            for i in range(track_width):
                if i == 0:
                    row.append("@", style="bold cyan")
                elif i == position:
                    row.append(glyph, style=TYPE_COLORS.get(member.type, "bold white"))
                else:
                    row.append("-", style="bright_black")

            row.append("|  ")
            name_style = "bold cyan" if is_current else ("bold green" if is_visited else "white")
            row.append(f"{member.name[:18]:18}  ", style=name_style)
            row.append(f"{member.type[:12]:12}  ", style=TYPE_COLORS.get(member.type, "white"))
            row.append(f"{self.ship.format_local_distance(distance):>16}", style="white")
            row.append("\n")
            output.append_text(row)

        output.append("\n")
        output.append("Legend: ", style="white")
        output.append("▶ current location, ", style="bold cyan")
        output.append("green names = visited, ", style="bold green")
        output.append("@ ship anchor, ", style="cyan")
        output.append("* # o O m . ~ body glyphs\n", style="white")
        output.append(header, style="green")
        self.update(output)
