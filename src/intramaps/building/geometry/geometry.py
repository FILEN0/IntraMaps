'''Geometry class definition.'''
from intramaps.building.geometry.coordinates import Coordinates

class Geometry:
    '''The line of a connection, made of points in travel order.

    Attributes:
        points: The points of the line, at least two, from the first end to the last end.
        length: Length of the line in meters.
    '''

    def __init__(self, points: tuple[Coordinates, ...]):
        points = tuple(points)
        if len(points) < 2:
            raise ValueError("a geometry needs at least two points")
        if not all(isinstance(point, Coordinates) for point in points):
            raise ValueError("points must be Coordinates objects")
        self.__points = points

    @property
    def points(self) -> tuple[Coordinates, ...]:
        '''Returns the points of the line in travel order.'''
        return self.__points

    @property
    def length(self) -> float:
        '''Returns the length of the line in meters.'''
        return sum(start.distance_to(end) for start, end in zip(self.__points, self.__points[1:]))
