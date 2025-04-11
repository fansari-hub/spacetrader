from textual.containers import HorizontalGroup, VerticalGroup
from textual.widgets import Log, Button

class ShipComms(VerticalGroup):

    def __init__(self, id=None):
        self.comm_count = 0
        self.TEXT = """Starting
Captain's log, started something
I am sitting here on my comfy chair
Number one is missing
Beverly is gone
I like green ale
and where is scotty gone
This must be Q's fault
This is more log
""".splitlines()

        super().__init__(id=id)

    def compose(self):
        with HorizontalGroup():
            yield Log(max_lines=10_000, auto_scroll=True, highlight=True, name="Ship Comm", id="shipcomm")
        with HorizontalGroup():
            yield Button("Hail\nChannel")
            yield Button("Open\nChannel")
            yield Button("Close\nChannel")
        
        
    def on_mount(self):
        self.set_interval(0.50, self.update_comm)

    def update_comm(self):
        log = self.query_one("#shipcomm")
        if self.is_scrolling:
            return
        self.comm_count +=1
        line_no = self.comm_count
        line = self.TEXT[self.comm_count % len(self.TEXT)]
        log.write_line(f"Entry[{line_no}]= {line!r}")
