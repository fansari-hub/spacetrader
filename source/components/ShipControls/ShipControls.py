from textual.containers import HorizontalGroup, VerticalGroup
from textual.widgets import Button, Switch

class ShipControls(HorizontalGroup):

    def __init__(self, id=None):
        super().__init__(id=id)

    def compose(self):
        with VerticalGroup():
            yield Button("Long-range\nScan", variant="primary")
            yield Button("Short-rang\nScan", variant="primary")
            yield Button("Local\nDestination", variant="primary")
        with VerticalGroup():
            yield Button("Jump to\nSystem")
            yield Button("Dock or Land\nProcedure")
            yield Button("Extract\nResources")