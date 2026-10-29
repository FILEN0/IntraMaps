'''Node class definition.'''

from abc import ABC
from intramaps.building.geometry.coordinates import Coordinates
from intramaps.enums.enum_building import EnumNode, EnumStatus
from intramaps.enums.enum_user import EnumRole
from intramaps.users.user import User

class Node(ABC):
    '''A graph node with a location and type.

    Attributes:
        id: Unique identifier for the node.
        type: Type of the node, defined by EnumNode.
        coordinates: A Coordinates object representing the node in 2D space and its floor id.
        status: Whether the node can be used, defined by EnumStatus.
        role_restriction: The lowest role that can use the node, defined by EnumRole. STUDENT
            means that everyone can.
    '''

    def __init__(self, node_id: int, node_type: EnumNode, coordinates: Coordinates, # pylint: disable=too-many-arguments,too-many-positional-arguments
                 status: EnumStatus = EnumStatus.OK,
                 role_restriction: EnumRole = EnumRole.STUDENT):
        if not isinstance(node_id, int):
            raise ValueError("id must be an integer")
        if not isinstance(node_type, EnumNode):
            raise ValueError("type must be an instance of EnumNode")
        if not isinstance(coordinates, Coordinates):
            raise ValueError("coordinates must be an instance of Coordinates")
        if not isinstance(status, EnumStatus):
            raise ValueError("status must be an instance of EnumStatus")
        if not isinstance(role_restriction, EnumRole):
            raise ValueError("role_restriction must be an instance of EnumRole")
        self.__id = node_id
        self.__type = node_type
        self.__coordinates = coordinates
        self.__status = status
        self.__role_restriction = role_restriction

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

    @property
    def status(self) -> EnumStatus:
        '''Returns the status of the node.'''
        return self.__status

    @property
    def role_restriction(self) -> EnumRole:
        '''Returns the lowest role that can use the node.'''
        return self.__role_restriction

    def is_valid_destination(self, user: User) -> bool:
        '''
        Determines if the node is a valid destination for a user.

        The role of the user must reach the role restriction of the node. Only staff can go to
        a node that is in maintenance or closed.

        Args:
            user: The user who wants to go to the node.
        '''
        if user.role.value < self.role_restriction.value:
            return False
        return self.status == EnumStatus.OK or user.role == EnumRole.STAFF

    def __eq__(self, other: object) -> bool:
        '''Two nodes are equal when they have the same id.'''
        if not isinstance(other, Node):
            raise ValueError("other must be a Node object")
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __repr__(self) -> str:
        return f"{type(self).__name__}(id={self.id}, type={self.type.name})"
