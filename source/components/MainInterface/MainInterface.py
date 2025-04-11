from textual.containers import HorizontalGroup, VerticalGroup
from ..ShipStats.ShipStats import ShipStats
from ..ShipControls.ShipControls import ShipControls
from ..ShipLog.ShipLog import ShipLog
from ..ShipComms.ShipComms import ShipComms

class MainInterface(VerticalGroup):
    def compose(self):
        with HorizontalGroup():
            yield ShipStats()
            yield ShipControls()
        with HorizontalGroup():
            yield ShipLog()
        with HorizontalGroup():
            yield ShipComms()