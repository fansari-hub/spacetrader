class Ship():
    def __init__(self):
        self.lifesupport_power = 100
        self.structure  = 100
        self.engine_power = 100
        self.shields = 100
        self.current_systemID = 0
        self.current_localID = 0
        self.is_docked = False
        self.resources = 0
        self.name = "Enterprise-D"

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

    def goto_location(self, intLocalID) -> None:
        self.current_localID = intLocalID        
    
    def get_currentLocation(self) -> tuple:
        return (self.current_systemID, self.current_localID)
    
    def dock(self) -> None:
        self.docked = True
    
    def undock(self) -> None:
        self.docked = False