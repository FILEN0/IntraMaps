'''Geometry class definition.'''
from bisect import bisect_left, bisect_right
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
        self.__walked = None

    @property
    def points(self) -> tuple[Coordinates, ...]:
        '''Returns the points of the line in travel order.'''
        return self.__points

    @property
    def length(self) -> float:
        '''Returns the length of the line in meters.'''
        return self.__distances()[-1]

    def point_at(self, position: float) -> Coordinates:
        '''Finds the point at a position along the line.

        Args:
            position: The position from 0 (first point) to 1 (last point), measured along the line.

        Returns:
            The point at that position.
        '''
        self.__check_position(position)
        if position == 0:
            return self.__points[0]
        if position == 1:
            return self.__points[-1]
        walked = self.__distances()
        target = position * walked[-1]
        index = bisect_left(walked, target)
        start, end = self.__points[index - 1], self.__points[index]
        ratio = (target - walked[index - 1]) / (walked[index] - walked[index - 1])
        return Coordinates(start.x + ratio * (end.x - start.x),
                           start.y + ratio * (end.y - start.y), start.floor_id)

    def points_between(self, start: float, end: float) -> tuple[Coordinates, ...]:
        '''Finds the points of the part of the line between two positions, in travel order.

        Args:
            start: The position where the part begins, from 0 to 1.
            end: The position where the part ends, from 0 to 1. When it is smaller than start,
                the part is walked backwards.

        Returns:
            The first point, the corners of the line in between and the last point.
            When start equals end, the same point twice.
        '''
        self.__check_position(start)
        self.__check_position(end)
        first, last = sorted((start, end))
        walked = self.__distances()
        corners = self.__points[bisect_right(walked, first * walked[-1]):
                              bisect_left(walked, last * walked[-1])]
        part = (self.point_at(first), *corners, self.point_at(last))
        return part if start <= end else part[::-1]

    def __check_position(self, position: float) -> None:
        if isinstance(position, bool) or not isinstance(position, (int, float)):
            raise ValueError("position must be a number")
        if not 0 <= position <= 1:
            raise ValueError("position must be between 0 and 1")

    def __distances(self) -> tuple[float, ...]:
        '''Returns the distance walked from the first point up to each point, calculated once.'''
        if self.__walked is None:
            walked = [0.0]
            for start, end in zip(self.__points, self.__points[1:]):
                walked.append(walked[-1] + start.distance_to(end))
            self.__walked = tuple(walked)
        return self.__walked
