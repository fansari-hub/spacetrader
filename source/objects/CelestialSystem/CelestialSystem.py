from ..GalacticCoordinates.GalacticCoordinates import GalacticCoordinates
from ..CelestialBody.CelestialBody import CelestialBody
from random import randrange, random
from ..NameGenerator import generate_body_name, generate_body_type

SYSTEM_MARKET_CHANCE = 0.90
STATION_PER_BODY_CHANCE = 0.35

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

        self._generate_orbital_stations(used_body_names)

    def _generate_orbital_stations(self, used_body_names: set[str]) -> None:
        if random() > SYSTEM_MARKET_CHANCE:
            return

        orbit_targets = [body for body in self.members if body.type in {"Planet", "Gas Giant", "Dwarf Planet"}]
        if not orbit_targets:
            orbit_targets = self.members[:1]

        station_targets = []
        for body in orbit_targets:
            if random() <= STATION_PER_BODY_CHANCE:
                station_targets.append(body)

        if not station_targets:
            station_targets.append(orbit_targets[0])

        next_id = len(self.members) + 1
        for body in station_targets:
            name = generate_body_name(self.name, "Station")
            while name in used_body_names:
                name = generate_body_name(self.name, "Station")
            used_body_names.add(name)
            offset_x = randrange(-40, 41)
            offset_y = randrange(-40, 41)
            coords = (
                max(0, min(999, body.coordinates.x + offset_x)),
                max(0, min(999, body.coordinates.y + offset_y)),
            )
            station = CelestialBody(
                coords,
                name,
                next_id,
                "Station",
                system_id=self.id,
                orbits_body_id=body.id,
                has_market=True,
            )
            self.members.append(station)
            body.moons.append(station.id)
            next_id += 1

    def to_dict(self) -> dict:
        return {
            "coordinates": self.coordinates.to_dict(),
            "name": self.name,
            "id": self.id,
            "type": self.type,
            "galaxy_id": self.galaxy_id,
            "members": [member.to_dict() for member in self.members],
        }

    @classmethod
    def from_dict(cls, data: dict):
        coords_data = data.get("coordinates", {})
        coords = (int(coords_data.get("x", 0)), int(coords_data.get("y", 0)))
        system = cls(
            coord=coords,
            name=data.get("name", "Unknown System"),
            id=int(data.get("id", 0)),
            type=data.get("type", "solar"),
            galaxy_id=int(data.get("galaxy_id", 0)),
        )
        system.members = [CelestialBody.from_dict(member) for member in data.get("members", [])]
        return system
