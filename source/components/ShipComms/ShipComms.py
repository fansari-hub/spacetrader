from textual.containers import VerticalGroup
from textual.widgets import Label, OptionList
from textual.widgets.option_list import Option
from rich.text import Text

class ShipComms(VerticalGroup):

    def __init__(self, id=None):
        self.menu_active = False
        self.menu_callback = None
        self.menu_values = []
        self.menu_title = ""
        super().__init__(id=id)

    def compose(self):
        with VerticalGroup(id="comms_menu_box"):
            yield Label("", id="comms_menu_title")
            yield OptionList(id="comms_menu_options")
            yield Label("", id="comms_menu_hint", markup=False)
        
        
    def on_mount(self) -> None:
        self.close_menu()

    def has_active_menu(self) -> bool:
        return self.menu_active

    def open_menu(self, option_values: list, title: str, callback=None, selected_index: int | None = None) -> None:
        self.menu_active = True
        self.menu_callback = callback
        self.menu_values = []
        self.menu_title = title
        self.remove_class("comms-idle")
        self.add_class("comms-active")
        self.query_one("#comms_menu_title", Label).update(title)
        self.query_one("#comms_menu_hint", Label).update("COMMAND INPUT REQUIRED  [Up/Down] Select  [Enter] Confirm  [Esc] Cancel")
        option_list = self.query_one("#comms_menu_options", OptionList)
        option_list.clear_options()
        for menu_entry in option_values:
            display_label, callback_value = self._normalize_menu_entry(menu_entry)
            option_list.add_option(Option(display_label))
            self.menu_values.append(callback_value)
        if option_values:
            if selected_index is None:
                option_list.highlighted = 0
            else:
                option_list.highlighted = max(0, min(int(selected_index), len(option_values) - 1))
        self._set_viewport_mode("Action Menu (Comms)")

    def close_menu(self) -> None:
        self.menu_active = False
        self.menu_callback = None
        self.menu_values = []
        self.menu_title = ""
        self.remove_class("comms-active")
        self.add_class("comms-idle")
        self.query_one("#comms_menu_title", Label).update("Channel Menu (Idle)")
        self.query_one("#comms_menu_hint", Label).update("No input required. Use navigation keys to select targets.")
        option_list = self.query_one("#comms_menu_options", OptionList)
        option_list.clear_options()
        option_list.add_option(Option("No active command menu"))
        option_list.highlighted = 0
        self._restore_viewport_mode()

    def show_action_preview(self, title: str, option_values: list[str]) -> None:
        if self.menu_active:
            return
        self.remove_class("comms-active")
        self.add_class("comms-idle")
        self.query_one("#comms_menu_title", Label).update(f"Action Preview: {title}")
        self.query_one("#comms_menu_hint", Label).update("Preview only. Press [Enter] to open command menu.")
        option_list = self.query_one("#comms_menu_options", OptionList)
        option_list.clear_options()
        if option_values:
            for option_text in option_values:
                option_list.add_option(Option(option_text))
            option_list.highlighted = 0
        else:
            option_list.add_option(Option("No actions available"))
            option_list.highlighted = 0

    def clear_action_preview(self) -> None:
        if self.menu_active:
            return
        self.query_one("#comms_menu_title", Label).update("Channel Menu (Idle)")
        self.query_one("#comms_menu_hint", Label).update("No input required. Use navigation keys to select targets.")
        option_list = self.query_one("#comms_menu_options", OptionList)
        option_list.clear_options()
        option_list.add_option(Option("No active command menu"))
        option_list.highlighted = 0

    def menu_cursor_up(self) -> bool:
        if not self.menu_active:
            return False
        self.query_one("#comms_menu_options", OptionList).action_cursor_up()
        return True

    def menu_cursor_down(self) -> bool:
        if not self.menu_active:
            return False
        self.query_one("#comms_menu_options", OptionList).action_cursor_down()
        return True

    def menu_confirm(self) -> bool:
        if not self.menu_active:
            return False
        option_list = self.query_one("#comms_menu_options", OptionList)
        highlighted = option_list.highlighted
        selected_value = None
        if highlighted is not None and 0 <= highlighted < len(self.menu_values):
            selected_value = self.menu_values[highlighted]
        callback = self.menu_callback
        self.close_menu()
        if callback and selected_value is not None:
            callback(selected_value)
        return True

    def menu_cancel(self) -> bool:
        if not self.menu_active:
            return False
        self.close_menu()
        return True

    def _set_viewport_mode(self, mode_text: str) -> None:
        from ..ViewPort.ViewPort import ViewPort
        try:
            viewport = self.app.query_one(ViewPort)
        except Exception:
            return
        viewport._set_mode_indicator(mode_text)

    def _restore_viewport_mode(self) -> None:
        from ..ViewPort.ViewPort import ViewPort
        try:
            viewport = self.app.query_one(ViewPort)
        except Exception:
            return
        viewport.refresh_current_display()
        viewport.focus()

    def _normalize_menu_entry(self, menu_entry):
        if isinstance(menu_entry, dict):
            label = menu_entry.get("label", "")
            value = menu_entry.get("value", "")
            return label, value
        if isinstance(menu_entry, tuple) and len(menu_entry) == 2:
            return menu_entry[0], menu_entry[1]
        if isinstance(menu_entry, Text):
            return menu_entry, str(menu_entry)
        return str(menu_entry), str(menu_entry)
