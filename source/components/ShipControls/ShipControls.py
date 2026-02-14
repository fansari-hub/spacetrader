from textual.containers import HorizontalGroup, VerticalGroup
from textual.widgets import Button
from rich.text import Text
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
        get_viewport = self.app.query_one(ViewPort)
        if self.ship.has_current_system_long_range_scan():
            get_log.update_log("Long Range Scanner data loaded from ship memory.")
            get_viewport.present_longrange_visual()
            return
        get_log.update_log("Started Long Range Scanner...")
        get_viewport.present_loadbar(label="Long Range Scanner", targetvalue=100, animation_interval=25, callback=self.behaviour_longrange)
        
    def action_btn_shortrange(self) -> None:
        get_log = self.app.query_one(ShipLog)
        get_viewport = self.app.query_one(ViewPort)
        if self.ship.has_current_system_short_range_scan():
            get_log.update_log("Short Range Scanner data loaded from ship memory.")
            get_viewport.present_system_visual()
            return
        get_log.update_log("Started Short Range Scanner...")
        get_viewport.present_loadbar(label="Short Range Scanner", targetvalue=100, animation_interval=50, callback=self.behaviour_shortrange)

    def action_btn_localdest(self) -> None:
        get_log = self.app.query_one(ShipLog)
        if not self.ship.has_current_system_short_range_scan():
            get_log.update_log("Short-range scan data unavailable for this system. Run Short-range Scan first.")
            return
        headers = ["#", "Name", "Type", "Distance (million km)"]
        data = self.ship.get_local_destinations()    
        get_viewport = self.app.query_one(ViewPort)
        get_viewport.present_table(id="longrange_list", headers=headers, data=data, title="Local Destination", callback=self.behaviour_localdest)        

    def action_btn_jump(self) -> None:
        get_log = self.app.query_one(ShipLog)
        if not self.ship.has_current_system_long_range_scan():
            get_log.update_log("Long-range scan data unavailable for this system. Run Long-range Scan first.")
            return
        headers = ["#", "Name", "Distance (ly)"]
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
        self.ship.mark_short_range_scan()
        get_log = self.app.query_one(ShipLog)
        get_log.update_log("Callback: Short Range Scan Complete (saved to ship memory)")
        get_viewport = self.app.query_one(ViewPort)
        get_viewport.present_system_visual()

    def behaviour_longrange(self) -> None:
        self.ship.mark_long_range_scan()
        get_log = self.app.query_one(ShipLog)
        get_log.update_log("Callback: Long Range Scan Complete (saved to ship memory)")
        get_viewport = self.app.query_one(ViewPort)
        get_viewport.present_longrange_visual()

    def behaviour_jump(self, id) -> None:
        id = int(id)
        get_log = self.app.query_one(ShipLog)
        system_name = self.ship.galaxy.get_celestial_system(id).name
        jump_distance = self.ship.get_jump_distance(id)
        message = Text("Initiating jump to ")
        message.append(system_name, style="bold cyan")
        message.append(f" ({self.ship.format_interstellar_distance(jump_distance)})")
        get_log.update_log(message)
        get_viewport = self.app.query_one(ViewPort)
        get_viewport.present_loadbar(
            label="Jump Drive",
            targetvalue=100,
            animation_interval=self._travel_animation_interval(jump_distance, "jump"),
            callback=lambda: self._complete_jump(id),
        )

    def behaviour_localdest(self, id) -> None:
        id = int(id)
        get_log = self.app.query_one(ShipLog)
        local_name = self.ship.galaxy.get_celestial_system(self.ship.get_current_system()).members[id - 1].name
        local_distance = self.ship.get_local_distance(id)
        message = Text("Navigating to ")
        message.append(local_name, style="bold cyan")
        message.append(f" ({self.ship.format_local_distance(local_distance)})")
        get_log.update_log(message)
        get_viewport = self.app.query_one(ViewPort)
        get_viewport.present_loadbar(
            label="Sublight Transit",
            targetvalue=100,
            animation_interval=self._travel_animation_interval(local_distance, "local"),
            callback=lambda: self._complete_local_travel(id),
        )

    def _complete_jump(self, id: int) -> None:
        self.ship.jump_to_system(id)
        get_log = self.app.query_one(ShipLog)
        system_name = self.ship.galaxy.get_celestial_system(id).name
        message = Text("Arrived at ")
        message.append(system_name, style="bold green")
        message.append(".")
        get_log.update_log(message)
        get_locationwidget = self.app.query_one(LocationIndicator)
        get_locationwidget.update_system(id)
        get_viewport = self.app.query_one(ViewPort)
        get_viewport.refresh_current_display()

    def _complete_local_travel(self, id: int) -> None:
        self.ship.goto_location(id)
        get_log = self.app.query_one(ShipLog)
        local_name = self.ship.galaxy.get_celestial_system(self.ship.get_current_system()).members[id - 1].name
        message = Text("Arrived at ")
        message.append(local_name, style="bold green")
        message.append(".")
        get_log.update_log(message)
        get_locationwidget = self.app.query_one(LocationIndicator)
        get_locationwidget.update_location(id)
        get_viewport = self.app.query_one(ViewPort)
        get_viewport.refresh_current_display()

    def _travel_animation_interval(self, distance: float, travel_type: str) -> int:
        if travel_type == "jump":
            target_seconds = max(2.0, min(12.0, distance / 120.0))
        else:
            target_seconds = max(1.0, min(6.0, distance / 250.0))
        return max(5, int(100 / target_seconds))
