from textual.containers import HorizontalGroup, VerticalGroup
from ..ShipStats.ShipStats import ShipStats
from ..ShipControls.ShipControls import ShipControls
from ..ShipLog.ShipLog import ShipLog
from ..ShipComms.ShipComms import ShipComms
from ..ViewPort.ViewPort import ViewPort

class MainInterface(VerticalGroup):

    def __init__(self, ship, galaxy, id=None):
        self.ship = ship
        self.galaxy = galaxy
        super().__init__(id=id)

    def compose(self):
        with HorizontalGroup():
            with VerticalGroup(classes="interface_left"):
                yield ViewPort(ship=self.ship, galaxy=self.galaxy, id="viewport")
                yield ShipLog()
            with VerticalGroup(classes="interface_right"):
                yield ShipStats()
                yield ShipControls(ship=self.ship)
                yield ShipComms()
