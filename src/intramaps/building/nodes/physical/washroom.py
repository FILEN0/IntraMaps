'''Washroom class definition.'''
from intramaps.building.geometry.coordinates import Coordinates
from intramaps.building.nodes.node import Node
from intramaps.enums.enum_building import EnumNode, EnumStatus
from intramaps.enums.enum_user import EnumGender, EnumRole
from intramaps.users.user import User

class Washroom(Node):
    '''A washroom of the building, that can be only for one gender.

    Attributes:
        id: Unique identifier for the washroom.
        name: Name of the washroom.
        gender_restriction: The only gender that can use the washroom, or NONE when it is for
            everyone.
        coordinates: Coordinates of the washroom.
        type: Type of the node, defined by EnumNode.
        status: Whether the washroom can be used, defined by EnumStatus.
        role_restriction: The lowest role that can go to the washroom, defined by EnumRole.
    '''

    def __init__(self, node_id: int, coordinates: Coordinates, node_name: str, # pylint: disable=too-many-arguments,too-many-positional-arguments
                 gender_restriction: EnumGender = EnumGender.NONE,
                 status: EnumStatus = EnumStatus.OK,
                 role_restriction: EnumRole = EnumRole.STUDENT):
        if not isinstance(node_name, str) or not node_name.strip():
            raise ValueError("name must be a non-empty string")
        if not isinstance(gender_restriction, EnumGender):
            raise ValueError("gender_restriction must be an instance of EnumGender")
        super().__init__(node_id, EnumNode.WASHROOM, coordinates, status, role_restriction)
        self.__name = node_name
        self.__gender_restriction = gender_restriction

    @property
    def name(self) -> str:
        '''Returns the name of the washroom.'''
        return self.__name

    @property
    def gender_restriction(self) -> EnumGender:
        '''Returns the only gender that can use the washroom, or NONE when it is for everyone.'''
        return self.__gender_restriction

    def is_valid_destination(self, user: User) -> bool:
        '''
        Determines if the washroom is a valid destination for a user.

        On top of the rules of every node, the gender of the user must be the one of the washroom.

        Args:
            user: The user who wants to go to the washroom.
        '''
        return (super().is_valid_destination(user)
                and self.gender_restriction in (EnumGender.NONE, user.gender))
