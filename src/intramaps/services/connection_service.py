'''ConnectionService class definition.'''
from intramaps.building.connections.connection import Connection
from intramaps.database.connection_repository import ConnectionRepository
from intramaps.services.node_service import NodeService

class ConnectionService: # pylint: disable=too-few-public-methods
    '''Loads the connections of the building, linked to its nodes.

    Args:
        connection_repository: The repository of connections.
        node_service: The service that loads the nodes the connections link.
    '''

    def __init__(self, connection_repository: ConnectionRepository,
                 node_service: NodeService) -> None:
        self.__connection_repository = connection_repository
        self.__node_service = node_service

    def get_connections(self) -> list[Connection]:
        '''Loads every connection, with its ends and children taken from the nodes.

        Returns:
            The connections ordered by id.
        '''
        return self.__connection_repository.list_all(self.__node_service.get_nodes())
