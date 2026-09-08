"""Keyboard-first Textual client for the Proto2 shared-world vertical slice."""

from __future__ import annotations

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header, Static

from .engine import Captain, Order, Simulation, TraderAI


DEMO_STATION_ID = "0:0:0"


def build_demo_simulation() -> Simulation:
    """Create a deterministic local session containing one human and one AI captain."""
    simulation = Simulation(seed="cinder-reach")
    simulation.register_captain(Captain(id="human-1", name="Farid", kind="human"))
    simulation.register_captain(Captain(id="ai-1", name="Mara Vale", kind="ai"))
    return simulation


class Proto2(App):
    TITLE = "SpaceTrader Proto2 — Cinder Reach"
    CSS = """
    Screen { background: #101820; color: #d9e7ef; }
    #title { color: #6ce5e8; text-style: bold; height: 3; padding: 1 2; }
    #world, #captain, #log { border: round #397a8c; padding: 1; margin: 1; }
    #world { width: 2fr; }
    #captain { width: 1fr; }
    #log { height: 12; }
    .heading { color: #ffc857; text-style: bold; }
    """
    BINDINGS = [
        ("s", "queue_scan", "Queue Scan"),
        ("b", "queue_fuel", "Buy Fuel"),
        ("r", "resolve", "Resolve Turn"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.simulation = build_demo_simulation()
        self.ai = TraderAI("ai-1")
        self.messages = ["Welcome to Cinder Reach. Queue an order, then resolve the cycle."]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("CINDER REACH // shared procedural frontier", id="title")
        with Horizontal():
            yield Static(id="world")
            yield Static(id="captain")
        yield Static(id="log")
        yield Footer()

    def on_mount(self) -> None:
        self._refresh_view()

    def action_queue_scan(self) -> None:
        self._queue_human(Order(captain_id="human-1", action="scan"))

    def action_queue_fuel(self) -> None:
        self._queue_human(Order(
            captain_id="human-1", action="buy", target=DEMO_STATION_ID, commodity="fuel", amount=2,
        ))

    def action_resolve(self) -> None:
        if not any(order.captain_id == "ai-1" for order in self.simulation._pending_orders):
            self.simulation.queue_order(self.ai.choose_order(self.simulation))
        events = self.simulation.resolve_turn()
        self.messages.extend(f"T{event.turn} [{event.action.upper()}] {event.detail}" for event in events)
        self.messages = self.messages[-8:]
        self._refresh_view()

    def _queue_human(self, order: Order) -> None:
        try:
            self.simulation.queue_order(order)
        except ValueError as exc:
            self.messages.append(f"Order rejected: {exc}")
        else:
            self.messages.append(f"Order queued: {order.action.upper()}. Press R to resolve the cycle.")
        self._refresh_view()

    def _refresh_view(self) -> None:
        sector = self.simulation.world.sector_at(0, 0)
        systems = "\n".join(
            f"  {system.name:<18} {system.station_role:<16} danger {system.danger}/5"
            for system in sector.systems
        )
        fuel_price = self.simulation.market_price(DEMO_STATION_ID, "fuel")
        fuel_stock = self.simulation.market_stock(DEMO_STATION_ID, "fuel")
        self.query_one("#world", Static).update(
            f"[b]SECTOR 0,0 — CINDER REACH[/b]\n{systems}\n\n"
            f"Station market: Fuel {fuel_price} cr | stock {fuel_stock}\n"
            f"World facts: {', '.join(sorted(self.simulation.world_facts)) or 'none'}"
        )
        human = self.simulation.captains["human-1"]
        ai = self.simulation.captains["ai-1"]
        self.query_one("#captain", Static).update(
            f"[b]CAPTAIN STATUS[/b]\n\n{human.name} (human)\n"
            f"Credits: {human.credits}\nCargo: {human.cargo or 'empty'}\nScans: {human.scans}\n\n"
            f"{ai.name} (AI trader)\nScans: {ai.scans}\n\n"
            f"Cycle: {self.simulation.turn + 1}\n"
            "\n[S] scan\n[B] buy 2 fuel\n[R] resolve"
        )
        self.query_one("#log", Static).update("[b]SECTOR BULLETIN[/b]\n" + "\n".join(self.messages))


if __name__ == "__main__":
    Proto2().run()
