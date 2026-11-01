'''Stairs class definition.'''
from intramaps.building.connections.connection import Connection
from intramaps.building.geometry.coordinates import Coordinates
from intramaps.building.nodes.floor_change_node import FloorChangeNode
from intramaps.enums.enum_building import EnumConnection, EnumNode, EnumStatus

class Stairs(Connection):
    '''Stairs between two stairs entrances, on the same floor or on different floors.

    People with accessibility needs cannot use it.

    Attributes:
        rise_m: Height climbed along the stairs, in meters.
    '''

    def __init__(self, connection_id: int, node_a: FloorChangeNode, node_b: FloorChangeNode, # pylint: disable=too-many-arguments,too-many-positional-arguments
                 rise_m: float, waypoints: tuple[Coordinates, ...] = (),
                 status: EnumStatus = EnumStatus.OK):
        for end in (node_a, node_b):
            if not isinstance(end, FloorChangeNode) or end.type != EnumNode.STAIRS_ENTRANCE:
                raise ValueError("the ends of stairs must be stairs entrances")
        if isinstance(rise_m, bool) or not isinstance(rise_m, (int, float)) or rise_m < 0:
            raise ValueError("rise_m must be a number that is not negative")
        super().__init__(connection_id, EnumConnection.STAIRS, node_a, node_b, waypoints,
                         status, accessible=False)
        self.__rise_m = rise_m

    @property
    def rise_m(self) -> float:
        '''Returns the height climbed along the stairs, in meters.'''
        return self.__rise_m

    def _distance(self, speed: float) -> float:
        '''Returns the time in seconds to take the stairs.

        It is the walk along the line, when both ends are on the same floor, plus the climb. The
        climb goes at a fraction of the walking speed that is smaller the higher the stairs are.
        '''
        same_floor = self.node_a.coordinates.floor_id == self.node_b.coordinates.floor_id
        walk = self.geometry.length / speed if same_floor else 0.0
        if self.__rise_m <= 2.0:
            climb_ratio = 0.2
        elif self.__rise_m <= 5.0:
            climb_ratio = 0.14
        else:
            climb_ratio = 0.08
        return walk + self.__rise_m / (climb_ratio * speed)
