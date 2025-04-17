from textual.containers import HorizontalGroup, VerticalGroup
from textual.widgets import Button
from ..ViewPort.ViewPort import ViewPort
from ..ShipLog.ShipLog import ShipLog
from ..LocationIndicator.LocationIndicator import LocationIndicator

class ShipControls(HorizontalGroup):

    BINDINGS = [
        ("l", "btn_longrange", "Long-Range Scanner"),
        ("s", "btn_shortrange", "Short-Range Scanner"),
        ("d", "btn_localdest", "Local Destination"),
        ("j", "btn_jump", "Jump to System"),
        ("p", "btn_dock", "Dock or Land"),
        ("e", "btn_extract", "Extract Resources"),
    ]

    def __init__(self, ship, id=None):
        self.ship = ship
        super().__init__(id=id)

    def compose(self):
        with VerticalGroup():
            yield Button("Long-range\nScan", id="btn_cmd_longrange", variant="primary")
            yield Button("Short-rang\nScan", id="btn_cmd_shortrange", variant="primary")
            yield Button("Local\nDestination", id="btn_cmd_dest", variant="primary")
        with VerticalGroup():
            yield Button("Jump to\nSystem", id="btn_cmd_jump")
            yield Button("Dock or Land\nProcedure", id="btn_cmd_dock")
            yield Button("Extract\nResources", id="btn_cmd_extract")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        button_id = event.button.id
        match button_id:
            case "btn_cmd_longrange":
                self.action_btn_longrange()
            case "btn_cmd_shortrange":
                self.action_btn_shortrange()
            case "btn_cmd_dest":
                self.action_btn_localdest()
            case "btn_cmd_jump":
                self.action_btn_jump()
            case "btn_cmd_dock":
                self.action_btn_dock()
            case "btn_cmd_extract":
                self.action_btn_extract()

    def action_btn_longrange(self) -> None:
        get_log = self.app.query_one(ShipLog)
        get_log.update_log("Started Long Range Scanner...")
        get_viewport = self.app.query_one(ViewPort)
        get_viewport.present_loadbar(label="Long Range Scanner", targetvalue=100, animation_interval=25, callback=self.behaviour_longrange)
        
    def action_btn_shortrange(self) -> None:
        get_log = self.app.query_one(ShipLog)
        get_log.update_log("Started Short Range Scanner...")
        get_viewport = self.app.query_one(ViewPort)
        get_viewport.present_loadbar(label="Short Range Scanner", targetvalue=100, animation_interval=50, callback=self.behaviour_shortrange)

    def action_btn_localdest(self) -> None:
        headers = ["#", "Name", "Type", "Distance"]
        data = self.ship.get_local_destinations()    
        get_viewport = self.app.query_one(ViewPort)
        get_viewport.present_table(id="longrange_list", headers=headers, data=data, title="Local Destination", callback=self.behaviour_localdest)        

    def action_btn_jump(self) -> None:
        headers = ["#", "Name", "Distance"]
        data = self.ship.get_jump_desination()
        get_viewport = self.app.query_one(ViewPort)
        get_viewport.present_table(id="longrange_list", headers=headers, data=data, title="System Jump Destination", callback=self.behaviour_jump)          

    def action_btn_dock(self) -> None:
        option_list = ["Option1", "Option2", "Option3"]
        get_viewport = self.app.query_one(ViewPort)
        get_viewport.present_options(id="longrange_list", option_values=option_list, title="Land or Dock Target", callback=self.behaviour_dock)        

    def action_btn_extract(self) -> None:
        option_list = ["Option1", "Option2", "Option3"]
        get_viewport = self.app.query_one(ViewPort)
        get_viewport.present_options(id="longrange_list", option_values=option_list, title="Extract Resource", callback=self.behaviour_extract)

    def behaviour_dock(self, text) -> None:
        get_log = self.app.query_one(ShipLog)
        get_log.update_log("Callback: Docked with " + text)

    def behaviour_extract(self, text) -> None:
        get_log = self.app.query_one(ShipLog)
        get_log.update_log("Callback: Extracted some " + text)      

    def behaviour_shortrange(self) -> None:
        get_log = self.app.query_one(ShipLog)
        get_log.update_log("Callback: Short Range Scan Complete")

    def behaviour_longrange(self) -> None:
        get_log = self.app.query_one(ShipLog)
        get_log.update_log("Callback: Long Range Scan Complete")   

    def behaviour_jump(self, id) -> None:
        get_log = self.app.query_one(ShipLog)
        get_log.update_log(f"Callback: Selected jump destination: {id}")
        self.ship.jump_to_system(id)
        get_locationwidget = self.app.query_one(LocationIndicator)
        get_locationwidget.update_system(id)

    def behaviour_localdest(self, id) -> None:
        get_log = self.app.query_one(ShipLog)
        get_log.update_log(f"Callback: Selected local destination: {id}")
        self.ship.goto_location(id)
        get_locationwidget = self.app.query_one(LocationIndicator)
        get_locationwidget.update_location(id)