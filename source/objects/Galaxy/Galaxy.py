from random import randrange
from ..GalacticCoordinates.GalacticCoordinates import GalacticCoordinates
from ..CelestialSystem.CelestialSystem import CelestialSystem
from ..NameGenerator import generate_galaxy_name, generate_system_name

COMMODITY_DEFS = (
    {"id": "food", "name": "Food Rations", "base_price": 45},
    {"id": "ore", "name": "Raw Ore", "base_price": 75},
    {"id": "fuel", "name": "Refined Fuel", "base_price": 120},
    {"id": "parts", "name": "Ship Parts", "base_price": 190},
    {"id": "med", "name": "Medical Supplies", "base_price": 260},
)

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
        for commodity in COMMODITY_DEFS:
            volatility = randrange(-35, 46)
            price = max(5, commodity["base_price"] + volatility)
            stock = randrange(8, 61)
            market[commodity["id"]] = {
                "name": commodity["name"],
                "price": price,
                "stock": stock,
            }
        return market
