from textual.widgets import Static
from rich.text import Text
from objects.MarketConfig import MARKET_COMMODITY_NAME_BY_ID


class CargoVisualizer(Static):
    def __init__(self, ship, selected_cargo_id: str | None, id=None):
        self.ship = ship
        self.selected_cargo_id = selected_cargo_id
        super().__init__(id=id)

    def on_mount(self) -> None:
        self.refresh_visual()

    def refresh_visual(self) -> None:
        manifest = {
            cargo_id: int(quantity)
            for cargo_id, quantity in self.ship.cargo_manifest.items()
            if int(quantity) > 0
        }
        ordered_items = sorted(
            manifest.items(),
            key=lambda item: (
                MARKET_COMMODITY_NAME_BY_ID.get(item[0], item[0].title()),
                item[0],
            ),
        )

        header = "=" * 56
        output = Text()
        output.append(f"{header}\n", style="green")
        output.append("CARGO HOLD MANIFEST\n", style="bold green")
        output.append(
            f"Capacity: {self.ship.get_cargo_used()}/{self.ship.cargo_capacity}\n\n",
            style="white",
        )

        if not ordered_items:
            output.append("Cargo hold empty.\n\n", style="dim")
            output.append("Controls: [C] open cargo manifest\n", style="white")
            output.append(header, style="green")
            self.update(output)
            return

        for cargo_id, quantity in ordered_items:
            name = MARKET_COMMODITY_NAME_BY_ID.get(cargo_id, cargo_id.title())
            is_selected = cargo_id == self.selected_cargo_id
            marker = ">" if is_selected else " "
            marker_style = "bold yellow" if is_selected else "white"
            name_style = "bold yellow" if is_selected else "white"
            quantity_style = "bold yellow" if is_selected else "bold cyan"
            row = Text()
            row.append(f"{marker} ", style=marker_style)
            row.append(f"{name:24}", style=name_style)
            row.append(" | Qty ", style="white")
            row.append(f"{quantity:>4}", style=quantity_style)
            row.append(f" | id: {cargo_id}", style="dim")
            row.append("\n")
            output.append_text(row)

        output.append("\n")
        output.append("Controls: Up/Down select cargo, Enter open actions, [C] cargo manifest\n", style="white")
        output.append(header, style="green")
        self.update(output)
