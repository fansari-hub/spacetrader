from textual.containers import VerticalGroup, HorizontalGroup
from textual.widgets import DataTable, Label, Button
from ..ShipLog.ShipLog import ShipLog

class TableList(VerticalGroup):

    def __init__(self, id=None, headers=("Column1", "Columns2", "Column3"), data=[("Data", "Not", "Set")], title=None):
        self.headers = headers
        self.data = data
        self.title = title
        super().__init__(id=id)

    def compose(self):
        if self.title:
            yield Label(self.title)
            yield Label("")
        yield DataTable(id = "datatable", cursor_type="row")
        with HorizontalGroup(classes="datatable_buttons"):
            yield Button("Confirm", id="btn_cmd_confirm", variant="primary")
            yield Button("Cancel", id="btn_cmd_cancel", variant="error")
    
    def on_mount(self):
        get_log = self.app.query_one(ShipLog)
        get_log.update_log("Opened interface -> " + self.title)    
        table = self.query_one("#datatable")
        table.add_columns(*self.headers)
        table.add_rows(self.data)

    def on_unmount(self):
        get_log = self.app.query_one(ShipLog)
        get_log.update_log("Closed interface -> " + self.title)       


    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        match button_id:
            case "btn_cmd_confirm":
                get_log = self.app.query_one(ShipLog)
                table = self.query_one("#datatable")
                get_log.update_log(f"{self.title} -> {table.cursor_coordinate}")    
                self.remove()
            case "btn_cmd_cancel":
                self.remove()         