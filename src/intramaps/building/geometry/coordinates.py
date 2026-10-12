'''A point in a floor.'''
import math

class Coordinates:
    """A point in a floor.

    Attributes:
        x: X coordinate in meters.
        y: Y coordinate in meters.
        floor_id: Floor identifier.
    """
    def __init__(self, x: float, y: float, floor_id: int):
        if not isinstance(x, (int, float)):
            raise ValueError("x must be a number")
        if not isinstance(y, (int, float)):
            raise ValueError("y must be a number")
        if not isinstance(floor_id, (int)):
            raise ValueError("floor_id must be an integer")
        self.__x = x
        self.__y = y
        self.__floor_id = floor_id

    @property
    def x(self) -> float:
        '''Returns the x coordinate in meters.'''
        return self.__x

    @property
    def y(self) -> float:
        '''Returns the y coordinate in meters.'''
        return self.__y

    @property
    def floor_id(self) -> int:
        '''Returns the floor identifier.'''
        return self.__floor_id

    def distance_to(self, other: 'Coordinates') -> float:
        """Calculates the Euclidean distance to another Coordinates object.

        Args:
            other: Another Coordinates object.

        Returns:
            The Euclidean distance in meters.
        """
        if not isinstance(other, Coordinates):
            raise ValueError("other must be a Coordinates object")
        if not self.floor_id == other.floor_id:
            raise ValueError("Cannot calculate distance between points on different floors")
        return math.dist((self.__x, self.__y), (other.x, other.y))

    def __repr__(self):
        return f"Coordinates(x={self.__x}m, y={self.__y}m, floor_id={self.__floor_id})"

    def __str__(self):
        return f"({self.__x}m, {self.__y}m, {self.__floor_id}))"
