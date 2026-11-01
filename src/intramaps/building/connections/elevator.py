'''Elevator class definition.'''
from intramaps.building.connections.connection import Connection
from intramaps.building.nodes.floor_change_node import FloorChangeNode
from intramaps.enums.enum_building import EnumConnection, EnumNode, EnumStatus

class Elevator(Connection):
    '''An elevator between two elevator doors on different floors.

    Attributes:
        rise_m: Height between the two doors, in meters.
        wait_time_s: Time spent waiting for the elevator to arrive, in seconds.
    '''

    SPEED = 1.0

    def __init__(self, connection_id: int, node_a: FloorChangeNode, node_b: FloorChangeNode, # pylint: disable=too-many-arguments,too-many-positional-arguments
                 rise_m: float, wait_time_s: float, status: EnumStatus = EnumStatus.OK):
        for end in (node_a, node_b):
            if not isinstance(end, FloorChangeNode) or end.type != EnumNode.ELEVATOR_DOOR:
                raise ValueError("the ends of an elevator must be elevator doors")
        if node_a.coordinates.floor_id == node_b.coordinates.floor_id:
            raise ValueError("an elevator must link different floors")
        for value, label in ((rise_m, "rise_m"), (wait_time_s, "wait_time_s")):
            if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
                raise ValueError(f"{label} must be a number that is not negative")
        super().__init__(connection_id, EnumConnection.ELEVATOR, node_a, node_b, (), status,
                         accessible=True)
        self.__rise_m = rise_m
        self.__wait_time_s = wait_time_s

    @property
    def rise_m(self) -> float:
        '''Returns the height between the two doors, in meters.'''
        return self.__rise_m

    @property
    def wait_time_s(self) -> float:
        '''Returns the time spent waiting for the elevator, in seconds.'''
        return self.__wait_time_s

    def _distance(self, speed: float) -> float:
        '''Returns the time in seconds to take the elevator: the wait plus the ride at SPEED.'''
        return self.__wait_time_s + self.__rise_m / self.SPEED
