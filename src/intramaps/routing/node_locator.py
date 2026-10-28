'''NodeLocator class definition.'''
from intramaps.building.connections.connection import Connection
from intramaps.building.nodes.node import Node

class NodeLocator:
    '''Finds where the nodes are on the connections of the building.

    Args:
        connections: The connections of the building.
    '''

    def __init__(self, connections: list[Connection]) -> None:
        self.__dict_nodes_connection = {}
        self.__dict_places_corridor = {}
        self.__dict_places_position = {}
        for connection in connections:
            self.__dict_nodes_connection[(connection.node_a.id, connection.node_b.id)] = connection
            for child, position in getattr(connection, "children", ()):
                self.__dict_places_corridor[child.id] = connection
                self.__dict_places_position[child.id] = position

    def corridor_of(self, place: Node) -> Connection:
        '''Finds the corridor that a place is on.

        Args:
            place: A node that is not an end of a corridor, like a room.
        '''
        if place.id not in self.__dict_places_corridor:
            raise LookupError(f"node {place.id} is not a place on a corridor")
        return self.__dict_places_corridor[place.id]

    def connection_between(self, start: Node, end: Node) -> Connection:
        '''Finds the connection that links two nodes: the one a place is on, or the one they end.

        Args:
            start: One of the nodes.
            end: The other node.
        '''
        for node in (start, end):
            if node.id in self.__dict_places_corridor:
                return self.__dict_places_corridor[node.id]
        ends = (min(start.id, end.id), max(start.id, end.id))
        if ends not in self.__dict_nodes_connection:
            raise ValueError(f"nodes {start.id} and {end.id} are not linked")
        return self.__dict_nodes_connection[ends]

    def position_along(self, connection: Connection, node: Node) -> float:
        '''Returns where a node is along a connection: 0 at node_a, 1 at node_b, or its position.

        Args:
            connection: The connection the node is on.
            node: The node to place.
        '''
        if node.id in self.__dict_places_corridor:
            if self.__dict_places_corridor[node.id].id == connection.id:
                return self.__dict_places_position[node.id]
        if node.id == connection.node_a.id:
            return 0.0
        if node.id == connection.node_b.id:
            return 1.0
        raise ValueError(f"node {node.id} is not on connection {connection.id}")
