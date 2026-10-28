'''DrinkingFountain class definition.'''
from intramaps.building.geometry.coordinates import Coordinates
from intramaps.building.nodes.node import Node
from intramaps.enums.enum_building import EnumNode, EnumStatus
from intramaps.enums.enum_user import EnumRole

class DrinkingFountain(Node):
    '''A drinking fountain of the building.

    Attributes:
        id: Unique identifier for the drinking fountain.
        name: Name of the drinking fountain.
        coordinates: Coordinates of the drinking fountain.
        type: Type of the node, defined by EnumNode.
        status: Whether the drinking fountain can be used, defined by EnumStatus.
        role_restriction: The lowest role that can go to the drinking fountain, defined by EnumRole.
    '''

    def __init__(self, node_id: int, coordinates: Coordinates, node_name: str, # pylint: disable=too-many-arguments,too-many-positional-arguments
                 status: EnumStatus = EnumStatus.OK,
                 role_restriction: EnumRole = EnumRole.STUDENT):
        if not isinstance(node_name, str) or not node_name.strip():
            raise ValueError("name must be a non-empty string")
        super().__init__(node_id, EnumNode.DRINKING_FOUNTAIN, coordinates, status, role_restriction)
        self.__name = node_name

    @property
    def name(self) -> str:
        '''Returns the name of the drinking fountain.'''
        return self.__name
