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
        selected_system_id = self.ship.get_selected_jump_system_id()
        current_system = self.galaxy.get_celestial_system(current_system_id)
        ordered_ids = self.ship.get_ordered_jump_system_ids()
        systems = [self.galaxy.get_celestial_system(system_id) for system_id in ordered_ids]

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

        visible_systems, first_visible, last_visible = self._visible_window(
            systems, selected_system_id
        )

        if len(visible_systems) < len(systems):
            output.append(
                f"Showing {first_visible}-{last_visible} of {len(systems)} systems\n\n",
                style="dim",
            )

        for system in visible_systems:
            is_current = system.id == current_system_id
            is_selected = system.id == selected_system_id
            is_visited = system.id in self.ship.visited_systems
            distance = system.coordinates.get_distance(current_system.coordinates)
            position = int((distance / max_distance) * (track_width - 1))
            marker = "@"
            marker_style = "bold cyan"
            if not is_current:
                marker = "+" if is_visited else "*"
                marker_style = "bold green" if is_visited else "bold yellow"

            row = Text()
            row_prefix = ">" if is_selected else " "
            row_style = "yellow" if is_selected else "white"
            if is_current:
                row_prefix = "@"
                row_style = "cyan"
            row.append(f"{row_prefix}[{system.id:02d}] |", style=row_style)
            for i in range(track_width):
                if i == position:
                    row.append(marker, style=marker_style)
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
            row.append(f"{system.name[:20]:20}  ", style=name_style)
            row.append(f"{'VISITED' if is_visited else 'UNSEEN ':7}  ", style="green" if is_visited else "white")
            row.append(f"{self.ship.format_interstellar_distance(distance):>12}", style="white")
            row.append("\n")
            output.append_text(row)

        output.append("\n")
        output.append("Legend: ", style="white")
        output.append("@ current system, ", style="bold cyan")
        output.append("> selected target, ", style="bold yellow")
        output.append("green names = visited, ", style="bold green")
        output.append("@ current marker, ", style="bold cyan")
        output.append("+ visited marker, ", style="bold green")
        output.append("* unseen marker\n", style="bold yellow")
        output.append("Controls: Up/Down select target, Enter open actions, [J] jump navigation\n", style="white")
        output.append(header, style="green")
        self.update(output)

    def _visible_window(self, systems: list, selected_id: int) -> tuple[list, int, int]:
        total = len(systems)
        if total <= 0:
            return [], 0, 0
        max_rows = max(8, self.size.height - 13)
        if total <= max_rows:
            return systems, 1, total

        selected_index = 0
        for idx, system in enumerate(systems):
            if system.id == selected_id:
                selected_index = idx
                break

        half = max_rows // 2
        start = max(0, min(selected_index - half, total - max_rows))
        end = start + max_rows
        return systems[start:end], start + 1, end
