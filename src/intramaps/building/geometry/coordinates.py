'''A point in a floor.'''
import math

class Coordinates:
    '''A point in a floor.

    Attributes:
        x: X coordinate in meters.
        y: Y coordinate in meters.
        floor_id: Floor identifier.
    '''
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
        '''Calculates the Euclidean distance to another Coordinates object.

        Args:
            other: Another Coordinates object.

        Returns:
            The Euclidean distance in meters.
        '''
        if not isinstance(other, Coordinates):
            raise ValueError("other must be a Coordinates object")
        if not self.floor_id == other.floor_id:
            raise ValueError("Cannot calculate distance between points on different floors")
        return math.dist((self.__x, self.__y), (other.x, other.y))

    def __sub__(self, other: 'Coordinates') -> tuple[float, float]:
        '''Calculates the vector that goes from another point to this one, as self - other.

        Args:
            other: The point the vector starts from.

        Returns:
            The (x, y) difference in meters, which is this point minus the other.
        '''
        if not isinstance(other, Coordinates):
            return NotImplemented
        if not self.floor_id == other.floor_id:
            raise ValueError("Cannot subtract points on different floors")
        return (self.__x - other.x, self.__y - other.y)

    def turn_angle(self, previous: 'Coordinates', following: 'Coordinates') -> float:
        '''Calculates the turn made at this point when walking from one point to another through it.

        It only compares the two stretches, so it does not depend on how the map is oriented.
        The sign assumes the axes of the floor plan, where y grows downwards.

        Args:
            previous: The point the walk comes from, before this one.
            following: The point the walk goes to, after this one.

        Returns:
            The angle in degrees from -180 up to 180. Positive is a turn to the right,
            negative is a turn to the left, 0 is going straight on and 180 is going back.
        '''
        if not isinstance(previous, Coordinates) or not isinstance(following, Coordinates):
            raise ValueError("previous and following must be Coordinates objects")
        arriving = self - previous
        leaving = following - self
        if arriving == (0, 0) or leaving == (0, 0):
            raise ValueError("previous and following must be different from this point")
        cross = arriving[0] * leaving[1] - arriving[1] * leaving[0]
        dot = arriving[0] * leaving[0] + arriving[1] * leaving[1]
        return math.degrees(math.atan2(cross, dot))

    def __eq__(self, other: object) -> bool:
        '''Two points are equal when they have the same x, y and floor.'''
        if not isinstance(other, Coordinates):
            return NotImplemented
        return (self.__x, self.__y, self.__floor_id) == (other.x, other.y, other.floor_id)

    def __hash__(self) -> int:
        return hash((self.__x, self.__y, self.__floor_id))

    def __repr__(self):
        return f"Coordinates(x={self.__x}m, y={self.__y}m, floor_id={self.__floor_id})"

    def __str__(self):
        return f"({self.__x}m, {self.__y}m, {self.__floor_id}))"
