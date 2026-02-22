from ..Galaxy.Galaxy import Galaxy
from random import randrange
from math import ceil
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
        self.credits = 2000
        self.fuel = 100
        self.cargo_capacity = 20
        self.cargo_manifest = {}
        self.name = "Enterprise-D"
        self.galaxy = galaxy
        self.scanned_long_range_systems = set()
        self.scanned_short_range_systems = set()
        self.visited_systems = {self.current_systemID}
        self.visited_locations_by_system = {self.current_systemID: {self.current_localID}}
        self.selected_jump_system_id = self.current_systemID
        self.selected_local_id = self.current_localID
        self.travel_event_index = 0
        # Starting sector is immediately known to the player.
        self.mark_long_range_scan()
        self.mark_short_range_scan()


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
        self.selected_jump_system_id = intSystemID
        self.goto_location(1)

    def goto_location(self, intLocalID) -> None:
        self.current_localID = intLocalID
        self.ship_coordinates_local = self.galaxy.celestial_systems[self.current_systemID-1].members[self.current_localID-1].coordinates
        self.selected_local_id = intLocalID
        if self.current_systemID not in self.visited_locations_by_system:
            self.visited_locations_by_system[self.current_systemID] = set()
        self.visited_locations_by_system[self.current_systemID].add(self.current_localID)
    
    def get_current_system(self) -> int:
        return self.current_systemID
    
    def get_current_location(self) -> int:
        return self.current_localID

    def get_current_body(self):
        return self.galaxy.celestial_systems[self.current_systemID - 1].members[self.current_localID - 1]

    def get_jump_fuel_cost(self, distance: float) -> int:
        return max(3, ceil(distance / 120.0))

    def get_local_fuel_cost(self, distance: float) -> int:
        return max(1, ceil(distance / 250.0))

    def can_spend_fuel(self, amount: int) -> bool:
        return self.fuel >= amount

    def spend_fuel(self, amount: int) -> None:
        self.fuel = max(0, self.fuel - amount)

    def get_jump_distance(self, system_id: int) -> float:
        target = self.galaxy.celestial_systems[system_id - 1]
        return target.coordinates.get_distance(self.ship_coordinates_galactic)

    def get_local_distance(self, local_id: int) -> float:
        target = self.galaxy.celestial_systems[self.current_systemID - 1].members[local_id - 1]
        return target.coordinates.get_distance(self.ship_coordinates_local)

    def get_selected_jump_system_id(self) -> int:
        if not 1 <= self.selected_jump_system_id <= len(self.galaxy.celestial_systems):
            self.selected_jump_system_id = self.current_systemID
        return self.selected_jump_system_id

    def get_selected_local_id(self) -> int:
        members = self.galaxy.celestial_systems[self.current_systemID - 1].members
        if not members:
            self.selected_local_id = 0
            return 0
        if not 1 <= self.selected_local_id <= len(members):
            self.selected_local_id = self.current_localID
        return self.selected_local_id

    def shift_selected_jump(self, step: int) -> int:
        ordered_ids = self.get_ordered_jump_system_ids()
        total = len(ordered_ids)
        if total == 0:
            self.selected_jump_system_id = 0
            return 0
        current = self.get_selected_jump_system_id()
        if current not in ordered_ids:
            current = ordered_ids[0]
        current_idx = ordered_ids.index(current)
        self.selected_jump_system_id = ordered_ids[(current_idx + step) % total]
        return self.selected_jump_system_id

    def shift_selected_local(self, step: int) -> int:
        ordered_ids = self.get_ordered_local_ids()
        total = len(ordered_ids)
        if total == 0:
            self.selected_local_id = 0
            return 0
        current = self.get_selected_local_id()
        if current not in ordered_ids:
            current = ordered_ids[0]
        current_idx = ordered_ids.index(current)
        self.selected_local_id = ordered_ids[(current_idx + step) % total]
        return self.selected_local_id

    def get_ordered_jump_system_ids(self) -> list[int]:
        systems = list(self.galaxy.celestial_systems)
        if not systems:
            return []
        current_id = self.current_systemID
        current_coords = self.ship_coordinates_galactic

        other_ids = [system.id for system in systems if system.id != current_id]
        other_ids.sort(
            key=lambda sid: self.galaxy.get_celestial_system(sid).coordinates.get_distance(current_coords),
            reverse=False,
        )
        return [current_id] + other_ids

    def get_ordered_local_ids(self) -> list[int]:
        members = list(self.galaxy.celestial_systems[self.current_systemID - 1].members)
        if not members:
            return []
        anchor = self.ship_coordinates_local
        ordered = sorted(
            members,
            key=lambda body: (
                body.coordinates.get_distance(anchor),
                body.id,
            ),
        )
        return [body.id for body in ordered]
    
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
            type = f"{local.type} (Market)" if local.has_market else local.type
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

    def get_cargo_used(self) -> int:
        return sum(self.cargo_manifest.values())

    def get_cargo_free(self) -> int:
        return max(0, self.cargo_capacity - self.get_cargo_used())

    def can_buy(self, unit_price: int, quantity: int = 1) -> tuple[bool, str]:
        if self.get_cargo_free() < quantity:
            return False, "Cargo hold is full."
        total_cost = unit_price * quantity
        if self.credits < total_cost:
            return False, "Insufficient credits."
        return True, ""

    def buy_commodity(self, commodity_id: str, unit_price: int, quantity: int = 1) -> None:
        self.credits -= unit_price * quantity
        self.cargo_manifest[commodity_id] = self.cargo_manifest.get(commodity_id, 0) + quantity

    def can_sell(self, commodity_id: str, quantity: int = 1) -> tuple[bool, str]:
        if self.cargo_manifest.get(commodity_id, 0) < quantity:
            return False, "Insufficient cargo."
        return True, ""

    def sell_commodity(self, commodity_id: str, unit_price: int, quantity: int = 1) -> None:
        self.credits += unit_price * quantity
        new_qty = self.cargo_manifest.get(commodity_id, 0) - quantity
        if new_qty > 0:
            self.cargo_manifest[commodity_id] = new_qty
        else:
            self.cargo_manifest.pop(commodity_id, None)

    
    def dock(self) -> None:
        self.is_docked = True
    
    def undock(self) -> None:
        self.is_docked = False

    def to_dict(self) -> dict:
        return {
            "lifesupport_power": self.lifesupport_power,
            "structure": self.structure,
            "engine_power": self.engine_power,
            "shields": self.shields,
            "current_systemID": self.current_systemID,
            "current_localID": self.current_localID,
            "is_docked": self.is_docked,
            "resources": self.resources,
            "credits": self.credits,
            "fuel": self.fuel,
            "cargo_capacity": self.cargo_capacity,
            "cargo_manifest": {key: int(value) for key, value in self.cargo_manifest.items()},
            "name": self.name,
            "scanned_long_range_systems": sorted(self.scanned_long_range_systems),
            "scanned_short_range_systems": sorted(self.scanned_short_range_systems),
            "visited_systems": sorted(self.visited_systems),
            "visited_locations_by_system": {
                str(system_id): sorted(location_ids)
                for system_id, location_ids in self.visited_locations_by_system.items()
            },
            "selected_jump_system_id": self.selected_jump_system_id,
            "selected_local_id": self.selected_local_id,
            "travel_event_index": self.travel_event_index,
        }

    def apply_state(self, data: dict) -> None:
        self.lifesupport_power = int(data.get("lifesupport_power", self.lifesupport_power))
        self.structure = int(data.get("structure", self.structure))
        self.engine_power = int(data.get("engine_power", self.engine_power))
        self.shields = int(data.get("shields", self.shields))
        self.is_docked = bool(data.get("is_docked", self.is_docked))
        self.resources = int(data.get("resources", self.resources))
        self.credits = int(data.get("credits", self.credits))
        self.fuel = int(data.get("fuel", self.fuel))
        self.cargo_capacity = int(data.get("cargo_capacity", self.cargo_capacity))
        self.cargo_manifest = {
            str(commodity_id): int(quantity)
            for commodity_id, quantity in data.get("cargo_manifest", {}).items()
            if int(quantity) > 0
        }
        self.name = data.get("name", self.name)

        total_systems = len(self.galaxy.celestial_systems)
        if total_systems <= 0:
            self.current_systemID = 1
            self.current_localID = 1
            self.selected_jump_system_id = 1
            self.selected_local_id = 1
            self.scanned_long_range_systems = set()
            self.scanned_short_range_systems = set()
            self.visited_systems = {1}
            self.visited_locations_by_system = {}
            return

        loaded_system_id = int(data.get("current_systemID", self.current_systemID))
        self.current_systemID = max(1, min(loaded_system_id, total_systems))
        members = self.galaxy.get_celestial_system(self.current_systemID).members
        member_count = len(members)

        loaded_local_id = int(data.get("current_localID", self.current_localID))
        if member_count > 0:
            self.current_localID = max(1, min(loaded_local_id, member_count))
        else:
            self.current_localID = 0

        self.ship_coordinates_galactic = self.galaxy.get_celestial_system(self.current_systemID).coordinates
        if self.current_localID > 0:
            self.ship_coordinates_local = members[self.current_localID - 1].coordinates
        else:
            self.ship_coordinates_local = self.ship_coordinates_galactic

        self.scanned_long_range_systems = {
            system_id
            for system_id in self._int_set(data.get("scanned_long_range_systems", []))
            if 1 <= system_id <= total_systems
        }
        self.scanned_short_range_systems = {
            system_id
            for system_id in self._int_set(data.get("scanned_short_range_systems", []))
            if 1 <= system_id <= total_systems
        }
        self.visited_systems = {
            system_id
            for system_id in self._int_set(data.get("visited_systems", []))
            if 1 <= system_id <= total_systems
        }
        self.visited_systems.add(self.current_systemID)

        visited_locations = {}
        for raw_system_id, raw_location_ids in data.get("visited_locations_by_system", {}).items():
            system_id = int(raw_system_id)
            if not (1 <= system_id <= total_systems):
                continue
            max_local = len(self.galaxy.get_celestial_system(system_id).members)
            visited_locations[system_id] = {
                location_id
                for location_id in self._int_set(raw_location_ids)
                if 1 <= location_id <= max_local
            }
        if self.current_systemID not in visited_locations:
            visited_locations[self.current_systemID] = set()
        if self.current_localID > 0:
            visited_locations[self.current_systemID].add(self.current_localID)
        self.visited_locations_by_system = visited_locations

        loaded_selected_jump = int(data.get("selected_jump_system_id", self.current_systemID))
        if 1 <= loaded_selected_jump <= total_systems:
            self.selected_jump_system_id = loaded_selected_jump
        else:
            self.selected_jump_system_id = self.current_systemID

        loaded_selected_local = int(data.get("selected_local_id", self.current_localID))
        if member_count <= 0:
            self.selected_local_id = 0
        elif 1 <= loaded_selected_local <= member_count:
            self.selected_local_id = loaded_selected_local
        else:
            self.selected_local_id = self.current_localID
        self.travel_event_index = max(0, int(data.get("travel_event_index", 0)))

    def _int_set(self, values) -> set[int]:
        converted = set()
        for value in values:
            try:
                converted.add(int(value))
            except (TypeError, ValueError):
                continue
        return converted

    def next_travel_event_index(self) -> int:
        self.travel_event_index += 1
        return self.travel_event_index
