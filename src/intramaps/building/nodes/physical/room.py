'''Room class definition.'''
from intramaps.building.nodes.node import Node
from intramaps.enums.enum_building import EnumNode

class Room(Node):
    '''
    A room in the building. A room has a number, a name, or both, and at least one is required.
    
    Attributes:
        id: Unique identifier for the room.
        name: Name of the room, or None if it only has a number.
        number: Number of the room (text, like "2069A"), or None if it only has a name.
        coordinates: Coordinates of the room.
        type: Type of the node, defined by EnumNode.
    '''

    def __init__(self, node_id: int, coordinates, node_name: str | None = None,
                 node_number: str | None = None):
        for value, label in ((node_name, "name"), (node_number, "number")):
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise ValueError(f"{label} must be None or a non-empty string")
        if node_name is None and node_number is None:
            raise ValueError("a room must have a name or a number")
        super().__init__(node_id, EnumNode.ROOM, coordinates)
        self.__name = node_name
        self.__number = node_number

    @property
    def name(self) -> str | None:
        '''Returns the name of the room, or None if it has none.'''
        return self.__name

    @property
    def number(self) -> str | None:
        '''Returns the number of the room, or None if it has none.'''
        return self.__number

    def is_valid_destination(self, gender, accessibility, role) -> bool:
        '''
        Determines if the room is a valid destination for a given user profile.

        Args:
            gender: The gender of the user.
            accessibility: The accessibility needs of the user.
            role: The role of the user.
        '''
        return True

    def __str__(self) -> str:
        return (f"Room(id={self.id}, name={self.name}, number={self.number}, "
                f"coordinates={self.coordinates}, type={self.type})")

    def __repr__(self) -> str:
        return self.__str__()
