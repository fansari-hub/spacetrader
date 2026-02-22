from textual.containers import HorizontalGroup, VerticalGroup
from textual.widgets import Label
from rich.text import Text
from pathlib import Path
from datetime import datetime
from ..ViewPort.ViewPort import ViewPort
from ..ShipLog.ShipLog import ShipLog
from ..LocationIndicator.LocationIndicator import LocationIndicator
from ..ShipStats.ShipStats import ShipStats
from ..LongRangeVisualizer.LongRangeVisualizer import LongRangeVisualizer
from ..SystemVisualizer.SystemVisualizer import SystemVisualizer
from ..ShipComms.ShipComms import ShipComms
from objects.SaveGame import save_game, load_game, get_save_slot_summaries

class ShipControls(HorizontalGroup):

    BINDINGS = [
        ("j", "open_jump_nav", "Jump to System"),
        ("g", "open_local_nav", "Goto Local Destination"),
        ("t", "toggle_market_sort", "Toggle Market Sort"),
        ("ctrl+s", "save_game", "Save Game"),
        ("ctrl+l", "load_game", "Load Game"),
        ("up", "select_prev_target", "Previous Target"),
        ("down", "select_next_target", "Next Target"),
        ("enter", "confirm_target", "Open Actions"),
    ]

    def __init__(self, ship, id=None):
        self.ship = ship
        self.pending_action = None
        self.market_sort_mode = "name"
        self.active_trade_menu_mode = None
        self.trade_selected_commodity_id = None
        super().__init__(id=id)

    def compose(self):
        with VerticalGroup():
            yield Label("", id="hint_jump", markup=False)
            yield Label("", id="hint_local", markup=False)
            yield Label("[Up/Down] Select", id="hint_select", markup=False)
            yield Label("[Enter] Actions", id="hint_action", markup=False)
            yield Label("[T] Sort | [Ctrl+S] Save | [Ctrl+L] Load", id="hint_save", markup=False)

    def on_mount(self) -> None:
        self.refresh_action_buttons()
        self.call_after_refresh(self.refresh_action_preview)

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
            self._update_comms_action_preview()
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
        self._update_comms_action_preview()

    def action_open_jump_nav(self) -> None:
        get_log = self.app.query_one(ShipLog)
        if not self.ship.has_current_system_long_range_scan():
            self.action_btn_longrange()
            self._update_comms_action_preview()
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
        self._update_comms_action_preview()

    def _open_trade_console(self) -> None:
        get_log = self.app.query_one(ShipLog)
        current_body = self.ship.get_current_body()
        if not current_body.has_market:
            get_log.update_log("Trade console unavailable. Navigate to an orbital station with a market.")
            return
        self.active_trade_menu_mode = None
        self.trade_selected_commodity_id = None
        option_list = ["Buy Cargo", "Sell Cargo", "Close Console"]
        self.app.query_one(ShipComms).open_menu(
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
        self._update_comms_action_preview()

    def behaviour_shortrange(self) -> None:
        self.ship.mark_short_range_scan()
        self.refresh_action_buttons()
        get_log = self.app.query_one(ShipLog)
        get_log.update_log("Callback: Short Range Scan Complete (saved to ship memory)")
        get_viewport = self.app.query_one(ViewPort)
        get_viewport.present_system_visual()
        self._update_comms_action_preview()

    def behaviour_longrange(self) -> None:
        self.ship.mark_long_range_scan()
        self.refresh_action_buttons()
        get_log = self.app.query_one(ShipLog)
        get_log.update_log("Callback: Long Range Scan Complete (saved to ship memory)")
        get_viewport = self.app.query_one(ViewPort)
        get_viewport.present_longrange_visual()
        self._update_comms_action_preview()

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
        self.call_after_refresh(self.refresh_action_preview)

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
        self.call_after_refresh(self.refresh_action_preview)

    def _travel_animation_interval(self, distance: float, travel_type: str) -> int:
        if travel_type == "jump":
            target_seconds = max(2.0, min(12.0, distance / 120.0))
        else:
            target_seconds = max(1.0, min(6.0, distance / 250.0))
        return max(5, int(100 / target_seconds))

    def _open_trade_inventory_menu(self, mode: str, selected_commodity_id: str | None = None) -> None:
        current_system_id = self.ship.get_current_system()
        market = self.ship.galaxy.system_markets.get(current_system_id, {})
        self.active_trade_menu_mode = mode
        if selected_commodity_id is not None:
            self.trade_selected_commodity_id = selected_commodity_id
        selected_commodity_id = self.trade_selected_commodity_id
        option_values = []
        selected_index = 0
        row_index = 0

        for commodity_id, data in self._sorted_market_items(market):
            your_qty = self.ship.cargo_manifest.get(commodity_id, 0)
            commodity_name = data["name"]
            if len(commodity_name) > 10:
                commodity_name = f"{commodity_name[:9]}."
            commodity_name = f"{commodity_name:<10}"
            price_text = f"{data['price']:>4}"
            stock_text = f"{data['stock']:>3}"
            your_text = f"{your_qty:>3}"
            option_label = Text()
            option_label.append(commodity_name, style="white")
            option_label.append(" | ", style="grey50")
            option_label.append(price_text, style="bold yellow")
            option_label.append(" cr", style="white")
            option_label.append(" | ", style="grey50")
            option_label.append("Stock ", style="white")
            option_label.append(stock_text, style=self._stock_style(data["stock"]))
            option_label.append(" | ", style="grey50")
            option_label.append("You ", style="white")
            option_label.append(your_text, style=self._cargo_style(your_qty))
            option_values.append((option_label, commodity_id))
            if selected_commodity_id is not None and commodity_id == selected_commodity_id:
                selected_index = row_index
            row_index += 1

        option_values.append(("Back", "Back"))
        title = f"Station Market ({mode.upper()} | Sort: {self._market_sort_indicator()})"
        self.app.query_one(ShipComms).open_menu(
            option_values=option_values,
            title=title,
            callback=lambda text: self.behaviour_trade_pick(mode, text),
            selected_index=selected_index,
        )

    def behaviour_trade_pick(self, mode: str, option_value: str) -> None:
        if option_value == "Back":
            self._open_trade_console()
            return
        commodity_id = str(option_value)
        market = self.ship.galaxy.system_markets.get(self.ship.get_current_system(), {})
        if commodity_id not in market:
            self.app.query_one(ShipLog).update_log("Trade failed: invalid commodity selection.")
            self._open_trade_inventory_menu(mode)
            return
        self.trade_selected_commodity_id = commodity_id
        self._open_trade_quantity_menu(mode, commodity_id)

    def _open_trade_quantity_menu(self, mode: str, commodity_id: str) -> None:
        self.active_trade_menu_mode = None
        market_item = self.ship.galaxy.system_markets[self.ship.get_current_system()][commodity_id]
        commodity_name = market_item["name"]
        quantity_options = [(f"+{qty} units", qty) for qty in (1, 5, 10)]
        quantity_options.append(("Back", "Back"))
        title = f"{mode.upper()} Quantity: {commodity_name}"
        self.app.query_one(ShipComms).open_menu(
            option_values=quantity_options,
            title=title,
            callback=lambda value: self.behaviour_trade_quantity_pick(mode, commodity_id, value),
        )

    def behaviour_trade_quantity_pick(self, mode: str, commodity_id: str, option_value) -> None:
        if option_value == "Back":
            self._open_trade_inventory_menu(mode, selected_commodity_id=commodity_id)
            return
        quantity = int(option_value)
        self._execute_trade_by_commodity(mode, commodity_id, quantity=quantity)
        self._open_trade_inventory_menu(mode, selected_commodity_id=commodity_id)

    def _stock_style(self, stock: int) -> str:
        if stock >= 20:
            return "bold green"
        if stock >= 8:
            return "bold yellow"
        return "bold red"

    def _cargo_style(self, quantity: int) -> str:
        if quantity > 0:
            return "bold cyan"
        return "grey50"

    def action_save_game(self) -> None:
        self._open_save_load_slot_menu("save")

    def action_load_game(self) -> None:
        self._open_save_load_slot_menu("load")

    def _open_save_load_slot_menu(self, mode: str) -> None:
        summaries = get_save_slot_summaries()
        option_values = []
        for summary in summaries:
            slot = summary["slot"]
            label = Text()
            label.append("Slot ", style="white")
            label.append(f"{slot}", style="bold cyan")
            label.append(" | ", style="grey50")
            if summary["exists"]:
                saved_at = self._format_saved_at_short(summary.get("saved_at"))
                size_kb = summary["size_bytes"] / 1024.0
                label.append(f"{saved_at:16}", style="green")
                label.append(" | ", style="grey50")
                label.append(f"{size_kb:>6.1f}", style="bold yellow")
                label.append(" KB", style="white")
            else:
                label.append(f"{'EMPTY':16}", style="red")
                label.append(" | ", style="grey50")
                label.append("  --.- KB", style="grey50")
            option_values.append((label, slot))

        option_values.append(("Cancel", "cancel"))
        title = "Save Game: Choose Slot" if mode == "save" else "Load Game: Choose Slot"
        self.app.query_one(ShipComms).open_menu(
            option_values=option_values,
            title=title,
            callback=lambda text: self.behaviour_save_load_slot_pick(mode, text),
        )

    def behaviour_save_load_slot_pick(self, mode: str, option_value) -> None:
        get_log = self.app.query_one(ShipLog)
        if option_value == "cancel":
            get_log.update_log("Save/Load canceled.")
            return

        slot = int(option_value)

        if mode == "save":
            try:
                save_path = save_game(self.ship, slot=slot)
            except Exception as exc:
                get_log.update_log(f"Save failed: {exc}")
                return
            relative_path = Path(save_path).as_posix()
            get_log.update_log(f"Progress saved to slot {slot} ({relative_path})")
            return

        try:
            save_path = load_game(self.ship, slot=slot)
        except FileNotFoundError:
            get_log.update_log(f"Load failed: slot {slot} is empty.")
            return
        except Exception as exc:
            get_log.update_log(f"Load failed: {exc}")
            return

        self.pending_action = None
        self.active_trade_menu_mode = None
        self.refresh_action_buttons()
        self.app.query_one(ShipStats).refresh_from_ship()
        location_widget = self.app.query_one(LocationIndicator)
        location_widget.update_system(self.ship.get_current_system())
        location_widget.update_location(self.ship.get_current_location())
        viewport = self.app.query_one(ViewPort)
        viewport.refresh_current_display()
        relative_path = Path(save_path).as_posix()
        get_log.update_log(f"Progress loaded from slot {slot} ({relative_path})")
        self.call_after_refresh(self.refresh_action_preview)

    def _execute_trade_by_commodity(self, mode: str, commodity_id: str, quantity: int = 1) -> None:
        get_log = self.app.query_one(ShipLog)
        system_id = self.ship.get_current_system()
        market_item = self.ship.galaxy.system_markets[system_id][commodity_id]
        commodity_name = market_item["name"]
        price = market_item["price"]
        quantity = max(1, int(quantity))

        if mode == "buy":
            market_stock = self.ship.galaxy.market_stock(system_id, commodity_id)
            if market_stock < quantity:
                get_log.update_log(f"{commodity_name} is out of stock.")
                return
            can_buy, reason = self.ship.can_buy(price, quantity=quantity)
            if not can_buy:
                get_log.update_log(f"Purchase failed: {reason}")
                return
            total_cost = price * quantity
            self.ship.buy_commodity(commodity_id, price, quantity=quantity)
            self.ship.galaxy.market_decrease_stock(system_id, commodity_id, quantity=quantity)
            self.app.query_one(ShipStats).refresh_from_ship()
            get_log.update_log(
                f"Bought {quantity} {commodity_name} for {total_cost} cr | Credits: {self.ship.credits} | Cargo: {self.ship.get_cargo_used()}/{self.ship.cargo_capacity}"
            )
            return

        can_sell, reason = self.ship.can_sell(commodity_id, quantity=quantity)
        if not can_sell:
            get_log.update_log(f"Sale failed: {reason}")
            return
        total_revenue = price * quantity
        self.ship.sell_commodity(commodity_id, price, quantity=quantity)
        self.ship.galaxy.market_increase_stock(system_id, commodity_id, quantity=quantity)
        self.app.query_one(ShipStats).refresh_from_ship()
        get_log.update_log(
            f"Sold {quantity} {commodity_name} for {total_revenue} cr | Credits: {self.ship.credits} | Cargo: {self.ship.get_cargo_used()}/{self.ship.cargo_capacity}"
        )

    def action_toggle_market_sort(self) -> None:
        comms = self.app.query_one(ShipComms)
        if self.active_trade_menu_mode and comms.has_active_menu():
            self.market_sort_mode = self._next_market_sort_mode()
            self._open_trade_inventory_menu(
                self.active_trade_menu_mode,
                selected_commodity_id=self.trade_selected_commodity_id,
            )
            return
        self.app.query_one(ShipLog).update_log("Sort toggle available in Station Market list only.")

    def _next_market_sort_mode(self) -> str:
        modes = ("name", "price", "stock", "owned")
        current_index = modes.index(self.market_sort_mode)
        return modes[(current_index + 1) % len(modes)]

    def _sorted_market_items(self, market: dict) -> list[tuple[str, dict]]:
        items = list(market.items())
        if self.market_sort_mode == "price":
            return sorted(items, key=lambda item: item[1]["price"])
        if self.market_sort_mode == "stock":
            return sorted(items, key=lambda item: item[1]["stock"], reverse=True)
        if self.market_sort_mode == "owned":
            return sorted(items, key=lambda item: self.ship.cargo_manifest.get(item[0], 0), reverse=True)
        return sorted(items, key=lambda item: item[1]["name"])

    def _market_sort_indicator(self) -> str:
        if self.market_sort_mode == "name":
            return "NAME ↑"
        if self.market_sort_mode == "price":
            return "PRICE ↑"
        if self.market_sort_mode == "stock":
            return "STOCK ↓"
        return "OWNED ↓"

    def _format_saved_at_short(self, saved_at: str | None) -> str:
        if not saved_at:
            return "Unknown"
        try:
            normalized = saved_at.replace("Z", "+00:00")
            parsed = datetime.fromisoformat(normalized)
            return parsed.strftime("%Y-%m-%d %H:%M")
        except ValueError:
            stripped = saved_at.replace("T", " ")
            return stripped[:16] if len(stripped) >= 16 else stripped

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
            self._update_comms_action_preview()
            return
        if get_viewport.display_mode == "long" and self.ship.has_current_system_long_range_scan():
            self.ship.shift_selected_jump(step)
            get_viewport.refresh_current_display()
            self._update_comms_action_preview()
            return
        if get_viewport.display_mode == "long":
            get_log.update_log("Long-range targets unavailable. Press [J] to scan current system first.")
            self._update_comms_action_preview()
            return
        if get_viewport.display_mode == "short" and self.ship.has_current_system_short_range_scan():
            self.ship.shift_selected_local(step)
            get_viewport.refresh_current_display()
            self._update_comms_action_preview()
            return
        if get_viewport.display_mode == "short":
            get_log.update_log("Local targets unavailable. Press [G] to scan current system first.")
            self._update_comms_action_preview()

    def _open_longrange_action_menu(self) -> None:
        target_id = self.ship.get_selected_jump_system_id()
        if target_id == self.ship.get_current_system():
            self.app.query_one(ShipLog).update_log("You are already in the selected system.")
            return
        target_system = self.ship.galaxy.get_celestial_system(target_id)
        self.pending_action = ("jump", target_id)
        self.app.query_one(ShipComms).open_menu(
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
        self.app.query_one(ShipComms).open_menu(
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

        select_label = Text()
        select_label.append("[", style="white")
        select_label.append("Up/Down", style="bold yellow")
        select_label.append("] Select", style="white")

        action_label = Text()
        action_label.append("[", style="white")
        action_label.append("Enter", style="bold magenta")
        action_label.append("] Actions", style="white")

        save_label = Text()
        save_label.append("[", style="white")
        save_label.append("T", style="bold yellow")
        save_label.append("] Sort  |  ", style="white")
        save_label.append("[", style="white")
        save_label.append("Ctrl+S", style="bold cyan")
        save_label.append("] Save  |  ", style="white")
        save_label.append("[", style="white")
        save_label.append("Ctrl+L", style="bold green")
        save_label.append("] Load", style="white")

        self.query_one("#hint_jump", Label).update(jump_label)
        self.query_one("#hint_local", Label).update(local_label)
        self.query_one("#hint_select", Label).update(select_label)
        self.query_one("#hint_action", Label).update(action_label)
        self.query_one("#hint_save", Label).update(save_label)

    def _update_comms_action_preview(self) -> None:
        comms = self.app.query_one(ShipComms)
        if comms.has_active_menu():
            return

        viewport = self.app.query_one(ViewPort)
        if not self._is_cartography_active(viewport):
            comms.clear_action_preview()
            return

        if viewport.display_mode == "long":
            if not self.ship.has_current_system_long_range_scan():
                comms.show_action_preview("Long Cartography", ["Run long-range scan first"])
                return
            target_id = self.ship.get_selected_jump_system_id()
            target_system = self.ship.galaxy.get_celestial_system(target_id)
            if target_id == self.ship.get_current_system():
                comms.show_action_preview(target_system.name, ["Already in current system"])
                return
            comms.show_action_preview(target_system.name, [f"Jump to {target_system.name}"])
            return

        if not self.ship.has_current_system_short_range_scan():
            comms.show_action_preview("Local Cartography", ["Run short-range scan first"])
            return

        system = self.ship.galaxy.get_celestial_system(self.ship.get_current_system())
        target_id = self.ship.get_selected_local_id()
        if target_id <= 0:
            comms.show_action_preview(system.name, ["No local target selected"])
            return
        target_body = system.members[target_id - 1]
        is_current = target_id == self.ship.get_current_location()
        preview_options = []
        if not is_current:
            preview_options.append(f"Travel to {target_body.name}")
        elif target_body.has_market:
            preview_options.append("Open Trade Console")
        elif target_body.type in {"Planet", "Gas Giant", "Dwarf Planet", "Moon"}:
            preview_options.extend(["Dock or Land", "Extract Resources"])

        comms.show_action_preview(target_body.name, preview_options)

    def refresh_action_preview(self) -> None:
        self._refresh_action_preview_with_retry(retries=5, delay=0.05)

    def _refresh_action_preview_with_retry(self, retries: int, delay: float) -> None:
        comms = self.app.query_one(ShipComms)
        if comms.has_active_menu():
            return

        viewport = self.app.query_one(ViewPort)
        if self._is_cartography_active(viewport):
            self._update_comms_action_preview()
            return

        if retries > 0:
            self.set_timer(delay, lambda: self._refresh_action_preview_with_retry(retries - 1, delay))
            return

        self._update_comms_action_preview()
