from textual.containers import HorizontalGroup
from textual.widgets import Log

class ShipLog(HorizontalGroup):

    def __init__(self, id=None):
        self.log_count = 0
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
        yield Log(max_lines=10_000, auto_scroll=True, highlight=True, name="Ship Log", id="shiplog")
        
        
    def on_mount(self):
        self.set_interval(0.25, self.update_log)

    def update_log(self):
        log = self.query_one("#shiplog")
        if self.is_scrolling:
            return
        self.log_count +=1
        line_no = self.log_count
        line = self.TEXT[self.log_count % len(self.TEXT)]
        log.write_line(f"Entry[{line_no}]= {line!r}")
