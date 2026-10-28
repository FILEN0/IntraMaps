'''A pseudo node in a building.
Places where the user navigate through, but not target destinations.
Can be a corridor_end or a ramp_entrance. Nodes that change floors are FloorChangeNodes.
'''
from intramaps.building.nodes.node import Node
from intramaps.building.geometry.coordinates import Coordinates
from intramaps.enums.enum_building import EnumNode, EnumStatus
from intramaps.enums.enum_user import EnumRole
from intramaps.users.user import User

class PseudoNode(Node):
    '''
    A pseudo node in a building.
    Places where the user navigate through, but not target destinations.
    e.g.: a corridor_end or a ramp_entrance.

    Attributes:
        id: Unique identifier for the node.
        coordinates: Coordinates of the node.
        type: Type of the node, defined by EnumNode.
        status: Whether the node can be used, defined by EnumStatus.
        role_restriction: The lowest role that can use the node, defined by EnumRole.
    '''

    TYPES = (EnumNode.CORRIDOR_END, EnumNode.RAMP_ENTRANCE)

    def __init__(self, node_id: int, node_type: EnumNode, coordinates: Coordinates, # pylint: disable=too-many-arguments,too-many-positional-arguments
                 status: EnumStatus = EnumStatus.OK,
                 role_restriction: EnumRole = EnumRole.STUDENT):
        if node_type not in self.TYPES:
            raise ValueError(f"Cant create a {type(self).__name__} with type {node_type}. Must be one of: {list(self.TYPES)}") # pylint: disable=line-too-long
        super().__init__(node_id, node_type, coordinates, status, role_restriction)

    def is_valid_destination(self, user: User) -> bool:
        '''
        Determines if the node is a valid destination for a user.
        Since pseudo nodes are not target destinations, this method always returns False.
        '''
        return False
