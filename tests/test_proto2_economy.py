"""Economy behavior tests for Proto2."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

SOURCE_ROOT = Path(__file__).resolve().parents[1] / "source"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from proto2.engine import Captain, Order, Simulation  # noqa: E402


class MarketTests(unittest.TestCase):
    def test_trade_order_changes_shared_market_and_captain_state(self) -> None:
        simulation = Simulation(seed="cinder-reach")
        simulation.register_captain(Captain(id="human-1", name="Farid", kind="human"))
        station_id = simulation.world.sector_at(0, 0).systems[0].id
        opening_stock = simulation.market_stock(station_id, "fuel")
        opening_credits = simulation.captains["human-1"].credits

        simulation.queue_order(
            Order(captain_id="human-1", action="buy", target=station_id, commodity="fuel", amount=2)
        )
        events = simulation.resolve_turn()

        self.assertEqual(simulation.captains["human-1"].cargo["fuel"], 2)
        self.assertLess(simulation.captains["human-1"].credits, opening_credits)
        self.assertEqual(simulation.market_stock(station_id, "fuel"), opening_stock - 2)
        self.assertEqual(events[0].action, "buy")


class SituationTests(unittest.TestCase):
    def test_market_depletion_creates_a_persistent_shortage_lead(self) -> None:
        simulation = Simulation(seed="cinder-reach")
        simulation.register_captain(Captain(id="human-1", name="Farid", kind="human"))
        station_id = simulation.world.sector_at(0, 0).systems[0].id

        simulation.queue_order(Order(captain_id="human-1", action="buy", target=station_id, commodity="fuel", amount=99))
        events = simulation.resolve_turn()

        self.assertTrue(any(event.action == "situation" for event in events))
        self.assertIn(f"fuel_shortage:{station_id}", simulation.world_facts)


if __name__ == "__main__":
    unittest.main()
