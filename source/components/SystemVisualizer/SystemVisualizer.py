from random import Random
from textual.widgets import Static
from rich.text import Text


TYPE_GLYPHS = {
    "Star": "*",
    "Neutron Star": "#",
    "Planet": "o",
    "Gas Giant": "O",
    "Moon": "m",
    "Station": "S",
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
    "Station": "bold green",
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
        selected_local_id = self.ship.get_selected_local_id()
        system = self.galaxy.get_celestial_system(system_id)
        ordered_ids = self.ship.get_ordered_local_ids()
        members = [system.members[member_id - 1] for member_id in ordered_ids]

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

        visible_members, first_visible, last_visible = self._visible_window(
            members, selected_local_id
        )

        if len(visible_members) < len(members):
            output.append(
                f"Showing {first_visible}-{last_visible} of {len(members)} objects\n\n",
                style="dim",
            )

        for member in visible_members:
            is_current = member.id == ship_body.id
            is_selected = member.id == selected_local_id
            is_visited = member.id in visited_locations
            distance = member.coordinates.get_distance(ship_body.coordinates)
            position = int((distance / max_distance) * (track_width - 1))
            glyph = TYPE_GLYPHS.get(member.type, "?")
            row = Text()
            row_marker = ">" if is_selected else " "
            row_style = "yellow" if is_selected else "white"
            if is_current:
                row_marker = "@"
                row_style = "cyan"
            row.append(f"{row_marker}[{member.id:02d}] |", style=row_style)

            for i in range(track_width):
                if i == 0:
                    row.append("@", style="bold cyan")
                elif i == position:
                    row.append(glyph, style=TYPE_COLORS.get(member.type, "bold white"))
                else:
                    row.append("-", style="bright_black")

            row.append("|  ")
            if is_current:
                name_style = "bold cyan"
            elif is_selected:
                name_style = "bold yellow"
            elif is_visited:
                name_style = "bold green"
            else:
                name_style = "white"
            row.append(f"{member.name[:18]:18}  ", style=name_style)
            row.append(f"{member.type[:12]:12}  ", style=TYPE_COLORS.get(member.type, "white"))
            row.append(f"{self.ship.format_local_distance(distance):>16}", style="white")
            row.append("\n")
            output.append_text(row)

        output.append("\n")
        output.append("Legend: ", style="white")
        output.append("@ current location, ", style="bold cyan")
        output.append("> selected target, ", style="bold yellow")
        output.append("green names = visited, ", style="bold green")
        output.append("@ ship anchor, ", style="cyan")
        output.append("* # o O m S . ~ body glyphs\n", style="white")
        output.append("Controls: Up/Down select target, Enter open actions, [G] goto local destination\n", style="white")
        output.append(header, style="green")
        self.update(output)

    def _visible_window(self, members: list, selected_id: int) -> tuple[list, int, int]:
        total = len(members)
        if total <= 0:
            return [], 0, 0
        max_rows = max(8, self.size.height - 14)
        if total <= max_rows:
            return members, 1, total

        selected_index = 0
        for idx, member in enumerate(members):
            if member.id == selected_id:
                selected_index = idx
                break

        half = max_rows // 2
        start = max(0, min(selected_index - half, total - max_rows))
        end = start + max_rows
        return members[start:end], start + 1, end
