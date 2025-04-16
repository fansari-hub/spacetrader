from textual.containers import HorizontalGroup, VerticalGroup
from ..ShipStats.ShipStats import ShipStats
from ..ShipControls.ShipControls import ShipControls
from ..ShipLog.ShipLog import ShipLog
from ..ShipComms.ShipComms import ShipComms
from ..SelectionMenu.SelectionMenu import SelectionMenu
from ..TableList.TableList import TableList
from ..ViewPort.ViewPort import ViewPort

class MainInterface(VerticalGroup):
    def compose(self):
        with HorizontalGroup():
            with VerticalGroup(classes="interface_left"):
                yield ViewPort(id = "viewport")
                yield ShipLog()
            with VerticalGroup(classes="interface_right"):
                yield ShipStats()
                yield ShipControls()
                yield ShipComms()