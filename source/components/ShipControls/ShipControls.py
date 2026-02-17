from textual.containers import HorizontalGroup, VerticalGroup
from textual.widgets import Label
from rich.text import Text
from ..ViewPort.ViewPort import ViewPort
from ..ShipLog.ShipLog import ShipLog
from ..LocationIndicator.LocationIndicator import LocationIndicator
from ..ShipStats.ShipStats import ShipStats
from ..LongRangeVisualizer.LongRangeVisualizer import LongRangeVisualizer
from ..SystemVisualizer.SystemVisualizer import SystemVisualizer

class ShipControls(HorizontalGroup):

    BINDINGS = [
        ("j", "open_jump_nav", "Jump to System"),
        ("g", "open_local_nav", "Goto Local Destination"),
        ("up", "select_prev_target", "Previous Target"),
        ("down", "select_next_target", "Next Target"),
        ("enter", "confirm_target", "Open Actions"),
    ]

    def __init__(self, ship, id=None):
        self.ship = ship
        self.pending_action = None
        self.trade_option_map = {}
        super().__init__(id=id)

    def compose(self):
        with VerticalGroup():
            yield Label("", id="hint_jump", markup=False)
            yield Label("", id="hint_local", markup=False)
            yield Label("[Up/Down] Select  [Enter] Actions", id="hint_target", markup=False)

    def on_mount(self) -> None:
        self.refresh_action_buttons()

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

    def action_open_local_nav(self) -> None:
        get_log = self.app.query_one(ShipLog)
        if not self.ship.has_current_system_short_range_scan():
            self.action_btn_shortrange()
            return
        get_viewport = self.app.query_one(ViewPort)
        if self._is_cartography_active(get_viewport) and get_viewport.display_mode == "short":
            self._open_local_action_menu()
            return
        get_viewport.present_system_visual()
        members = self.ship.galaxy.get_celestial_system(self.ship.get_current_system()).members
        if len(members) > 1 and self.ship.get_selected_local_id() == self.ship.get_current_location():
            self.ship.shift_selected_local(1)
            get_viewport.refresh_current_display()
        selected_id = self.ship.get_selected_local_id()
        if selected_id > 0:
            selected_body = self.ship.galaxy.get_celestial_system(self.ship.get_current_system()).members[selected_id - 1]
            get_log.update_log(
                f"Local target mode: {selected_body.name} selected. Use Up/Down and Enter for actions."
            )

    def action_open_jump_nav(self) -> None:
        get_log = self.app.query_one(ShipLog)
        if not self.ship.has_current_system_long_range_scan():
            self.action_btn_longrange()
            return
        get_viewport = self.app.query_one(ViewPort)
        if self._is_cartography_active(get_viewport) and get_viewport.display_mode == "long":
            self._open_longrange_action_menu()
            return
        get_viewport.present_longrange_visual()
        if len(self.ship.galaxy.celestial_systems) > 1 and self.ship.get_selected_jump_system_id() == self.ship.get_current_system():
            self.ship.shift_selected_jump(1)
            get_viewport.refresh_current_display()
        selected_id = self.ship.get_selected_jump_system_id()
        selected_system = self.ship.galaxy.get_celestial_system(selected_id)
        get_log.update_log(
            f"Jump target mode: {selected_system.name} selected. Use Up/Down and Enter for actions."
        )

    def _open_trade_console(self) -> None:
        get_log = self.app.query_one(ShipLog)
        current_body = self.ship.get_current_body()
        if not current_body.has_market:
            get_log.update_log("Trade console unavailable. Navigate to an orbital station with a market.")
            return
        option_list = ["Buy Cargo", "Sell Cargo", "Close Console"]
        get_viewport = self.app.query_one(ViewPort)
        get_viewport.present_options(
            id="trade_mode",
            option_values=option_list,
            title="Trade Console: Select Operation",
            callback=self.behaviour_trade_mode,
        )

    def behaviour_dock(self, text) -> None:
        get_log = self.app.query_one(ShipLog)
        get_log.update_log("Callback: Docked with " + text)

    def behaviour_extract(self, text) -> None:
        get_log = self.app.query_one(ShipLog)
        get_log.update_log("Callback: Extracted some " + text)      

    def behaviour_trade_mode(self, text) -> None:
        if text == "Buy Cargo":
            self._open_trade_inventory_menu("buy")
            return
        if text == "Sell Cargo":
            self._open_trade_inventory_menu("sell")
            return
        self.app.query_one(ShipLog).update_log("Trade console closed.")

    def behaviour_shortrange(self) -> None:
        self.ship.mark_short_range_scan()
        self.refresh_action_buttons()
        get_log = self.app.query_one(ShipLog)
        get_log.update_log("Callback: Short Range Scan Complete (saved to ship memory)")
        get_viewport = self.app.query_one(ViewPort)
        get_viewport.present_system_visual()

    def behaviour_longrange(self) -> None:
        self.ship.mark_long_range_scan()
        self.refresh_action_buttons()
        get_log = self.app.query_one(ShipLog)
        get_log.update_log("Callback: Long Range Scan Complete (saved to ship memory)")
        get_viewport = self.app.query_one(ViewPort)
        get_viewport.present_longrange_visual()

    def behaviour_jump(self, id) -> None:
        id = int(id)
        get_log = self.app.query_one(ShipLog)
        if id == self.ship.get_current_system():
            get_log.update_log("Jump aborted. You are already in that system.")
            return
        system_name = self.ship.galaxy.get_celestial_system(id).name
        jump_distance = self.ship.get_jump_distance(id)
        fuel_cost = self.ship.get_jump_fuel_cost(jump_distance)
        if not self.ship.can_spend_fuel(fuel_cost):
            get_log.update_log(
                f"Jump aborted. Fuel required: {fuel_cost}, available: {self.ship.fuel}."
            )
            return
        message = Text("Initiating jump to ")
        message.append(system_name, style="bold cyan")
        message.append(
            f" ({self.ship.format_interstellar_distance(jump_distance)} | Fuel cost: {fuel_cost})"
        )
        get_log.update_log(message)
        get_viewport = self.app.query_one(ViewPort)
        get_viewport.present_loadbar(
            label="Jump Drive",
            targetvalue=100,
            animation_interval=self._travel_animation_interval(jump_distance, "jump"),
            callback=lambda: self._complete_jump(id, fuel_cost),
        )

    def behaviour_localdest(self, id) -> None:
        id = int(id)
        get_log = self.app.query_one(ShipLog)
        if id == self.ship.get_current_location():
            get_log.update_log("Transit aborted. You are already at that local destination.")
            return
        local_name = self.ship.galaxy.get_celestial_system(self.ship.get_current_system()).members[id - 1].name
        local_distance = self.ship.get_local_distance(id)
        fuel_cost = self.ship.get_local_fuel_cost(local_distance)
        if not self.ship.can_spend_fuel(fuel_cost):
            get_log.update_log(
                f"Transit aborted. Fuel required: {fuel_cost}, available: {self.ship.fuel}."
            )
            return
        message = Text("Navigating to ")
        message.append(local_name, style="bold cyan")
        message.append(f" ({self.ship.format_local_distance(local_distance)} | Fuel cost: {fuel_cost})")
        get_log.update_log(message)
        get_viewport = self.app.query_one(ViewPort)
        get_viewport.present_loadbar(
            label="Sublight Transit",
            targetvalue=100,
            animation_interval=self._travel_animation_interval(local_distance, "local"),
            callback=lambda: self._complete_local_travel(id, fuel_cost),
        )

    def _complete_jump(self, id: int, fuel_cost: int) -> None:
        self.ship.spend_fuel(fuel_cost)
        self.ship.jump_to_system(id)
        # Keep long-range navigation usable immediately after arrival.
        self.ship.mark_long_range_scan()
        auto_scanned_local = False
        if not self.ship.has_current_system_short_range_scan():
            self.ship.mark_short_range_scan()
            auto_scanned_local = True
        self.refresh_action_buttons()
        self.app.query_one(ShipStats).refresh_from_ship()
        get_log = self.app.query_one(ShipLog)
        system_name = self.ship.galaxy.get_celestial_system(id).name
        message = Text("Arrived at ")
        message.append(system_name, style="bold green")
        message.append(f". Fuel -{fuel_cost} (remaining: {self.ship.fuel}).")
        get_log.update_log(message)
        if auto_scanned_local:
            get_log.update_log("Auto-scan complete: local cartography data loaded for arrival sector.")
        get_locationwidget = self.app.query_one(LocationIndicator)
        get_locationwidget.update_system(id)
        get_viewport = self.app.query_one(ViewPort)
        get_viewport.present_system_visual()

    def _complete_local_travel(self, id: int, fuel_cost: int) -> None:
        self.ship.spend_fuel(fuel_cost)
        self.ship.goto_location(id)
        self.refresh_action_buttons()
        self.app.query_one(ShipStats).refresh_from_ship()
        get_log = self.app.query_one(ShipLog)
        local_body = self.ship.galaxy.get_celestial_system(self.ship.get_current_system()).members[id - 1]
        local_name = local_body.name
        message = Text("Arrived at ")
        message.append(local_name, style="bold green")
        message.append(f". Fuel -{fuel_cost} (remaining: {self.ship.fuel}).")
        get_log.update_log(message)
        if local_body.has_market:
            station_message = Text("Docking corridor open: ")
            station_message.append(local_name, style="bold cyan")
            station_message.append(" market services available. Select this station and press Enter for actions.", style="white")
            get_log.update_log(station_message)
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

    def _open_trade_inventory_menu(self, mode: str) -> None:
        current_system_id = self.ship.get_current_system()
        market = self.ship.galaxy.system_markets.get(current_system_id, {})
        option_values = []
        self.trade_option_map = {}

        for commodity_id, data in market.items():
            your_qty = self.ship.cargo_manifest.get(commodity_id, 0)
            option_text = (
                f"{data['name']} | {data['price']} cr | "
                f"Stock {data['stock']} | You {your_qty}"
            )
            option_values.append(option_text)
            self.trade_option_map[option_text] = commodity_id

        option_values.append("Back")
        title = f"Station Market ({mode.upper()} 1 unit)"
        self.app.query_one(ViewPort).present_options(
            id="market_menu",
            option_values=option_values,
            title=title,
            callback=lambda text: self.behaviour_trade_pick(mode, text),
        )

    def behaviour_trade_pick(self, mode: str, option_text: str) -> None:
        if option_text == "Back":
            self._open_trade_console()
            return
        commodity_id = self.trade_option_map.get(option_text)
        if not commodity_id:
            self.app.query_one(ShipLog).update_log("Trade failed: invalid commodity selection.")
            self._open_trade_inventory_menu(mode)
            return
        self._execute_trade_by_commodity(mode, commodity_id)
        self._open_trade_inventory_menu(mode)

    def _execute_trade_by_commodity(self, mode: str, commodity_id: str) -> None:
        get_log = self.app.query_one(ShipLog)
        system_id = self.ship.get_current_system()
        market_item = self.ship.galaxy.system_markets[system_id][commodity_id]
        commodity_name = market_item["name"]
        price = market_item["price"]

        if mode == "buy":
            if self.ship.galaxy.market_stock(system_id, commodity_id) < 1:
                get_log.update_log(f"{commodity_name} is out of stock.")
                return
            can_buy, reason = self.ship.can_buy(price, quantity=1)
            if not can_buy:
                get_log.update_log(f"Purchase failed: {reason}")
                return
            self.ship.buy_commodity(commodity_id, price, quantity=1)
            self.ship.galaxy.market_decrease_stock(system_id, commodity_id, quantity=1)
            self.app.query_one(ShipStats).refresh_from_ship()
            get_log.update_log(
                f"Bought 1 {commodity_name} for {price} cr | Credits: {self.ship.credits} | Cargo: {self.ship.get_cargo_used()}/{self.ship.cargo_capacity}"
            )
            return

        can_sell, reason = self.ship.can_sell(commodity_id, quantity=1)
        if not can_sell:
            get_log.update_log(f"Sale failed: {reason}")
            return
        self.ship.sell_commodity(commodity_id, price, quantity=1)
        self.ship.galaxy.market_increase_stock(system_id, commodity_id, quantity=1)
        self.app.query_one(ShipStats).refresh_from_ship()
        get_log.update_log(
            f"Sold 1 {commodity_name} for {price} cr | Credits: {self.ship.credits} | Cargo: {self.ship.get_cargo_used()}/{self.ship.cargo_capacity}"
        )

    def action_select_prev_target(self) -> None:
        self._move_target_selection(-1)

    def action_select_next_target(self) -> None:
        self._move_target_selection(1)

    def action_confirm_target(self) -> None:
        get_viewport = self.app.query_one(ViewPort)
        if not self._is_cartography_active(get_viewport):
            return
        if get_viewport.display_mode == "long" and self.ship.has_current_system_long_range_scan():
            self._open_longrange_action_menu()
            return
        if get_viewport.display_mode == "short" and self.ship.has_current_system_short_range_scan():
            self._open_local_action_menu()

    def _move_target_selection(self, step: int) -> None:
        get_viewport = self.app.query_one(ViewPort)
        get_log = self.app.query_one(ShipLog)
        if not self._is_cartography_active(get_viewport):
            get_log.update_log("Target selection unavailable. Open [J] jump navigation or [G] local navigation first.")
            return
        if get_viewport.display_mode == "long" and self.ship.has_current_system_long_range_scan():
            selected_id = self.ship.shift_selected_jump(step)
            selected_system = self.ship.galaxy.get_celestial_system(selected_id)
            get_viewport.refresh_current_display()
            get_log.update_log(f"Jump target selected: {selected_system.name}. Enter for actions.")
            return
        if get_viewport.display_mode == "long":
            get_log.update_log("Long-range targets unavailable. Press [J] to scan current system first.")
            return
        if get_viewport.display_mode == "short" and self.ship.has_current_system_short_range_scan():
            selected_id = self.ship.shift_selected_local(step)
            selected_body = self.ship.galaxy.get_celestial_system(self.ship.get_current_system()).members[selected_id - 1]
            get_viewport.refresh_current_display()
            get_log.update_log(f"Local target selected: {selected_body.name}. Enter for actions.")
            return
        if get_viewport.display_mode == "short":
            get_log.update_log("Local targets unavailable. Press [G] to scan current system first.")

    def _open_longrange_action_menu(self) -> None:
        target_id = self.ship.get_selected_jump_system_id()
        if target_id == self.ship.get_current_system():
            self.app.query_one(ShipLog).update_log("You are already in the selected system.")
            return
        target_system = self.ship.galaxy.get_celestial_system(target_id)
        self.pending_action = ("jump", target_id)
        self.app.query_one(ViewPort).present_options(
            id="target_action_menu",
            option_values=[f"Jump to {target_system.name}"],
            title="Target Actions",
            callback=self.behaviour_target_action,
        )

    def _open_local_action_menu(self) -> None:
        system = self.ship.galaxy.get_celestial_system(self.ship.get_current_system())
        target_id = self.ship.get_selected_local_id()
        if target_id <= 0:
            return
        target_body = system.members[target_id - 1]
        is_current = target_id == self.ship.get_current_location()

        options = []
        action_map = {}
        if not is_current:
            travel_label = f"Travel to {target_body.name}"
            options.append(travel_label)
            action_map[travel_label] = ("travel_local", target_id)
        elif target_body.has_market:
            trade_label = "Open Trade Console"
            options.append(trade_label)
            action_map[trade_label] = ("trade", target_id)
        elif target_body.type in {"Planet", "Gas Giant", "Dwarf Planet", "Moon"}:
            dock_label = "Dock or Land"
            extract_label = "Extract Resources"
            options.extend([dock_label, extract_label])
            action_map[dock_label] = ("dock", target_id)
            action_map[extract_label] = ("extract", target_id)

        if not options:
            self.app.query_one(ShipLog).update_log("No actions available for selected location.")
            return

        self.pending_action = ("local", action_map)
        self.app.query_one(ViewPort).present_options(
            id="target_action_menu",
            option_values=options,
            title=f"Target Actions: {target_body.name}",
            callback=self.behaviour_target_action,
        )

    def behaviour_target_action(self, option_text) -> None:
        if not self.pending_action:
            return
        context_type, context_value = self.pending_action
        self.pending_action = None

        if context_type == "jump":
            if option_text.startswith("Jump to "):
                self.behaviour_jump(context_value)
            return

        if context_type != "local":
            return

        action = context_value.get(option_text)
        if not action:
            return

        action_type, target_id = action
        if action_type == "travel_local":
            self.behaviour_localdest(target_id)
            return
        if action_type == "trade":
            self._open_trade_console()
            return
        if action_type == "dock":
            body_name = self.ship.galaxy.get_celestial_system(self.ship.get_current_system()).members[target_id - 1].name
            self.behaviour_dock(body_name)
            return
        if action_type == "extract":
            body_name = self.ship.galaxy.get_celestial_system(self.ship.get_current_system()).members[target_id - 1].name
            self.behaviour_extract(body_name)

    def _is_cartography_active(self, viewport: ViewPort) -> bool:
        content = viewport.query_one("#viewport_content")
        if not content.children:
            return False
        active_widget = content.children[0]
        return isinstance(active_widget, (LongRangeVisualizer, SystemVisualizer))

    def refresh_action_buttons(self) -> None:
        jump_ready = self.ship.has_current_system_long_range_scan()
        local_ready = self.ship.has_current_system_short_range_scan()
        jump_status = "Ready" if jump_ready else "Will scan first"
        local_status = "Ready" if local_ready else "Will scan first"
        jump_label = Text()
        jump_label.append("[", style="white")
        jump_label.append("J", style="bold cyan")
        jump_label.append("]ump to System ", style="white")
        jump_label.append(f"({jump_status})", style="dim")

        local_label = Text()
        local_label.append("[", style="white")
        local_label.append("G", style="bold green")
        local_label.append("]oto Local Destination ", style="white")
        local_label.append(f"({local_status})", style="dim")

        self.query_one("#hint_jump", Label).update(jump_label)
        self.query_one("#hint_local", Label).update(local_label)
