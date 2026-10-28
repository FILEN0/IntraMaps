'''BicycleParking class definition.'''
from intramaps.building.geometry.coordinates import Coordinates
from intramaps.building.nodes.node import Node
from intramaps.enums.enum_building import EnumNode, EnumStatus
from intramaps.enums.enum_user import EnumRole

class BicycleParking(Node):
    '''A place of the building to park bicycles.

    Attributes:
        id: Unique identifier for the bicycle parking.
        name: Name of the bicycle parking.
        coordinates: Coordinates of the bicycle parking.
        type: Type of the node, defined by EnumNode.
        status: Whether the bicycle parking can be used, defined by EnumStatus.
        role_restriction: The lowest role that can go to the bicycle parking, defined by EnumRole.
    '''

    def __init__(self, node_id: int, coordinates: Coordinates, node_name: str, # pylint: disable=too-many-arguments,too-many-positional-arguments
                 status: EnumStatus = EnumStatus.OK,
                 role_restriction: EnumRole = EnumRole.STUDENT):
        if not isinstance(node_name, str) or not node_name.strip():
            raise ValueError("name must be a non-empty string")
        super().__init__(node_id, EnumNode.BICYCLE_PARKING, coordinates, status, role_restriction)
        self.__name = node_name

    @property
    def name(self) -> str:
        '''Returns the name of the bicycle parking.'''
        return self.__name
