"""Behavior tests for the Proto2 shared-world simulation."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = PROJECT_ROOT / "source"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from proto2.engine import Captain, Order, Simulation, TraderAI, World  # noqa: E402
from proto2.app import build_demo_simulation  # noqa: E402


class WorldGenerationTests(unittest.TestCase):
    def test_sector_generation_is_stable_for_a_world_seed(self) -> None:
        first = World(seed="cinder-reach").sector_at(0, 0)
        second = World(seed="cinder-reach").sector_at(0, 0)

        self.assertEqual(first, second)
        self.assertEqual(first.coordinate, (0, 0))
        self.assertGreaterEqual(len(first.systems), 3)
        self.assertTrue(all(system.station_role for system in first.systems))


class TurnResolutionTests(unittest.TestCase):
    def test_human_and_ai_orders_share_a_deterministic_event_log(self) -> None:
        simulation = Simulation(seed="cinder-reach")
        simulation.register_captain(Captain(id="human-1", name="Farid", kind="human"))
        simulation.register_captain(Captain(id="ai-1", name="Mara", kind="ai"))

        simulation.queue_order(Order(captain_id="human-1", action="scan"))
        simulation.queue_order(TraderAI("ai-1").choose_order(simulation))
        events = simulation.resolve_turn()

        self.assertEqual([event.captain_id for event in events], ["ai-1", "human-1"])
        self.assertEqual([event.action for event in events], ["scan", "scan"])
        self.assertEqual([event.turn for event in events], [1, 1])
        self.assertEqual(simulation.events, events)


class DemoSetupTests(unittest.TestCase):
    def test_demo_registers_a_human_and_an_ai_captain(self) -> None:
        simulation = build_demo_simulation()

        self.assertEqual(simulation.captains["human-1"].kind, "human")
        self.assertEqual(simulation.captains["ai-1"].kind, "ai")
        self.assertEqual(simulation.world.seed, "cinder-reach")


if __name__ == "__main__":
    unittest.main()
