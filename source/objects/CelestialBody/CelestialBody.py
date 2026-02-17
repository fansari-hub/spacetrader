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
