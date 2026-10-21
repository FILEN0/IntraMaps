'''Corridor class definition.'''
from intramaps.building.connections.connection import Connection
from intramaps.building.geometry.coordinates import Coordinates
from intramaps.building.nodes.node import Node
from intramaps.building.nodes.pseudo_node import PseudoNode
from intramaps.enums.enum_building import EnumConnection, EnumStatus

class Corridor(Connection):
    '''A walkable line between two pseudo nodes, with the places along it.

    Attributes:
        waypoints: Coordinates of the bends of the line, in order from node_a to node_b.
        children: (node, position) pairs ordered by position. The position goes from 0 (node_a)
            to 1 (node_b), measured along the line.
        length: Length of the line in meters.
    '''

    def __init__(self, connection_id: int, node_a: PseudoNode, node_b: PseudoNode, # pylint: disable=too-many-arguments,too-many-positional-arguments
                 waypoints: tuple[Coordinates, ...] = (),
                 children: tuple[tuple[Node, float], ...] = (),
                 status: EnumStatus = EnumStatus.OK):
        super().__init__(connection_id, EnumConnection.CORRIDOR, node_a, node_b, status)
        floor_id = node_a.coordinates.floor_id
        if node_b.coordinates.floor_id != floor_id:
            raise ValueError("a corridor cannot change floors")
        self.__check_waypoints(waypoints, floor_id)
        self.__check_children(children, floor_id)
        self.__waypoints = tuple(waypoints)
        self.__children = tuple(sorted(children, key=lambda pair: pair[1]))

    def __check_waypoints(self, waypoints, floor_id: int) -> None:
        for point in waypoints:
            if not isinstance(point, Coordinates):
                raise ValueError("waypoints must be Coordinates objects")
            if point.floor_id != floor_id:
                raise ValueError("waypoints must be on the same floor as the corridor")

    def __check_children(self, children, floor_id: int) -> None:
        ids = set()
        for child, position in children:
            if not isinstance(child, Node) or isinstance(child, PseudoNode):
                raise ValueError("children must be nodes that are not PseudoNodes")
            if child.coordinates.floor_id != floor_id:
                raise ValueError("children must be on the same floor as the corridor")
            if isinstance(position, bool) or not isinstance(position, (int, float)):
                raise ValueError("position must be a number")
            if not 0 <= position <= 1:
                raise ValueError("position must be between 0 and 1")
            if child.id in ids:
                raise ValueError("a node cannot be a child twice")
            ids.add(child.id)

    @property
    def waypoints(self) -> tuple[Coordinates, ...]:
        '''Returns the bends of the line, in order from node_a to node_b.'''
        return self.__waypoints

    @property
    def children(self) -> tuple[tuple[Node, float], ...]:
        '''Returns the (node, position) pairs, ordered by position.'''
        return self.__children

    @property
    def length(self) -> float:
        '''Returns the length of the line in meters.'''
        points = (self.node_a.coordinates, *self.__waypoints, self.node_b.coordinates)
        return sum(start.distance_to(end) for start, end in zip(points, points[1:]))

    def _distance(self, speed: float) -> float:
        '''Returns the time in seconds to walk the whole line at the given speed.'''
        return self.length / speed
