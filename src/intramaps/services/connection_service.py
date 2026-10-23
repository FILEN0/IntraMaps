'''ConnectionService class definition.'''
from intramaps.building.connections.corridor import Corridor
from intramaps.database.connection_repository import ConnectionRepository
from intramaps.services.node_service import NodeService

class ConnectionService: # pylint: disable=too-few-public-methods
    '''Loads the connections of the building, linked to its nodes.

    Args:
        connections: The repository of connections.
        nodes: The service that loads the nodes the connections link.
    '''

    def __init__(self, connections: ConnectionRepository, nodes: NodeService) -> None:
        self.__connections = connections
        self.__nodes = nodes

    def get_corridors(self) -> list[Corridor]:
        '''Loads every corridor, with its ends and children taken from the nodes.

        Returns:
            The corridors ordered by id.
        '''
        return self.__connections.list_all(self.__nodes.get_nodes())
