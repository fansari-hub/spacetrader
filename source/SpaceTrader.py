from textual.app import App, ComposeResult
from textual.widgets import Footer, Header
from components.MainInterface.MainInterface import MainInterface
from components.ShipControls.ShipControls import ShipControls
from components.ShipComms.ShipComms import ShipComms
from components.ViewPort.ViewPort import ViewPort
from objects.Ship.Ship import Ship
from objects.Galaxy.Galaxy import Galaxy

class SpaceTrader(App):

    CSS_PATH = "SpaceTrader.tcss"
    BINDINGS = [
        ("j", "open_jump_nav", "Jump to System"),
        ("g", "open_local_nav", "Goto Local Destination"),
        ("t", "toggle_market_sort", "Toggle Market Sort"),
        ("ctrl+s", "save_game", "Save Game"),
        ("ctrl+l", "load_game", "Load Game"),
        ("up", "select_prev_target", "Previous Target"),
        ("down", "select_next_target", "Next Target"),
        ("enter", "confirm_target", "Open Actions"),
        ("escape", "cancel_popup", "Cancel Popup"),
    ]
    galaxy = Galaxy()
    galaxy.generate_galaxy(20)
    ship = Ship(galaxy)
    #BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        yield MainInterface(ship=self.ship, galaxy=self.galaxy, id="main_interface")

    def action_open_jump_nav(self) -> None:
        self.query_one(ShipControls).action_open_jump_nav()
        self.query_one(ViewPort).focus()

    def action_open_local_nav(self) -> None:
        self.query_one(ShipControls).action_open_local_nav()
        self.query_one(ViewPort).focus()

    def action_save_game(self) -> None:
        self.query_one(ShipControls).action_save_game()
        self.query_one(ViewPort).focus()

    def action_load_game(self) -> None:
        self.query_one(ShipControls).action_load_game()
        self.query_one(ViewPort).focus()

    def action_toggle_market_sort(self) -> None:
        self.query_one(ShipControls).action_toggle_market_sort()
        self.query_one(ViewPort).focus()

    def action_select_prev_target(self) -> None:
        comms_menu = self._get_active_comms_menu()
        if comms_menu:
            comms_menu.menu_cursor_up()
            return
        self.query_one(ShipControls).action_select_prev_target()

    def action_select_next_target(self) -> None:
        comms_menu = self._get_active_comms_menu()
        if comms_menu:
            comms_menu.menu_cursor_down()
            return
        self.query_one(ShipControls).action_select_next_target()

    def action_confirm_target(self) -> None:
        comms_menu = self._get_active_comms_menu()
        if comms_menu:
            comms_menu.menu_confirm()
            return
        self.query_one(ShipControls).action_confirm_target()

    def action_cancel_popup(self) -> None:
        comms_menu = self._get_active_comms_menu()
        if comms_menu:
            comms_menu.menu_cancel()
            self.query_one(ShipControls).refresh_action_preview()
            return

    def _get_active_comms_menu(self):
        comms = self.query_one(ShipComms)
        if comms.has_active_menu():
            return comms
        return None

    # def action_toggle_dark(self) -> None:
    #     """An action to toggle dark mode."""
    #     self.theme = (
    #         "textual-dark" if self.theme == "textual-light" else "textual-light"
    #     )


if __name__ == "__main__":
    app = SpaceTrader()
    app.run()
