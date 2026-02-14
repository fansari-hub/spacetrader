from ..GalacticCoordinates.GalacticCoordinates import GalacticCoordinates
from ..CelestialBody.CelestialBody import CelestialBody
from random import randrange
from ..NameGenerator import generate_body_name, generate_body_type

class CelestialSystem():
    def __init__(self, coord=(0,0), name="The Solar System", id=0, type="Solar", galaxy_id=0):
        self.coordinates = GalacticCoordinates(*coord)
        self.name = name
        self.id = id
        self.type = type
        self.members = []
        self.galaxy_id = galaxy_id


    def generate_system(self, intSize : int):
        intSize = max(1, intSize)
        used_body_names = {member.name for member in self.members}
        for x in range(1, intSize + 1):
            coord_x = randrange(1000)
            coord_y = randrange(1000)
            coords = (coord_x, coord_y)
            body_type = generate_body_type(x)
            name = generate_body_name(self.name, body_type)
            while name in used_body_names:
                name = generate_body_name(self.name, body_type)
            used_body_names.add(name)
            new_member = CelestialBody(coords, name, x, body_type, system_id=self.id)
            self.members.append(new_member)
