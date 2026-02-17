from textual.containers import VerticalScroll
from textual.widgets import Label
from rich.text import Text
from ..StatusBar.StatusBar import StatusBar

class ShipStats(VerticalScroll):
    def __init__(self, ship, id=None):
        self.ship = ship
        super().__init__(id=id)

    def compose(self):
        label_width = 12
        yield Label("", id="stats_resources")
        yield Label("")
        yield StatusBar(self.ship.get_shields(), "Shields", totalInt=100, id="shields", label_width=label_width)
        yield StatusBar(self.ship.get_engine_power(), "Engines", totalInt=100, id="engines", label_width=label_width)
        yield StatusBar(self.ship.get_structure(), "Structure", totalInt=100, id="structures", label_width=label_width)
        yield StatusBar(self.ship.lifesupport_power, "Life Support", totalInt=100, id="lifesupport", label_width=label_width)

    def on_mount(self) -> None:
        self.refresh_from_ship()

    def refresh_from_ship(self) -> None:
        self.query_one("#shields", StatusBar).update_value(self.ship.get_shields())
        self.query_one("#engines", StatusBar).update_value(self.ship.get_engine_power())
        self.query_one("#structures", StatusBar).update_value(self.ship.get_structure())
        self.query_one("#lifesupport", StatusBar).update_value(self.ship.lifesupport_power)
        resources = Text()
        resources.append(f"Credits: {self.ship.credits} cr", style="white")
        resources.append("  |  ", style="dim")
        resources.append(
            f"Cargo: {self.ship.get_cargo_used()}/{self.ship.cargo_capacity}",
            style="white",
        )
        resources.append("  |  ", style="dim")
        resources.append("Fuel: ", style="white")
        resources.append(str(self.ship.fuel), style=self._fuel_style(self.ship.fuel))
        self.query_one("#stats_resources", Label).update(resources)

    def _fuel_style(self, fuel: int) -> str:
        if fuel >= 60:
            return "bold green"
        if fuel >= 30:
            return "bold yellow"
        return "bold red"
