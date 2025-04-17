from ..GalacticCoordinates.GalacticCoordinates import GalacticCoordinates

class CelestialBody():
    def __init__(self, coord=(0,0), name="Planet Earth", id=0, type="planet", moons=[], system_id=0):
        self.coordinates = GalacticCoordinates(*coord, type="local")
        self.name = name
        self.id = id
        self.type = type
        self.moons = moons
        self.system_id = system_id