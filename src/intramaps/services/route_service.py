'''RouteService class definition.'''
from intramaps.building.nodes.node import Node
from intramaps.enums.enum_building import EnumNode
from intramaps.routing.route import Route
from intramaps.services.graph_service import GraphService
from intramaps.services.node_service import NodeService
from intramaps.users.user import User

class RouteService:
    '''Finds the way between two places of the building, or to the nearest place of a type.

    Each way is made for a user, and is returned as the nodes it goes through or as a Route.

    Args:
        node_service: The service that loads the nodes of the building.
        graph_service: The service that finds the fastest way through the building.
    '''

    def __init__(self, node_service: NodeService, graph_service: GraphService) -> None:
        self.__node_service = node_service
        self.__graph_service = graph_service

    def find_nodes(self, origin_id: int, destination_id: int, user: User) -> list[Node]:
        '''Finds the fastest way between two nodes, as the nodes it goes through.

        Args:
            origin_id: Id of the node where the way begins.
            destination_id: Id of the node where the way ends.
            user: The user the way is made for.

        Returns:
            The nodes in travel order, from the origin to the destination, with the corridor ends
            in between.
        '''
        return self.__get_route(origin_id, destination_id, user)

    def find_nearest_nodes(self, origin_id: int, node_type: EnumNode, user: User) -> list[Node]:
        '''Finds the fastest way to the nearest place of a type, as the nodes it goes through.

        Args:
            origin_id: Id of the node where the way begins.
            node_type: The type of the place the user is looking for.
            user: The user the way is made for.

        Returns:
            The nodes in travel order, from the origin to the nearest valid place.
        '''
        return self.__get_nearest_route(origin_id, node_type, user)

    def find_route(self, origin_id: int, destination_id: int, user: User) -> Route:
        '''Finds the fastest way between two nodes, as steps with directions.

        Args:
            origin_id: Id of the node where the way begins.
            destination_id: Id of the node where the way ends.
            user: The user the way is made for.

        Returns:
            The route, as consecutive steps.
        '''
        path = self.find_nodes(origin_id, destination_id, user)
        return Route(tuple(self.__graph_service.make_steps(path, user.travel_speed)))

    def find_nearest_route(self, origin_id: int, node_type: EnumNode, user: User) -> Route:
        '''Finds the fastest way to the nearest place of a type, as steps with directions.

        Args:
            origin_id: Id of the node where the way begins.
            node_type: The type of the place the user is looking for.
            user: The user the way is made for.

        Returns:
            The route, as consecutive steps, ending at the nearest valid place.
        '''
        path = self.find_nearest_nodes(origin_id, node_type, user)
        return Route(tuple(self.__graph_service.make_steps(path, user.travel_speed)))

    def __get_route(self, origin_id: int, destination_id: int, user: User) -> list[Node]:
        '''Checks the request and finds the nodes of the fastest way, with an A* search.'''
        if origin_id == destination_id:
            raise ValueError("origin and destination must be different")
        nodes_by_id = self.__node_service.get_nodes()
        origin = self.__find(nodes_by_id, origin_id)
        destination = self.__find(nodes_by_id, destination_id)
        if not destination.is_valid_destination(user):
            raise PermissionError(f"node {destination_id} is not a valid destination for this user")
        return self.__graph_service.find_path(origin, destination, user)

    def __get_nearest_route(self, origin_id: int, node_type: EnumNode, user: User) -> list[Node]:
        '''Checks the request and finds the nodes of the way to the nearest valid place.'''
        origin = self.__find(self.__node_service.get_nodes(), origin_id)
        places = [place for place in self.__node_service.find_places(node_type=node_type)
                  if place.is_valid_destination(user)]
        return self.__graph_service.find_nearest_path(origin, places, user)

    def __find(self, nodes_by_id: dict[int, Node], node_id: int) -> Node:
        if node_id not in nodes_by_id:
            raise LookupError(f"node {node_id} does not exist")
        return nodes_by_id[node_id]
