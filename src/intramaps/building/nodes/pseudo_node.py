'''A pseudo node in a building.
Places where the user navigate through, but not target destinations.
Can be a corridor_end or a ramp_entrance. Nodes that change floors are FloorChangeNodes.
'''
from intramaps.building.nodes.node import Node
from intramaps.building.geometry.coordinates import Coordinates
from intramaps.enums.enum_building import EnumNode
from intramaps.enums.enum_user import EnumAccessibility, EnumGender, EnumRole

class PseudoNode(Node):
    '''
    A pseudo node in a building.
    Places where the user navigate through, but not target destinations.
    e.g.: a corridor_end or a ramp_entrance.

    Attributes:
        id: Unique identifier for the node.
        coordinates: Coordinates of the node.
        type: Type of the node, defined by EnumNode.
    '''

    TYPES = (EnumNode.CORRIDOR_END, EnumNode.RAMP_ENTRANCE)

    def __init__(self, node_id: int, node_type: EnumNode, coordinates: Coordinates):
        if node_type not in self.TYPES:
            raise ValueError(f"Cant create a {type(self).__name__} with type {node_type}. Must be one of: {list(self.TYPES)}") # pylint: disable=line-too-long
        super().__init__(node_id, node_type, coordinates)

    def is_valid_destination(self, gender: EnumGender, accessibility: EnumAccessibility,
                              role: EnumRole) -> bool:
        '''
        Determines if the node is a valid destination for a given user profile.
        Since pseudo nodes are not target destinations, this method always returns False.
        '''
        return False
