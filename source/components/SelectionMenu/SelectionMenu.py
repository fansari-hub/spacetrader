from textual.containers import VerticalGroup
from textual.widgets import OptionList, Label
from textual.widgets.option_list import Option

class SelectionMenu(VerticalGroup):
    BINDINGS = [
        ("enter", "confirm", "Confirm"),
        ("escape", "cancel", "Cancel"),
    ]

    def __init__(self, id=None, option_values=None, title=None, callback=None):
        self.option_values = option_values
        self.title = title
        self.callback = callback
        super().__init__(id=id)

    def compose(self):
        if self.title:
            yield Label(self.title)
            yield Label("")
        yield OptionList(Option("Select Item"), id="optionlist")
        yield Label("[Enter] Confirm   [Esc] Cancel", markup=False, id="selection_hint")
    
    def on_mount(self) -> None:
        #get_log = self.app.query_one(ShipLog)
        #get_log.update_log("Opened interface -> " + self.title)    
        option_object = self.query_one("#optionlist")
        if self.option_values:
            option_object.clear_options()
            for option in self.option_values:
                option_object.add_option(option)
            # Ensure confirm works immediately without requiring arrow movement first.
            if len(self.option_values) > 0:
                option_object.highlighted = 0

    def on_unmount(self) -> None:
        #get_log = self.app.query_one(ShipLog)
        #get_log.update_log("Closed interface -> " + self.title)
        pass

    def action_confirm(self) -> None:
        option_object = self.query_one("#optionlist")
        option_highlighted = option_object.highlighted
        if option_highlighted is not None:
            option_index = option_object.get_option_at_index(option_object.highlighted)
            if self.callback:
                self.callback(str(option_index.prompt))
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
