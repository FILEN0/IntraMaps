'''A pseudo node in a building. 
Places where the user navigate through, but not target destinations. 
Can be a corridor_end, elevator_door, ramp_entrance, stairs_entrance .
'''
from abc import ABC
from intramaps.building.nodes.node import Node

class PseudoNode(Node,ABC):
    '''
    A pseudo node in a building. 
    Places where the user navigate through, but not target destinations. 
    e.g.: a corridor_end, elevator_door, ramp_entrance, or stairs_entrance.

    Attributes:
        id: Unique identifier for the node.
        coordinates: Coordinates of the node.
        type: Type of the node, defined by EnumNode.
    '''

    def __init__(self, node_id: int, node_type, coordinates):
        if type(self) is PseudoNode: # pylint: disable=unidiomatic-typecheck
            raise TypeError("PseudoNode is an abstract class and cannot be instantiated directly.")
        super().__init__(node_id, node_type, coordinates)

    def is_valid_destination(self, gender, accessibility, role) -> bool:
        '''
        Determines if the node is a valid destination for a given user profile.

        Args:
            gender: The gender of the user.
            accessibility: The accessibility needs of the user.
            role: The role of the user.
        '''
        return False
