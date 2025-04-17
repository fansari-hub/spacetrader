from textual.containers import HorizontalGroup, VerticalGroup
from textual.widgets import Log, Button

class ShipComms(VerticalGroup):

    def __init__(self, id=None):
        self.comm_count = 0
        super().__init__(id=id)

    def compose(self):
        with HorizontalGroup():
            yield Log(max_lines=10_000, auto_scroll=True, highlight=True, name="Ship Comm", id="shipcomm")
        with HorizontalGroup():
            yield Button("Hail\nChannel")
            yield Button("Open\nChannel")
            yield Button("Close\nChannel")
        
        
    def on_mount(self) -> None:
        #self.set_interval(0.50, self.update_comm)
        pass

    def update_comm(self, text) -> None:
        log = self.query_one("#shipcomm")
        if self.is_scrolling:
            return
        self.comm_count +=1
        line_no = self.comm_count
        log.write_line(f"Entry[{line_no}]= {text!r}")
        # line = self.TEXT[self.comm_count % len(self.TEXT)]
        # log.write_line(f"Entry[{line_no}]= {line!r}")
