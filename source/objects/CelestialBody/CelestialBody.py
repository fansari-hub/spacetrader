from ..GalacticCoordinates.GalacticCoordinates import GalacticCoordinates

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
    ):
        self.coordinates = GalacticCoordinates(*coord, type="local")
        self.name = name
        self.id = id
        self.type = type
        self.moons = moons or []
        self.system_id = system_id
        self.orbits_body_id = orbits_body_id
        self.has_market = has_market

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
        )
