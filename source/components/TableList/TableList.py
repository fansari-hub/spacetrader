from textual.containers import VerticalGroup, HorizontalGroup
from textual.widgets import DataTable, Label, Button

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
        yield DataTable(id = "datatable")
        with HorizontalGroup(classes="datatable_buttons"):
            yield Button("Confirm", id="btn_cmd_confirm", variant="primary")
            yield Button("Cancel", id="btn_cmd_cancel", variant="error")
    
    def on_mount(self):
        table = self.query_one("#datatable")
        table.add_columns(*self.headers)
        table.add_rows(self.data)