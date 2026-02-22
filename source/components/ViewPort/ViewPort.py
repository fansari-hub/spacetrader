from textual.containers import VerticalGroup, HorizontalGroup
from textual.widgets import Static, Label
from ..StatusBar.StatusBar import StatusBar
from ..LocationIndicator.LocationIndicator import LocationIndicator
from ..SystemVisualizer.SystemVisualizer import SystemVisualizer
from ..LongRangeVisualizer.LongRangeVisualizer import LongRangeVisualizer


class ViewPort(VerticalGroup):
    can_focus = True

    def __init__(self, ship, galaxy, id=None):
        self.ship = ship
        self.galaxy = galaxy
        self.display_mode = "short"
        super().__init__(id=id)

    def compose(self):
        yield LocationIndicator(ship=self.ship, galaxy=self.galaxy)
        yield Label("", id="viewport_mode_indicator", markup=False)
        yield HorizontalGroup(id="viewport_content")

    def _replace_viewport_content(self, widget) -> None:
        content_area = self.query_one("#viewport_content")
        content_area.remove_children()
        content_area.mount(widget)

    def on_mount(self) -> None:
        self.refresh_current_display()

    def present_loadbar(self, id=None, targetvalue=0, label=None, animation_interval=100, callback=None) -> None:
        new_statusbar = StatusBar(valueInt=0, labelStr=label, totalInt=100, animation_interval=animation_interval, callback=callback)
        self._replace_viewport_content(new_statusbar)
        mode_text = "Progress"
        if label:
            mode_text = f"Progress: {label}"
        self._set_mode_indicator(mode_text)
        new_statusbar.update_value(targetvalue)

    def _present_blank(self, text: str) -> None:
        self._replace_viewport_content(Static(text, classes="viewport_empty"))
        self._set_mode_indicator("Unavailable")

    def present_system_visual(self) -> None:
        self.display_mode = "short"
        self.refresh_current_display()

    def present_longrange_visual(self) -> None:
        self.display_mode = "long"
        self.refresh_current_display()

    def refresh_current_display(self) -> None:
        if self.display_mode == "long":
            if not self.ship.has_current_system_long_range_scan():
                self._present_blank("LONG-RANGE CARTOGRAPHY UNAVAILABLE\nRun Long-range Scan in this system.")
                self._set_mode_indicator("Long Cartography (Scan Required)")
                return
            self._replace_viewport_content(
                LongRangeVisualizer(ship=self.ship, galaxy=self.galaxy)
            )
            self._set_mode_indicator("Long Cartography")
            return

        if not self.ship.has_current_system_short_range_scan():
            self._present_blank("LOCAL CARTOGRAPHY UNAVAILABLE\nRun Short-range Scan in this system.")
            self._set_mode_indicator("Local Cartography (Scan Required)")
            return

        self._replace_viewport_content(SystemVisualizer(ship=self.ship, galaxy=self.galaxy))
        self._set_mode_indicator("Local Cartography")

    def _set_mode_indicator(self, mode_text: str) -> None:
        self.query_one("#viewport_mode_indicator", Label).update(f"Mode: {mode_text}")
