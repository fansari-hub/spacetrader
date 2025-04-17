import uuid
from random import randrange
from ..GalacticCoordinates.GalacticCoordinates import GalacticCoordinates
from ..CelestialSystem.CelestialSystem import CelestialSystem

class Galaxy():

    def __init__(self, name="The Galaxy", id=0):
        self.coordinates = GalacticCoordinates(0, 0, type="glactic")
        self.name = name
        self.id = id
        self.type = "galaxy"
        self.celestial_systems = []

    def generate_galaxy(self, intSize=20):
        for x in range(1, intSize+1):
            coord_x = randrange(1000)
            coord_y = randrange(1000)
            coords = (coord_x, coord_y)
            name = uuid.uuid4()
            type = "solar"
            new_system = CelestialSystem(coords, name, x, type, galaxy_id=self.id)
            self.celestial_systems.append(new_system)
            new_system.generate_system(randrange(15))
    
    def get_celestial_system (self, IntSystem = 1):
        return self.celestial_systems[IntSystem-1]
