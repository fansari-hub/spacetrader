from textual.containers import HorizontalGroup
from textual.widgets import Label

class LocationIndicator(HorizontalGroup):
    def __init__(self, ship, galaxy, id=None):
        self.galaxy = galaxy
        self.localID = ship.get_current_location()
        self.systemID = ship.get_current_system()
        super().__init__(id=id)

    def compose(self):
        yield Label("Current Location: ")
        yield Label(f"{self.galaxy.celestial_systems[self.systemID - 1].name}", id="label_coord_system")
        yield Label("::")
        yield Label(f"{self.galaxy.celestial_systems[self.systemID - 1].members[self.localID -1].name}", id="label_coord_local")

    def update_system(self, systemID: int) -> None:
        self.query_one("#label_coord_system").renderable = self.galaxy.celestial_systems[systemID - 1].name

    def update_location(self, localID : int) -> None:
        self.query_one("#label_coord_local").renderable = self.galaxy.celestial_systems[self.systemID - 1].members[localID -1].name

