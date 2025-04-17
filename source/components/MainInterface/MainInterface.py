from textual.containers import HorizontalGroup, VerticalGroup
from ..ShipStats.ShipStats import ShipStats
from ..ShipControls.ShipControls import ShipControls
from ..ShipLog.ShipLog import ShipLog
from ..ShipComms.ShipComms import ShipComms
from ..SelectionMenu.SelectionMenu import SelectionMenu
from ..TableList.TableList import TableList
from ..ViewPort.ViewPort import ViewPort
from ..LocationIndicator.LocationIndicator import LocationIndicator

class MainInterface(VerticalGroup):

    def __init__(self, ship, galaxy, id=None):
        self.ship = ship
        self.galaxy = galaxy
        super().__init__(id=id)

    def compose(self):
        with HorizontalGroup():
            with VerticalGroup(classes="interface_left"):
                yield ViewPort(id = "viewport")
                yield ShipLog()
                yield LocationIndicator(ship=self.ship, galaxy=self.galaxy)
            with VerticalGroup(classes="interface_right"):
                yield ShipStats()
                yield ShipControls(ship=self.ship)
                yield ShipComms()