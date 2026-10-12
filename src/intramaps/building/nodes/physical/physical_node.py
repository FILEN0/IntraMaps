'''A physical node in a building. 
Places the user searches for. 
Can be a room, washroom, cafeteria, study space, photo spot, building exit, or drinking fountain.'''
from abc import ABC, abstractmethod
from intramaps.building.nodes.node import Node
from intramaps.building.geometry.coordinates import Coordinates
from intramaps.enums.enum_building import EnumNode
from intramaps.enums.enum_user import EnumAccessibility, EnumGender, EnumRole

class PhysicalNode(Node,ABC):
    '''
    A physical node in a building. 
    Places the user searches for. 
    e.g.: a room, washroom, cafeteria, study space, photo spot, building exit, or drinking fountain.
        
    Attributes:
        id: Unique identifier for the node.
        name: Name of the node.
        coordinates: Coordinates of the node.
        type: Type of the node, defined by EnumNode.
    '''

    def __init__(self, node_id: int, node_type: EnumNode, coordinates: Coordinates, node_name: str):
        super().__init__(node_id, node_type, coordinates)
        if not isinstance(node_name, str):
            raise ValueError("name must be a string")
        self.__name = node_name

    @property
    def name(self) -> str:
        '''Returns the name of the node.'''
        return self.__name

    @abstractmethod
    def is_valid_destination(self, gender: EnumGender, accessibility: EnumAccessibility
                             , role: EnumRole) -> bool:
        '''
        Determines if the node is a valid destination for a given user profile.

        Args:
            gender: The gender of the user.
            accessibility: The accessibility needs of the user.
            role: The role of the user.
        '''
