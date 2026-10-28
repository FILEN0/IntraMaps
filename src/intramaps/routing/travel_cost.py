'''TravelCost class definition.'''
import networkx as nx
from intramaps.building.connections.connection import Connection
from intramaps.building.geometry.coordinates import Coordinates

class TravelCost:
    '''The times that the search for a way and the steps of a route are made of.

    Args:
        speed: Walking speed of the user, in meters per second.
        graph: The graph of the search, with the node of each id in the "node" attribute. Only
            the heuristic needs it.
    '''

    def __init__(self, speed: float, graph: nx.Graph | None = None) -> None:
        self.__speed = speed
        self.__graph = graph

    def heuristic(self, node_id: int, target_id: int) -> float:
        '''Estimates the time to walk straight from a node to the target, for the A* search.

        Between nodes on different floors there is no straight line, so the estimate is zero.

        Args:
            node_id: Id of the node where the walk is.
            target_id: Id of the node where the walk ends.
        '''
        here = self.__graph.nodes[node_id]["node"].coordinates
        target = self.__graph.nodes[target_id]["node"].coordinates
        try:
            return self.walk_seconds(here, target)
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
