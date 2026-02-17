from textual.containers import VerticalGroup
from textual.widgets import DataTable, Label

class TableList(VerticalGroup):
    BINDINGS = [
        ("enter", "confirm", "Confirm"),
        ("escape", "cancel", "Cancel"),
    ]

    def __init__(self, id=None, headers=("Column1", "Columns2", "Column3"), data=[("Data", "Not", "Set")], title=None, callback=None):
        self.headers = headers
        self.data = data
        self.title = title
        self.callback = callback
        super().__init__(id=id)

    def compose(self):
        if self.title:
            yield Label(self.title)
            yield Label("")
        yield DataTable(id = "datatable", cursor_type="row", classes="datatable_data")
        yield Label("[Enter] Confirm   [Esc] Cancel", markup=False, id="table_hint")
    
    def on_mount(self) -> None:
        #get_log = self.app.query_one(ShipLog)
        #get_log.update_log("Opened interface -> " + self.title)    
        table = self.query_one("#datatable")
        table.add_columns(*self.headers)
        table.add_rows(self.data)

    def on_unmount(self) -> None:
        #get_log = self.app.query_one(ShipLog)
        #get_log.update_log("Closed interface -> " + self.title)
        pass


    def action_confirm(self) -> None:
        table = self.query_one("#datatable")
        if self.callback:
            self.callback(table.get_cell_at((table.cursor_coordinate.row, 0)))
        self._close_and_restore(force_restore=False)

    def action_cancel(self) -> None:
        self._close_and_restore(force_restore=True)

    def _close_and_restore(self, force_restore: bool) -> None:
        parent = self.parent
        if parent and self in parent.children:
            self.remove()
        self.call_after_refresh(lambda: self._restore_if_needed(force_restore))

    def _restore_if_needed(self, force_restore: bool) -> None:
        from ..ViewPort.ViewPort import ViewPort
        viewport = self.app.query_one(ViewPort)
        content = viewport.query_one("#viewport_content")
        if force_restore or not content.children:
            viewport.refresh_current_display()
