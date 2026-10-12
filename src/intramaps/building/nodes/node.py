'''A graph node with a location and type.'''

from abc import ABC, abstractmethod
from intramaps.building.geometry.coordinates import Coordinates
from intramaps.enums.enum_building import EnumNode
from intramaps.enums.enum_user import EnumGender, EnumRole, EnumAccessibility

class Node(ABC):
    '''A graph node with a location and type.
    
    Attributes:
        id: Unique identifier for the node.
        type: Type of the node, defined by EnumNode.
        coordinates: A Coordinates object representing the node in 2D space and its floor id.

    Todo:
        tests: Node(), PhysicalNode() and PseudoNode() cannot be instantiated directly.
    '''

    def __init__(self, node_id: int, node_type: EnumNode, coordinates: Coordinates):
        if not isinstance(node_id, int):
            raise ValueError("id must be an integer")
        if not isinstance(node_type, EnumNode):
            raise ValueError("type must be an instance of EnumNode")
        if not isinstance(coordinates, Coordinates):
            raise ValueError("coordinates must be an instance of Coordinates")
        self.__id = node_id
        self.__type = node_type
        self.__coordinates = coordinates

    @property
    def id(self) -> int:
        '''Returns the unique identifier for the node.'''
        return self.__id

    @property
    def type(self) -> EnumNode:
        '''Returns the type of the node.'''
        return self.__type

    @property
    def coordinates(self) -> Coordinates:
        '''Returns the coordinates of the node.'''
        return self.__coordinates

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
