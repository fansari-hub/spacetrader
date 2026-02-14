from textual.containers import HorizontalGroup
from textual.widgets import Label

class LocationIndicator(HorizontalGroup):
    def __init__(self, ship, galaxy, id=None):
        self.ship = ship
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
        self._refresh_labels()

    def update_location(self, localID : int) -> None:
        self._refresh_labels()

    def _sync_from_ship(self) -> None:
        self.systemID = self.ship.get_current_system()
        self.localID = self.ship.get_current_location()

    def _refresh_labels(self) -> None:
        self._sync_from_ship()
        system = self.galaxy.celestial_systems[self.systemID - 1]
        self.query_one("#label_coord_system", Label).update(system.name)
        if system.members and 1 <= self.localID <= len(system.members):
            self.query_one("#label_coord_local", Label).update(system.members[self.localID - 1].name)
        elif system.members:
            self.localID = 1
            self.query_one("#label_coord_local", Label).update(system.members[0].name)
        else:
            self.localID = 0
            self.query_one("#label_coord_local", Label).update("N/A")
