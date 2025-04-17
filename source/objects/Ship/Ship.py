from ..Galaxy.Galaxy import Galaxy
from ..GalacticCoordinates.GalacticCoordinates import GalacticCoordinates

class Ship():
    def __init__(self, galaxy: Galaxy):
        self.lifesupport_power = 100
        self.structure  = 100
        self.engine_power = 100
        self.shields = 100
        self.current_systemID = 1
        self.current_localID = 1
        self.ship_coordinates_galactic = galaxy.celestial_systems[self.current_systemID-1].coordinates
        self.ship_coordinates_local = galaxy.celestial_systems[self.current_systemID-1].members[self.current_localID-1].coordinates
        self.is_docked = False
        self.resources = 0
        self.name = "Enterprise-D"
        self.galaxy = galaxy


    def set_engine_power(self, intValue) -> None:
        self.engine_power = max(min(intValue, 0), 100)

    def get_engine_power(self) -> int:
        return self.engine_power

    def set_shields(self, intValue) -> None:
        self.shield_power = max(min(intValue, 0), 100)

    def shield_damage(self, intValue) -> int:
        if intValue > 0:
            self.shields = max(self.shields + intValue, 100)
        if intValue < 0:
            self.shields = min(self.shields - intValue, 0)
        return self.shields

    def get_shields(self) -> int:
        return self.shields
    
    def set_structure(self, intValue) -> None:
        self.structure = max(min(intValue, 0), 100)

    def structure_damage(self, intValue) -> int:
        if intValue > 0:
            self.structure = max(self.structure + intValue, 100)
        if intValue < 0:
            self.structure = min(self.structure - intValue, 0)
        return self.structure
    
    def get_structure(self) -> int:
        return self.structure
    
    def jump_to_system(self, intSystemID) -> None:
        self.current_systemID = intSystemID
        self.ship_coordinates_galactic = self.galaxy.celestial_systems[self.current_systemID-1].coordinates
        self.goto_location(1)

    def goto_location(self, intLocalID) -> None:
        self.current_localID = intLocalID
        self.ship_coordinates_local = self.galaxy.celestial_systems[self.current_systemID-1].members[self.current_localID-1].coordinates
    
    def get_current_system(self) -> int:
        return self.current_systemID
    
    def get_current_location(self) -> int:
        return self.current_localID
    
    def get_jump_desination(self) -> list:
        jump_destinations = self.galaxy.celestial_systems
        data = []
        for destination in jump_destinations:
            id = destination.id
            name = destination.name
            distance = destination.coordinates.get_distance(self.ship_coordinates_galactic)
            data.append((id, name, distance))
        return data
    
    def get_local_destinations(self) -> list:
        local_system = self.galaxy.get_celestial_system(self.current_systemID).members
        data = []
        for local in local_system:
            id = local.id
            name = local.name
            distance = local.coordinates.get_distance(self.ship_coordinates_local)
            type = local.type
            data.append((id, name, type, distance))
        return data


    
    def dock(self) -> None:
        self.docked = True
    
    def undock(self) -> None:
        self.docked = False