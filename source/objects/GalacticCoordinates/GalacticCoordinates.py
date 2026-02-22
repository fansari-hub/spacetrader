import math

class GalacticCoordinates():
    def __init__(self, intX, intY, type="galactic"):
        self.x = intX
        self.y = intY
        self.type = type

    def get_coord(self) -> tuple:
        return (self.x, self.y)
    
    def get_distance(self, other) -> float:
        return math.dist(self.get_coord(), other.get_coord())

    def to_dict(self) -> dict:
        return {
            "x": self.x,
            "y": self.y,
            "type": self.type,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            int(data.get("x", 0)),
            int(data.get("y", 0)),
            type=data.get("type", "galactic"),
        )

    
