'''RouteStep class definition.'''
from intramaps.building.connections.connection import Connection
from intramaps.building.geometry.coordinates import Coordinates
from intramaps.building.geometry.geometry import Geometry
from intramaps.building.nodes.node import Node

def _label(node: Node) -> str:
    '''Returns the name or number of a node, or its type and id when it has neither.'''
    return (getattr(node, "name", None) or getattr(node, "number", None)
            or f"{node.type.name.lower().replace('_', ' ')} {node.id}")

class RouteStep: # pylint: disable=too-many-arguments,too-many-positional-arguments
    '''One stretch of a route, walked along a single connection.

    Attributes:
        connection: The connection the stretch is walked along.
        start: The node where the stretch begins.
        end: The node where the stretch ends.
        geometry: The line of the stretch, in travel order.
        points: The points of the line.
        meters: Length of the stretch in meters, or None when it changes floors.
        seconds: Time to walk the stretch, in seconds.
    '''

    def __init__(self, connection: Connection, start: Node, end: Node,
                 geometry: Geometry, seconds: float):
        if not isinstance(connection, Connection):
            raise ValueError("connection must be an instance of Connection")
        if not isinstance(start, Node) or not isinstance(end, Node):
            raise ValueError("start and end must be nodes")
        if not isinstance(geometry, Geometry):
            raise ValueError("geometry must be an instance of Geometry")
        if isinstance(seconds, bool) or not isinstance(seconds, (int, float)) or seconds < 0:
            raise ValueError("seconds must be a number that is not negative")
        self.__connection = connection
        self.__start = start
        self.__end = end
        self.__geometry = geometry
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
    def geometry(self) -> Geometry:
        '''Returns the line of the stretch.'''
        return self.__geometry

    @property
    def points(self) -> tuple[Coordinates, ...]:
        '''Returns the points of the stretch in travel order.'''
        return self.__geometry.points

    @property
    def meters(self) -> float | None:
        '''Returns the length of the stretch in meters, or None when it changes floors.'''
        if len({point.floor_id for point in self.__geometry.points}) > 1:
            return None
        return self.__geometry.length

    @property
    def seconds(self) -> float:
        '''Returns the time to walk the stretch, in seconds.'''
        return self.__seconds
