'''BuildingExit class definition.'''
from intramaps.building.geometry.coordinates import Coordinates
from intramaps.building.nodes.node import Node
from intramaps.building.opening_hours import OpeningHours
from intramaps.enums.enum_building import EnumNode, EnumStatus
from intramaps.enums.enum_user import EnumRole
from intramaps.users.user import User

class BuildingExit(Node):
    '''An entrance or exit of the building, that is open only at some hours.

    Attributes:
        id: Unique identifier for the exit.
        name: Name of the exit.
        opening_hours: The hours when the exit is open, or None when it has no schedule and is
            always open.
        coordinates: Coordinates of the exit.
        type: Type of the node, defined by EnumNode.
        status: Whether the exit can be used, defined by EnumStatus.
        role_restriction: The lowest role that can go to the exit, defined by EnumRole.
    '''

    def __init__(self, node_id: int, coordinates: Coordinates, node_name: str, # pylint: disable=too-many-arguments,too-many-positional-arguments
                 opening_hours: OpeningHours | None, status: EnumStatus = EnumStatus.OK,
                 role_restriction: EnumRole = EnumRole.STUDENT):
        if not isinstance(node_name, str) or not node_name.strip():
            raise ValueError("name must be a non-empty string")
        if opening_hours is not None and not isinstance(opening_hours, OpeningHours):
            raise ValueError("opening_hours must be None or an instance of OpeningHours")
        super().__init__(node_id, EnumNode.BUILDING_EXIT, coordinates, status, role_restriction)
        self.__name = node_name
        self.__opening_hours = opening_hours

    @property
    def name(self) -> str:
        '''Returns the name of the exit.'''
        return self.__name

    @property
    def opening_hours(self) -> OpeningHours | None:
        '''Returns the hours when the exit is open, or None when it is always open.'''
        return self.__opening_hours

    def is_valid_destination(self, user: User) -> bool:
        '''
        Determines if the exit is a valid destination for a user.

        On top of the rules of every node, the exit must be open now. Staff can go to it at any
        hour.

        Args:
            user: The user who wants to go to the exit.
        '''
        if not super().is_valid_destination(user):
            return False
        return (user.role == EnumRole.STAFF or self.opening_hours is None
                or self.opening_hours.is_open())
