from textual.containers import VerticalGroup, HorizontalGroup
from textual.widgets import OptionList, Label, Button
from textual.widgets.option_list import Option
from ..ShipLog.ShipLog import ShipLog

class SelectionMenu(VerticalGroup):

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
        with HorizontalGroup(classes="dialogue_buttons"):
            yield Button("Confirm", id="btn_cmd_confirm", variant="primary")
            yield Button("Cancel", id="btn_cmd_cancel", variant="error")
    
    def on_mount(self) -> None:
        #get_log = self.app.query_one(ShipLog)
        #get_log.update_log("Opened interface -> " + self.title)    
        option_object = self.query_one("#optionlist")
        if self.option_values:
            option_object.clear_options()
            for option in self.option_values:
                option_object.add_option(option)

    def on_unmount(self) -> None:
        #get_log = self.app.query_one(ShipLog)
        #get_log.update_log("Closed interface -> " + self.title)
        pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        match button_id:
            case "btn_cmd_confirm":
                get_log = self.app.query_one(ShipLog)
                option_object = self.query_one("#optionlist")
                option_highlighted = option_object.highlighted
                if option_highlighted:
                    option_index = option_object.get_option_at_index(option_object.highlighted)
                    #get_log.update_log(self.title + " -> " + option_index.prompt)
                    if self.callback:
                        self.callback(option_index.prompt)    
                self.remove()
            case "btn_cmd_cancel":
                self.remove()