'''Room class definition.'''
from intramaps.building.nodes.physical.physical_node import PhysicalNode
from intramaps.enums.enum_building import EnumNode

class Room(PhysicalNode):
    '''
    A room in the building.
    
    Attributes:
        id: Unique identifier for the room.
        name: Name of the room.
        coordinates: Coordinates of the room.
        type: Type of the node, defined by EnumNode.
    '''

    def __init__(self, node_id: int, coordinates, node_name: str):
        super().__init__(node_id, EnumNode.ROOM, coordinates, node_name)

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
        return f"Room(id={self.id}, name={self.name}, coordinates={
            self.coordinates}, type={self.type})"

    def __repr__(self) -> str:
        return f"Room(id={self.id}, name={self.name}, coordinates={
            self.coordinates}, type={self.type})"
