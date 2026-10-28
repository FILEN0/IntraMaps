'''Connection class definition.'''
from abc import ABC, abstractmethod
from intramaps.building.geometry.coordinates import Coordinates
from intramaps.building.geometry.geometry import Geometry
from intramaps.building.nodes.pseudo_node import PseudoNode
from intramaps.enums.enum_building import EnumConnection, EnumStatus
from intramaps.enums.enum_user import EnumAccessibility

class Connection(ABC):
    '''A link between two pseudo nodes.

    Attributes:
        id: Unique identifier for the connection.
        type: Type of the connection, defined by EnumConnection.
        node_a: One end of the connection, the one with the smaller id.
        node_b: The other end of the connection.
        geometry: The line of the connection, from node_a through the waypoints to node_b.
        waypoints: The bends of the line between the two ends, in order from node_a to node_b.
        status: Whether the connection can be used, defined by EnumStatus.
        accessible: Whether people with accessibility needs, like a wheelchair, can use it.
    '''

    def __init__(self, connection_id: int, connection_type: EnumConnection, # pylint: disable=too-many-arguments,too-many-positional-arguments
                 node_a: PseudoNode, node_b: PseudoNode,
                 waypoints: tuple[Coordinates, ...] = (), status: EnumStatus = EnumStatus.OK,
                 accessible: bool = True):
        if not isinstance(connection_id, int):
            raise ValueError("id must be an integer")
        if not isinstance(connection_type, EnumConnection):
            raise ValueError("type must be an instance of EnumConnection")
        if not isinstance(node_a, PseudoNode) or not isinstance(node_b, PseudoNode):
            raise ValueError("the ends of a connection must be PseudoNodes")
        if node_a.id >= node_b.id:
            raise ValueError("node_a id must be smaller than node_b id")
        if not isinstance(status, EnumStatus):
            raise ValueError("status must be an instance of EnumStatus")
        if not isinstance(accessible, bool):
            raise ValueError("accessible must be a boolean")
        self.__id = connection_id
        self.__type = connection_type
        self.__node_a = node_a
        self.__node_b = node_b
        self.__status = status
        self.__accessible = accessible
        self.__geometry = Geometry((node_a.coordinates, *waypoints, node_b.coordinates))

    @property
    def id(self) -> int:
        '''Returns the unique identifier for the connection.'''
        return self.__id

    @property
    def type(self) -> EnumConnection:
        '''Returns the type of the connection.'''
        return self.__type

    @property
    def node_a(self) -> PseudoNode:
        '''Returns the end with the smaller id.'''
        return self.__node_a

    @property
    def node_b(self) -> PseudoNode:
        '''Returns the end with the larger id.'''
        return self.__node_b

    @property
    def geometry(self) -> Geometry:
        '''Returns the line of the connection.'''
        return self.__geometry

    @property
    def waypoints(self) -> tuple[Coordinates, ...]:
        '''Returns the bends of the line between the two ends, in order from node_a to node_b.'''
        return self.__geometry.points[1:-1]

    @property
    def status(self) -> EnumStatus:
        '''Returns the status of the connection.'''
        return self.__status

    @property
    def accessible(self) -> bool:
        '''Returns whether people with accessibility needs can use the connection.'''
        return self.__accessible

    def is_usable_by(self, accessibility: EnumAccessibility) -> bool:
        '''Determines if a person with this accessibility need can use the connection.

        Args:
            accessibility: The accessibility needs of the user.
        '''
        return accessibility == EnumAccessibility.NONE or self.accessible

    def distance(self, speed: float) -> float:
        '''Returns the distance of the connection, measured in time (seconds).

        Args:
            speed: Walking speed of the user, in meters per second.
        '''
        if isinstance(speed, bool) or not isinstance(speed, (int, float)):
            raise ValueError("speed must be a number")
        if speed <= 0:
            raise ValueError("speed must be positive")
        return self._distance(speed)

    @abstractmethod
    def _distance(self, speed: float) -> float:
        '''Returns the distance in seconds for a valid speed. Each connection type implements it.'''
