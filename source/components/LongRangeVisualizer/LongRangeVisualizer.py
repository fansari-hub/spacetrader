from random import Random
from textual.widgets import Static
from rich.text import Text


class LongRangeVisualizer(Static):
    def __init__(self, ship, galaxy, id=None):
        self.ship = ship
        self.galaxy = galaxy
        super().__init__(id=id)

    def on_mount(self) -> None:
        self.refresh_visual()

    def refresh_visual(self) -> None:
        current_system_id = self.ship.get_current_system()
        current_system = self.galaxy.get_celestial_system(current_system_id)
        systems = list(self.galaxy.celestial_systems)

        if not systems:
            self.update("LONG-RANGE SCANNER OFFLINE\nNo stellar systems found.")
            return

        distances = [
            system.coordinates.get_distance(current_system.coordinates) for system in systems
        ]
        max_distance = max(max(distances), 1.0)
        track_width = 30
        rng = Random(current_system_id * 6151 + len(systems))

        header = "=" * 56
        noise = "".join(rng.choice(".:*+") for _ in range(56))
        output = Text()
        output.append(f"{header}\n", style="green")
        output.append("LONG-RANGE CARTOGRAPHY // FROM ", style="bold green")
        output.append(f"{current_system.name}\n", style="bold cyan")
        output.append(f"Systems detected: {len(systems)}\n", style="white")
        output.append(
            f"Range scale: 0 to {self.ship.format_interstellar_distance(max_distance)}\n",
            style="white",
        )
        output.append(f"{noise}\n\n", style="bright_black")

        for system in systems:
            is_current = system.id == current_system_id
            is_visited = system.id in self.ship.visited_systems
            distance = system.coordinates.get_distance(current_system.coordinates)
            position = int((distance / max_distance) * (track_width - 1))
            marker = "@"
            marker_style = "bold cyan"
            if not is_current:
                marker = "+" if is_visited else "*"
                marker_style = "bold green" if is_visited else "bold yellow"

            row = Text()
            row_prefix = "▶" if is_current else " "
            row.append(f"{row_prefix}[{system.id:02d}] |", style="cyan" if is_current else "white")
            for i in range(track_width):
                if i == position:
                    row.append(marker, style=marker_style)
                else:
                    row.append("-", style="bright_black")
            row.append("|  ")
            name_style = "bold cyan" if is_current else ("bold green" if is_visited else "white")
            row.append(f"{system.name[:20]:20}  ", style=name_style)
            row.append(f"{'VISITED' if is_visited else 'UNSEEN ':7}  ", style="green" if is_visited else "white")
            row.append(f"{self.ship.format_interstellar_distance(distance):>12}", style="white")
            row.append("\n")
            output.append_text(row)

        output.append("\n")
        output.append("Legend: ", style="white")
        output.append("▶ current system, ", style="bold cyan")
        output.append("green names = visited, ", style="bold green")
        output.append("@ current marker, ", style="bold cyan")
        output.append("+ visited marker, ", style="bold green")
        output.append("* unseen marker\n", style="bold yellow")
        output.append(header, style="green")
        self.update(output)
