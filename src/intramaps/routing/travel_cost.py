'''TravelCost class definition.'''
import networkx as nx

class TravelCost: # pylint: disable=too-few-public-methods
    '''The time estimate and the time weight that a search through the graph of the building uses.

    Args:
        graph: The graph of the search, with the node of each id in the "node" attribute.
        speed: Walking speed of the user, in meters per second.
    '''

    def __init__(self, graph: nx.Graph, speed: float) -> None:
        self.__graph = graph
        self.__speed = speed

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
            return here.distance_to(target) / self.__speed
        except ValueError:
            return 0.0
