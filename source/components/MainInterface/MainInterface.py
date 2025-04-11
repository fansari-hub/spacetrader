from textual.containers import HorizontalGroup
from ..ShipStats.ShipStats import ShipStats
from ..ShipControls.ShipControls import ShipControls

class MainInterface(HorizontalGroup):
    def compose(self):
        yield ShipStats()
        yield ShipControls()