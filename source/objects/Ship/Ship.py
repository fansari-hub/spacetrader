from ..Galaxy.Galaxy import Galaxy
from random import randrange
from rich.text import Text

class Ship():
    def __init__(self, galaxy: Galaxy):
        self.lifesupport_power = 100
        self.structure  = 100
        self.engine_power = 100
        self.shields = 100
        self.current_systemID = randrange(1, len(galaxy.celestial_systems) + 1)
        current_system = galaxy.celestial_systems[self.current_systemID - 1]
        self.current_localID = randrange(1, len(current_system.members) + 1)
        self.ship_coordinates_galactic = current_system.coordinates
        self.ship_coordinates_local = current_system.members[self.current_localID - 1].coordinates
        self.is_docked = False
        self.resources = 0
        self.name = "Enterprise-D"
        self.galaxy = galaxy
        self.scanned_long_range_systems = set()
        self.scanned_short_range_systems = set()
        self.visited_systems = {self.current_systemID}
        self.visited_locations_by_system = {self.current_systemID: {self.current_localID}}


    def set_engine_power(self, intValue) -> None:
        self.engine_power = max(0, min(intValue, 100))

    def get_engine_power(self) -> int:
        return self.engine_power

    def set_shields(self, intValue) -> None:
        self.shields = max(0, min(intValue, 100))

    def shield_damage(self, intValue) -> int:
        # Positive values apply damage, negative values apply repair.
        self.shields = max(0, min(self.shields - intValue, 100))
        return self.shields

    def get_shields(self) -> int:
        return self.shields
    
    def set_structure(self, intValue) -> None:
        self.structure = max(0, min(intValue, 100))

    def structure_damage(self, intValue) -> int:
        # Positive values apply damage, negative values apply repair.
        self.structure = max(0, min(self.structure - intValue, 100))
        return self.structure
    
    def get_structure(self) -> int:
        return self.structure
    
    def jump_to_system(self, intSystemID) -> None:
        self.current_systemID = intSystemID
        self.ship_coordinates_galactic = self.galaxy.celestial_systems[self.current_systemID-1].coordinates
        self.visited_systems.add(self.current_systemID)
        self.goto_location(1)

    def goto_location(self, intLocalID) -> None:
        self.current_localID = intLocalID
        self.ship_coordinates_local = self.galaxy.celestial_systems[self.current_systemID-1].members[self.current_localID-1].coordinates
        if self.current_systemID not in self.visited_locations_by_system:
            self.visited_locations_by_system[self.current_systemID] = set()
        self.visited_locations_by_system[self.current_systemID].add(self.current_localID)
    
    def get_current_system(self) -> int:
        return self.current_systemID
    
    def get_current_location(self) -> int:
        return self.current_localID

    def get_jump_distance(self, system_id: int) -> float:
        target = self.galaxy.celestial_systems[system_id - 1]
        return target.coordinates.get_distance(self.ship_coordinates_galactic)

    def get_local_distance(self, local_id: int) -> float:
        target = self.galaxy.celestial_systems[self.current_systemID - 1].members[local_id - 1]
        return target.coordinates.get_distance(self.ship_coordinates_local)
    
    def get_jump_desination(self) -> list:
        jump_destinations = self.galaxy.celestial_systems
        data = []
        for destination in jump_destinations:
            id = destination.id
            visited = id in self.visited_systems
            name = Text(destination.name, style="bold green" if visited else "grey70")
            raw_distance = destination.coordinates.get_distance(self.ship_coordinates_galactic)
            distance = self._format_interstellar_distance(raw_distance)
            data.append((id, name, distance))
        return data
    
    def get_local_destinations(self) -> list:
        local_system = self.galaxy.get_celestial_system(self.current_systemID).members
        visited_locations = self.visited_locations_by_system.get(self.current_systemID, set())
        data = []
        for local in local_system:
            id = local.id
            visited = id in visited_locations
            name = Text(local.name, style="bold green" if visited else "grey70")
            raw_distance = local.coordinates.get_distance(self.ship_coordinates_local)
            distance = self._format_local_distance(raw_distance)
            type = local.type
            data.append((id, name, type, distance))
        return data

    def _format_interstellar_distance(self, distance: float) -> str:
        return f"{distance:,.1f} ly"

    def _format_local_distance(self, distance: float) -> str:
        return f"{distance:,.1f} million km"

    def format_interstellar_distance(self, distance: float) -> str:
        return self._format_interstellar_distance(distance)

    def format_local_distance(self, distance: float) -> str:
        return self._format_local_distance(distance)

    def mark_long_range_scan(self) -> None:
        self.scanned_long_range_systems.add(self.current_systemID)

    def mark_short_range_scan(self) -> None:
        self.scanned_short_range_systems.add(self.current_systemID)

    def has_current_system_long_range_scan(self) -> bool:
        return self.current_systemID in self.scanned_long_range_systems

    def has_current_system_short_range_scan(self) -> bool:
        return self.current_systemID in self.scanned_short_range_systems


    
    def dock(self) -> None:
        self.is_docked = True
    
    def undock(self) -> None:
        self.is_docked = False
