'''PhotoSpot class definition.'''
from intramaps.building.geometry.coordinates import Coordinates
from intramaps.building.nodes.node import Node
from intramaps.enums.enum_building import EnumNode, EnumStatus
from intramaps.enums.enum_user import EnumRole

class PhotoSpot(Node):
    '''A place of the building that is good for taking photos.

    Attributes:
        id: Unique identifier for the photo spot.
        name: Name of the photo spot.
        coordinates: Coordinates of the photo spot.
        type: Type of the node, defined by EnumNode.
        status: Whether the photo spot can be used, defined by EnumStatus.
        role_restriction: The lowest role that can go to the photo spot, defined by EnumRole.
    '''

    def __init__(self, node_id: int, coordinates: Coordinates, node_name: str, # pylint: disable=too-many-arguments,too-many-positional-arguments
                 status: EnumStatus = EnumStatus.OK,
                 role_restriction: EnumRole = EnumRole.STUDENT):
        if not isinstance(node_name, str) or not node_name.strip():
            raise ValueError("name must be a non-empty string")
        super().__init__(node_id, EnumNode.PHOTO_SPOT, coordinates, status, role_restriction)
        self.__name = node_name

    @property
    def name(self) -> str:
        '''Returns the name of the photo spot.'''
        return self.__name
