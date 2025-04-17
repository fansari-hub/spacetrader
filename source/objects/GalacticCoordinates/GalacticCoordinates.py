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

    