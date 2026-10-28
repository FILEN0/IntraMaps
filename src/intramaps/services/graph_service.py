'''GraphService class definition.'''
import networkx as nx
from intramaps.building.geometry.coordinates import Coordinates
from intramaps.building.geometry.geometry import Geometry
from intramaps.building.nodes.node import Node
from intramaps.building.nodes.pseudo_node import PseudoNode
from intramaps.routing.node_locator import NodeLocator
from intramaps.routing.route_step import RouteStep
from intramaps.routing.travel_cost import TravelCost
from intramaps.services.connection_service import ConnectionService
from intramaps.users.user import User

class GraphService:
    '''Builds the graph of the building and finds the fastest way through it.

    Args:
        connection_service: The service that loads the connections of the building.
    '''

    def __init__(self, connection_service: ConnectionService) -> None:
        self.__connection_service = connection_service

    def find_path(self, origin: Node, destination: Node, user: User) -> list[Node]: # pylint: disable=too-many-locals,too-many-branches,too-many-statements
        '''Finds the fastest way between two nodes, with an A* search.

        The search leaves out the connections and the ends that the user cannot use.

        Args:
            origin: The node where the way begins.
            destination: The node where the way ends.
            user: The user the way is made for.

        Returns:
            The nodes in travel order, from the origin to the destination.
        '''
        connections = self.__connection_service.get_connections()
        locator = NodeLocator(connections)
        graph = nx.Graph()
        travel_cost = TravelCost(user.speed)

        # the ends of the connections that the user can walk, linked by those connections
        for connection in connections:
            if not connection.is_usable_by(user):
                continue
            graph.add_edge(connection.node_a, connection.node_b, connection=connection,
                           weight=travel_cost.connection_seconds(connection, 0.0, 1.0))

        # the origin and the destination, when places, are linked to the ends of their corridor
        places = []
        for node in (origin, destination):
            if node not in graph:
                places.append(node)

        dict_places_position = {}
        dict_places_walk = {}
        for place in places:
            corridor = locator.corridor_of(place)
            if not graph.has_edge(corridor.node_a, corridor.node_b):
                raise LookupError(f"node {place.id} is on a corridor that cannot be walked")

            position = locator.position_along(corridor, place)
            dict_places_position[place] = position
            dict_places_walk[place] = travel_cost.walk_seconds(
                place.coordinates, corridor.geometry.point_at(position))

            for end in (corridor.node_a, corridor.node_b):
                along = travel_cost.connection_seconds(
                    corridor, position, locator.position_along(corridor, end))
                graph.add_edge(place, end, connection=corridor,
                               weight=along + dict_places_walk[place])

        # two places on the same corridor are also linked to each other
        same_corridor = (len(places) == 2
                         and locator.corridor_of(origin) == locator.corridor_of(destination))
        if same_corridor:
            corridor = locator.corridor_of(origin)
            along = travel_cost.connection_seconds(
                corridor, dict_places_position[origin], dict_places_position[destination])
            walks = dict_places_walk[origin] + dict_places_walk[destination]
            graph.add_edge(origin, destination, connection=corridor, weight=along + walks)

        # the fastest way between the origin and the destination
        try:
            return nx.astar_path(graph, origin, destination,
                                 heuristic=travel_cost.heuristic, weight="weight")
        except nx.NetworkXNoPath as error:
            raise LookupError(f"there is no way from {origin.id} to {destination.id}") from error

    def find_nearest_path(self, origin: Node, candidates: list[Node], user: User) -> list[Node]:
        '''Finds the fastest way to the nearest of some places, with a Dijkstra search.

        Args:
            origin: The node where the way begins.
            candidates: The places that can be the destination.
            user: The user the way is made for.

        Returns:
            The nodes in travel order, from the origin to the nearest candidate.
        '''
        raise NotImplementedError

    def make_steps(self, path: list[Node], speed: float) -> list[RouteStep]:
        '''Turns the nodes of a way into the steps walked between each pair of them.

        Args:
            path: The nodes in travel order, as returned by find_path or find_nearest_path.
            speed: Walking speed of the user, in meters per second.

        Returns:
            The steps in travel order, one for each pair of consecutive nodes.
        '''
        locator = NodeLocator(self.__connection_service.get_connections())
        travel_cost = TravelCost(speed)
        return [self.__make_step(locator, travel_cost, start, end)
                for start, end in zip(path, path[1:])]

    def __make_step(self, locator: NodeLocator, travel_cost: TravelCost, start: Node,
                    end: Node) -> RouteStep:
        '''Builds the stretch between two nodes, with the walk from or to a room included.'''
        connection = locator.connection_between(start, end)
        begin = locator.position_along(connection, start)
        finish = locator.position_along(connection, end)
        seconds = travel_cost.connection_seconds(connection, begin, finish)
        if start.coordinates.floor_id != end.coordinates.floor_id:
            points = [start.coordinates, end.coordinates]
        else:
            points = list(connection.geometry.points_between(begin, finish))
            if not isinstance(start, PseudoNode):
                seconds += travel_cost.walk_seconds(start.coordinates, points[0])
                points.insert(0, start.coordinates)
            if not isinstance(end, PseudoNode):
                seconds += travel_cost.walk_seconds(end.coordinates, points[-1])
                points.append(end.coordinates)
            points = self.__remove_repeated_points(points)
        return RouteStep(connection, start, end, Geometry(points), seconds)

    def __remove_repeated_points(self, points: list[Coordinates]) -> list[Coordinates]:
        '''Drops the points that repeat the one before, keeping at least two points.'''
        kept = [points[0]]
        for point in points[1:]:
            if point.distance_to(kept[-1]) > 0:
                kept.append(point)
        return kept if len(kept) > 1 else [kept[0], kept[0]]
