import math

class Coordinates:
    """A point in a floor.

    Attributes:
        x: X coordinate in meters.
        y: Y coordinate in meters.
        floor: floor number.
    """
    def __init__(self, x: float, y: float, floor: int):
        if(not isinstance(x, (int, float))):
            raise ValueError("x must be a number")
        if(not isinstance(y, (int, float))):
            raise ValueError("y must be a number")
        if (not isinstance(floor, (int))):
            raise ValueError("floor must be an integer")
        self.__x = x
        self.__y = y
        self.__floor = floor

    @property
    def x(self) -> float:
        return self.__x
    
    @property
    def y(self) -> float:
        return self.__y
    
    @property
    def floor(self) -> int:
        return self.__floor

    @x.setter
    def x(self, value: float):
        if(not isinstance(value, (int, float))):
            raise ValueError("x must be a number")
        self.__x = value

    @y.setter
    def y(self, value: float):
        if(not isinstance(value, (int, float))):
            raise ValueError("y must be a number")
        self.__y = value

    @floor.setter
    def floor(self, value: int):
        if(not isinstance(value, (int))):
            raise ValueError("floor must be an integer")
        self.__floor = value

    def distance_to(self, other: 'Coordinates') -> float:
        """Calculates the Euclidean distance to another Coordinates object.

        Args:
            other: Another Coordinates object.

        Returns:
            The Euclidean distance in meters.
        """
        if not isinstance(other, Coordinates):
            raise ValueError("other must be a Coordinates object")
        if not(self.floor == other.floor):
            raise ValueError("Cannot calculate distance between points on different floors")
        return math.dist((self.__x, self.__y), (other.x, other.y))

    def __repr__(self):
        return f"Coordinates(x={self.__x}m, y={self.__y}m, floor={self.__floor})"
    
    def __str__(self):
        return f"({self.__x}m, {self.__y}m, {self.__floor})"
