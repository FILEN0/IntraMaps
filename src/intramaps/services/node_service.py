'''NodeService class definition.'''
from intramaps.building.nodes.node import Node
from intramaps.building.nodes.pseudo_node import PseudoNode
from intramaps.database.node_repository import NodeRepository
from intramaps.enums.enum_building import EnumNode

class NodeService:
    '''Loads and searches the nodes of the building.

    Args:
        nodes: The repository of nodes.
    '''

    def __init__(self, nodes: NodeRepository) -> None:
        self.__nodes = nodes

    def get_nodes(self) -> dict[int, Node]:
        '''Loads every node.

        Returns:
            The nodes by id.
        '''
        return {node.id: node for node in self.__nodes.list_all()}

    def find_places(self, text: str | None = None, node_type: EnumNode | None = None,
                    floor_id: int | None = None) -> list[Node]:
        '''Finds the places a user can search for, which are the nodes that are not PseudoNodes.

        Args:
            text: If given, only the places whose name or number contains it, ignoring case.
            node_type: If given, only the places of this type.
            floor_id: If given, only the places of this floor.

        Returns:
            The places ordered by id.
        '''
        places = [node for node in self.__nodes.list_all(floor_id, node_type)
                  if not isinstance(node, PseudoNode)]
        if text is None:
            return places
        text = text.lower()
        return [place for place in places
                if text in (getattr(place, "name", None) or "").lower()
                or text in (getattr(place, "number", None) or "").lower()]
