from random import randrange
from ..GalacticCoordinates.GalacticCoordinates import GalacticCoordinates
from ..CelestialSystem.CelestialSystem import CelestialSystem
from ..NameGenerator import generate_galaxy_name, generate_system_name
from ..MarketConfig import MARKET_COMMODITY_DEFS

class Galaxy():

    def __init__(self, name=None, id=0):
        self.coordinates = GalacticCoordinates(0, 0, type="glactic")
        self.name = name or generate_galaxy_name()
        self.id = id
        self.type = "galaxy"
        self.celestial_systems = []
        self.system_markets = {}

    def generate_galaxy(self, intSize=20):
        used_system_names = {system.name for system in self.celestial_systems}
        for x in range(1, intSize+1):
            coord_x = randrange(1000)
            coord_y = randrange(1000)
            coords = (coord_x, coord_y)
            name = generate_system_name()
            while name in used_system_names:
                name = generate_system_name()
            used_system_names.add(name)
            type = "solar"
            new_system = CelestialSystem(coords, name, x, type, galaxy_id=self.id)
            self.celestial_systems.append(new_system)
            # Generate at least one local body so ship/local UI always has a valid target.
            new_system.generate_system(randrange(1, 16))
            self.system_markets[new_system.id] = self._generate_system_market()
            self._ensure_market_has_all_commodities(self.system_markets[new_system.id])
    
    def get_celestial_system (self, IntSystem = 1):
        return self.celestial_systems[IntSystem-1]

    def get_system_market_rows(self, system_id: int, ship) -> list[tuple]:
        market = self.system_markets.get(system_id, {})
        rows = []
        index = 1
        for commodity_id, data in market.items():
            player_qty = ship.cargo_manifest.get(commodity_id, 0)
            rows.append(
                (
                    index,
                    data["name"],
                    f"{data['price']} cr",
                    data["stock"],
                    player_qty,
                )
            )
            index += 1
        return rows

    def get_market_commodity_id(self, system_id: int, row_index: int) -> str | None:
        market = self.system_markets.get(system_id, {})
        keys = list(market.keys())
        if 1 <= row_index <= len(keys):
            return keys[row_index - 1]
        return None

    def market_price(self, system_id: int, commodity_id: str) -> int:
        return self.system_markets[system_id][commodity_id]["price"]

    def market_stock(self, system_id: int, commodity_id: str) -> int:
        return self.system_markets[system_id][commodity_id]["stock"]

    def market_decrease_stock(self, system_id: int, commodity_id: str, quantity: int = 1) -> None:
        market_item = self.system_markets[system_id][commodity_id]
        market_item["stock"] = max(0, market_item["stock"] - quantity)

    def market_increase_stock(self, system_id: int, commodity_id: str, quantity: int = 1) -> None:
        market_item = self.system_markets[system_id][commodity_id]
        market_item["stock"] += quantity

    def _generate_system_market(self) -> dict:
        market = {}
        for commodity in MARKET_COMMODITY_DEFS:
            volatility = randrange(
                int(commodity.get("volatility_min", -35)),
                int(commodity.get("volatility_max", 45)) + 1,
            )
            price = max(5, commodity["base_price"] + volatility)
            stock = randrange(
                int(commodity.get("stock_min", 8)),
                int(commodity.get("stock_max", 60)) + 1,
            )
            market[commodity["id"]] = {
                "name": commodity["name"],
                "price": price,
                "stock": stock,
            }
        return market

    def _ensure_market_has_all_commodities(self, market: dict) -> None:
        for commodity in MARKET_COMMODITY_DEFS:
            commodity_id = commodity["id"]
            if commodity_id in market:
                continue
            volatility = randrange(
                int(commodity.get("volatility_min", -35)),
                int(commodity.get("volatility_max", 45)) + 1,
            )
            price = max(5, int(commodity["base_price"]) + volatility)
            stock = randrange(
                int(commodity.get("stock_min", 8)),
                int(commodity.get("stock_max", 60)) + 1,
            )
            market[commodity_id] = {
                "name": commodity["name"],
                "price": price,
                "stock": stock,
            }

    def to_dict(self) -> dict:
        return {
            "coordinates": self.coordinates.to_dict(),
            "name": self.name,
            "id": self.id,
            "type": self.type,
            "celestial_systems": [system.to_dict() for system in self.celestial_systems],
            "system_markets": {
                str(system_id): {
                    commodity_id: {
                        "name": commodity_data.get("name", ""),
                        "price": int(commodity_data.get("price", 0)),
                        "stock": int(commodity_data.get("stock", 0)),
                    }
                    for commodity_id, commodity_data in market.items()
                }
                for system_id, market in self.system_markets.items()
            },
        }

    def apply_state(self, data: dict) -> None:
        self.name = data.get("name", self.name)
        self.id = int(data.get("id", self.id))
        self.type = data.get("type", self.type)

        coords_data = data.get("coordinates", {})
        self.coordinates.x = int(coords_data.get("x", self.coordinates.x))
        self.coordinates.y = int(coords_data.get("y", self.coordinates.y))
        self.coordinates.type = coords_data.get("type", self.coordinates.type)

        self.celestial_systems = [
            CelestialSystem.from_dict(system_data)
            for system_data in data.get("celestial_systems", [])
        ]

        self.system_markets = {}
        for system_id, market in data.get("system_markets", {}).items():
            sid = int(system_id)
            self.system_markets[sid] = {}
            for commodity_id, commodity_data in market.items():
                self.system_markets[sid][commodity_id] = {
                    "name": commodity_data.get("name", commodity_id),
                    "price": int(commodity_data.get("price", 0)),
                    "stock": int(commodity_data.get("stock", 0)),
                }
            self._ensure_market_has_all_commodities(self.system_markets[sid])
        for system in self.celestial_systems:
            if system.id not in self.system_markets:
                self.system_markets[system.id] = self._generate_system_market()
            else:
                self._ensure_market_has_all_commodities(self.system_markets[system.id])
