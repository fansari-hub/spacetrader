from ..GalacticCoordinates.GalacticCoordinates import GalacticCoordinates
from ..ExtractionConfig import EXTRACTABLE_BODY_TYPES, generate_resource_pool

class CelestialBody():
    def __init__(
        self,
        coord=(0,0),
        name="Planet Earth",
        id=0,
        type="planet",
        moons=None,
        system_id=0,
        orbits_body_id=None,
        has_market=False,
        extractable_resources=None,
        extraction_scanned=False,
    ):
        self.coordinates = GalacticCoordinates(*coord, type="local")
        self.name = name
        self.id = id
        self.type = type
        self.moons = moons or []
        self.system_id = system_id
        self.orbits_body_id = orbits_body_id
        self.has_market = has_market
        self.extractable_resources = self._normalize_resource_pool(extractable_resources or {})
        self.extraction_scanned = bool(extraction_scanned)
        if self.type in EXTRACTABLE_BODY_TYPES and not self.extractable_resources:
            self.extractable_resources = generate_resource_pool()

    def _normalize_resource_pool(self, pool: dict) -> dict[str, int]:
        normalized = {}
        for resource_id, quantity in pool.items():
            amount = int(quantity)
            if amount > 0:
                normalized[str(resource_id)] = amount
        return normalized

    def get_resource_total(self) -> int:
        return sum(self.extractable_resources.values())

    def to_dict(self) -> dict:
        return {
            "coordinates": self.coordinates.to_dict(),
            "name": self.name,
            "id": self.id,
            "type": self.type,
            "moons": list(self.moons),
            "system_id": self.system_id,
            "orbits_body_id": self.orbits_body_id,
            "has_market": self.has_market,
            "extractable_resources": {
                resource_id: int(quantity)
                for resource_id, quantity in self.extractable_resources.items()
            },
            "extraction_scanned": self.extraction_scanned,
        }

    @classmethod
    def from_dict(cls, data: dict):
        coords_data = data.get("coordinates", {})
        coords = (int(coords_data.get("x", 0)), int(coords_data.get("y", 0)))
        return cls(
            coord=coords,
            name=data.get("name", "Unknown"),
            id=int(data.get("id", 0)),
            type=data.get("type", "Planet"),
            moons=[int(moon_id) for moon_id in data.get("moons", [])],
            system_id=int(data.get("system_id", 0)),
            orbits_body_id=data.get("orbits_body_id"),
            has_market=bool(data.get("has_market", False)),
            extractable_resources=data.get("extractable_resources", {}),
            extraction_scanned=bool(data.get("extraction_scanned", False)),
        )
