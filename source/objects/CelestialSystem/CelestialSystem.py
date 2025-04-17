from ..GalacticCoordinates.GalacticCoordinates import GalacticCoordinates
from ..CelestialBody.CelestialBody import CelestialBody
import uuid
from random import randrange

class CelestialSystem():
    def __init__(self, coord=(0,0), name="The Solar System", id=0, type="Solar", galaxy_id=0):
        self.coordinates = GalacticCoordinates(*coord)
        self.name = name
        self.id = id
        self.type = type
        self.members = []
        self.galaxy_id = galaxy_id


    def generate_system(self, intSize : int):
        for x in range(1, intSize):
            coord_x = randrange(1000)
            coord_y = randrange(1000)
            coords = (coord_x, coord_y)
            name = uuid.uuid4()
            type = "planet"
            new_member = CelestialBody(coords, name, x, type, system_id=self.id)
            self.members.append(new_member)