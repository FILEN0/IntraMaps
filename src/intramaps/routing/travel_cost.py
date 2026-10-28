'''TravelCost class definition.'''
from intramaps.building.connections.connection import Connection
from intramaps.building.geometry.coordinates import Coordinates
from intramaps.building.nodes.node import Node

class TravelCost:
    '''The times that the search for a way and the steps of a route are made of.

    Args:
        speed: Walking speed of the user, in meters per second.
    '''

    def __init__(self, speed: float) -> None:
        self.__speed = speed

    def heuristic(self, node: Node, target: Node) -> float:
        '''Estimates the time to walk straight from a node to the target, for the A* search.

        Between nodes on different floors there is no straight line, so the estimate is zero.

        Args:
            node: The node where the walk is.
            target: The node where the walk ends.
        '''
        try:
            return self.walk_seconds(node.coordinates, target.coordinates)
        except ValueError:
            return 0.0

    def walk_seconds(self, origin: Coordinates, target: Coordinates) -> float:
        '''Returns the time to walk in a straight line between two points of the same floor.

        Args:
            origin: The point where the walk begins.
            target: The point where the walk ends.
        '''
        return origin.distance_to(target) / self.__speed

    def connection_seconds(self, connection: Connection, begin: float, finish: float) -> float:
        '''Returns the time to walk the part of a connection between two positions.

        Args:
            connection: The connection that is walked.
            begin: The position where the walk begins, from 0 to 1.
            finish: The position where the walk ends, from 0 to 1.
        '''
        return abs(begin - finish) * connection.distance(self.__speed)
