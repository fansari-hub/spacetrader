from textual.containers import VerticalScroll
from random import randrange
from ..StatusBar.StatusBar import StatusBar

class ShipStats(VerticalScroll):
    BINDINGS = [("v", "random_values", "Random Stats")]

    def compose(self):
        yield StatusBar(50, "Shields", totalInt=100, id="shields")
        yield StatusBar(75, "Engines", totalInt=100, id="engines")
        yield StatusBar(25, "Structure", totalInt=100, id="structures")
        yield StatusBar(100, "Life Support", totalInt=100, id="lifesupport")

    def action_random_values(self) -> None:
        self.query_one("#shields").update_value(randrange(100))
        self.query_one("#engines").update_value(randrange(100))
        self.query_one("#structures").update_value(randrange(100))
        self.query_one("#lifesupport").update_value(randrange(100))