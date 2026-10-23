'''RouteStep class definition.'''
from intramaps.building.connections.connection import Connection
from intramaps.building.geometry.coordinates import Coordinates
from intramaps.building.nodes.node import Node

class RouteStep: # pylint: disable=too-many-arguments,too-many-positional-arguments
    '''One stretch of a route, walked along a single connection.

    Attributes:
        connection: The connection the stretch is walked along.
        start: The node where the stretch begins.
        end: The node where the stretch ends.
        points: The points of the stretch in travel order, at least two.
        seconds: Time to walk the stretch, in seconds.
    '''

    def __init__(self, connection: Connection, start: Node, end: Node,
                 points: tuple[Coordinates, ...], seconds: float):
        if not isinstance(connection, Connection):
            raise ValueError("connection must be an instance of Connection")
        if not isinstance(start, Node) or not isinstance(end, Node):
            raise ValueError("start and end must be nodes")
        if len(points) < 2 or not all(isinstance(point, Coordinates) for point in points):
            raise ValueError("points must be at least two Coordinates objects")
        if isinstance(seconds, bool) or not isinstance(seconds, (int, float)) or seconds < 0:
            raise ValueError("seconds must be a number that is not negative")
        self.__connection = connection
        self.__start = start
        self.__end = end
        self.__points = tuple(points)
        self.__seconds = seconds

    @property
    def connection(self) -> Connection:
        '''Returns the connection the stretch is walked along.'''
        return self.__connection

    @property
    def start(self) -> Node:
        '''Returns the node where the stretch begins.'''
        return self.__start

    @property
    def end(self) -> Node:
        '''Returns the node where the stretch ends.'''
        return self.__end

    @property
    def points(self) -> tuple[Coordinates, ...]:
        '''Returns the points of the stretch in travel order.'''
        return self.__points

    @property
    def seconds(self) -> float:
        '''Returns the time to walk the stretch, in seconds.'''
        return self.__seconds
