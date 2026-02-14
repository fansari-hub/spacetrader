from random import randrange
from ..GalacticCoordinates.GalacticCoordinates import GalacticCoordinates
from ..CelestialSystem.CelestialSystem import CelestialSystem
from ..NameGenerator import generate_galaxy_name, generate_system_name

class Galaxy():

    def __init__(self, name=None, id=0):
        self.coordinates = GalacticCoordinates(0, 0, type="glactic")
        self.name = name or generate_galaxy_name()
        self.id = id
        self.type = "galaxy"
        self.celestial_systems = []

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
    
    def get_celestial_system (self, IntSystem = 1):
        return self.celestial_systems[IntSystem-1]
