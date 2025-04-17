from textual.app import App, ComposeResult
from textual.widgets import Footer, Header
from components.MainInterface.MainInterface import MainInterface
from objects.Ship.Ship import Ship
from objects.Galaxy.Galaxy import Galaxy

class SpaceTrader(App):

    CSS_PATH = "SpaceTrader.tcss"
    galaxy = Galaxy()
    galaxy.generate_galaxy(20)
    ship = Ship(galaxy)
    #BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        yield MainInterface(ship=self.ship, galaxy=self.galaxy, id="main_interface")

    # def action_toggle_dark(self) -> None:
    #     """An action to toggle dark mode."""
    #     self.theme = (
    #         "textual-dark" if self.theme == "textual-light" else "textual-light"
    #     )


if __name__ == "__main__":
    app = SpaceTrader()
    app.run()