"""Deterministic shared-world simulation for the Proto2 vertical slice."""

from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
from random import Random

STATION_ROLES = (
    "Refinery", "Mining Exchange", "Frontier Colony", "Shipyard", "Freeport", "Listening Post",
)
SYSTEM_PREFIXES = ("Cinder", "Vela", "Kestrel", "Orison", "Nadir", "Morrow")
SYSTEM_SUFFIXES = ("Reach", "Gate", "Drift", "Belt", "Haven", "Span")
COMMODITIES = {"fuel": 90, "ore": 55, "parts": 180, "med": 240, "food": 40}


@dataclass(frozen=True)
class System:
    id: str
    name: str
    station_role: str
    danger: int


@dataclass(frozen=True)
class Sector:
    coordinate: tuple[int, int]
    systems: tuple[System, ...]


@dataclass
class MarketItem:
    price: int
    stock: int


class World:
    """A lazily generated canonical world identified by a stable seed."""

    def __init__(self, seed: str) -> None:
        self.seed = seed

    def sector_at(self, x: int, y: int) -> Sector:
        rng = Random(self._seed_for("sector", x, y))
        systems = []
        for index in range(rng.randint(3, 5)):
            systems.append(System(
                id=f"{x}:{y}:{index}",
                name=f"{rng.choice(SYSTEM_PREFIXES)} {rng.choice(SYSTEM_SUFFIXES)}",
                station_role=rng.choice(STATION_ROLES),
                danger=rng.randint(1, 5),
            ))
        return Sector(coordinate=(x, y), systems=tuple(systems))

    def _seed_for(self, *parts: object) -> int:
        source = "|".join((self.seed, *(str(part) for part in parts)))
        return int(sha256(source.encode("utf-8")).hexdigest()[:16], 16)


@dataclass
class Captain:
    """A human or AI captain; both submit the same order type."""

    id: str
    name: str
    kind: str
    sector: tuple[int, int] = (0, 0)
    credits: int = 1_000
    cargo: dict[str, int] = field(default_factory=dict)
    scans: int = 0


@dataclass(frozen=True)
class Order:
    captain_id: str
    action: str
    target: str | None = None
    commodity: str | None = None
    amount: int = 1


@dataclass(frozen=True)
class Event:
    turn: int
    captain_id: str
    action: str
    detail: str


class TraderAI:
    """A transparent first AI policy that obeys the public order contract."""

    def __init__(self, captain_id: str) -> None:
        self.captain_id = captain_id

    def choose_order(self, simulation: "Simulation") -> Order:
        if self.captain_id not in simulation.captains:
            raise ValueError("AI captain must be registered before choosing an order.")
        return Order(captain_id=self.captain_id, action="scan")


class Simulation:
    """Server-authoritative turn resolver with an append-only public event log."""

    def __init__(self, seed: str) -> None:
        self.world = World(seed)
        self.turn = 0
        self.captains: dict[str, Captain] = {}
        self._pending_orders: list[Order] = []
        self.events: list[Event] = []
        self.world_facts: set[str] = set()
        self._markets: dict[str, dict[str, MarketItem]] = {}

    def register_captain(self, captain: Captain) -> None:
        if captain.kind not in {"human", "ai"}:
            raise ValueError("Captain kind must be 'human' or 'ai'.")
        if captain.id in self.captains:
            raise ValueError(f"Captain '{captain.id}' already exists.")
        self.captains[captain.id] = captain

    def market_stock(self, station_id: str, commodity: str) -> int:
        return self._market_for(station_id)[commodity].stock

    def market_price(self, station_id: str, commodity: str) -> int:
        return self._market_for(station_id)[commodity].price

    def queue_order(self, order: Order) -> None:
        if order.captain_id not in self.captains:
            raise ValueError("Order captain is not registered.")
        if order.action not in {"scan", "buy"}:
            raise ValueError("Unsupported action.")
        if order.action == "buy":
            if not order.target or order.commodity not in COMMODITIES or order.amount <= 0:
                raise ValueError("Buy orders require a station, known commodity, and positive amount.")
        if any(pending.captain_id == order.captain_id for pending in self._pending_orders):
            raise ValueError("Only one order per captain may be queued each turn.")
        self._pending_orders.append(order)

    def resolve_turn(self) -> list[Event]:
        self.turn += 1
        resolved: list[Event] = []
        for order in sorted(self._pending_orders, key=lambda item: item.captain_id):
            captain = self.captains[order.captain_id]
            if order.action == "scan":
                captain.scans += 1
                sector = self.world.sector_at(*captain.sector)
                detail = f"Scan complete: {len(sector.systems)} systems charted in sector {captain.sector}."
            else:
                detail = self._resolve_buy(captain, order)
            resolved.append(Event(self.turn, captain.id, order.action, detail))
            if order.action == "buy":
                situation = self._depletion_situation(order)
                if situation:
                    resolved.append(Event(self.turn, captain.id, "situation", situation))
        self.events.extend(resolved)
        self._pending_orders.clear()
        return resolved

    def _resolve_buy(self, captain: Captain, order: Order) -> str:
        assert order.target is not None and order.commodity is not None
        item = self._market_for(order.target)[order.commodity]
        quantity = min(order.amount, item.stock)
        if quantity <= 0:
            return f"Market empty: no {order.commodity} available."
        affordable = captain.credits // item.price
        quantity = min(quantity, affordable)
        if quantity <= 0:
            return f"Purchase declined: insufficient credits for {order.commodity}."
        total = quantity * item.price
        item.stock -= quantity
        captain.credits -= total
        captain.cargo[order.commodity] = captain.cargo.get(order.commodity, 0) + quantity
        return f"Purchased {quantity} {order.commodity} for {total} credits at {order.target}."

    def _depletion_situation(self, order: Order) -> str | None:
        assert order.target is not None and order.commodity is not None
        if self.market_stock(order.target, order.commodity) > 3:
            return None
        fact = f"{order.commodity}_shortage:{order.target}"
        if fact in self.world_facts:
            return None
        self.world_facts.add(fact)
        return f"Situation opened: {order.commodity.title()} shortage at {order.target}; escort and supply contracts expected."

    def _market_for(self, station_id: str) -> dict[str, MarketItem]:
        if station_id not in self._markets:
            rng = Random(self.world._seed_for("market", station_id))
            self._markets[station_id] = {
                commodity: MarketItem(
                    price=max(10, base_price + rng.randint(-20, 30)),
                    stock=rng.randint(6, 18),
                )
                for commodity, base_price in COMMODITIES.items()
            }
        return self._markets[station_id]
