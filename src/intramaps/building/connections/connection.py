'''Connection class definition.'''
from abc import ABC, abstractmethod
from intramaps.building.nodes.pseudo_node import PseudoNode
from intramaps.enums.enum_building import EnumConnection, EnumStatus

class Connection(ABC):
    '''A link between two pseudo nodes.

    Attributes:
        id: Unique identifier for the connection.
        type: Type of the connection, defined by EnumConnection.
        node_a: One end of the connection, the one with the smaller id.
        node_b: The other end of the connection.
        status: Whether the connection can be used, defined by EnumStatus.
    '''

    def __init__(self, connection_id: int, connection_type: EnumConnection,
                 node_a: PseudoNode, node_b: PseudoNode, status: EnumStatus = EnumStatus.OK):
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
        self.__id = connection_id
        self.__type = connection_type
        self.__node_a = node_a
        self.__node_b = node_b
        self.__status = status

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
    def status(self) -> EnumStatus:
        '''Returns the status of the connection.'''
        return self.__status

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
