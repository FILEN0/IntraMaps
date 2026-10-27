'''A pseudo node in a building. 
Places where the user navigate through, but not target destinations. 
Can be a corridor_end, elevator_door, ramp_entrance, stairs_entrance .
'''
from abc import ABC
from intramaps.building.nodes.node import Node
from intramaps.building.geometry.coordinates import Coordinates
from intramaps.enums.enum_building import EnumNode
from intramaps.enums.enum_user import EnumAccessibility, EnumGender, EnumRole

class PseudoNode(Node,ABC):
    '''
    A pseudo node in a building. 
    Places where the user navigate through, but not target destinations. 
    e.g.: a corridor_end, elevator_door, ramp_entrance, or stairs_entrance.

    Attributes:
        id: Unique identifier for the node.
        coordinates: Coordinates of the node.
        type: Type of the node, defined by EnumNode.
        facing: Direction in degrees a person faces when stepping off the elevator or the stairs
            at this node, from 0 up to 360. It follows the axes of the floor plan: 0 is to the
            right, 90 is down, 180 is to the left and 270 is up. Elevator doors and stairs
            entrances must have it, and the other types must not.
    '''

    FACING_TYPES = (EnumNode.ELEVATOR_DOOR, EnumNode.STAIRS_ENTRANCE)

    def __init__(self, node_id: int, node_type: EnumNode, coordinates: Coordinates,
                 facing: float | None = None):
        if node_type not in [EnumNode.CORRIDOR_END, EnumNode.ELEVATOR_DOOR,
                             EnumNode.RAMP_ENTRANCE, EnumNode.STAIRS_ENTRANCE]:
            raise ValueError("Cant create a PseudoNode with type " + str(node_type)
                             + ". Must be one of: " +
                             str([EnumNode.CORRIDOR_END, EnumNode.ELEVATOR_DOOR,
                                  EnumNode.RAMP_ENTRANCE, EnumNode.STAIRS_ENTRANCE]))
        if node_type in self.FACING_TYPES and facing is None:
            raise ValueError(f"a {node_type.name} must have a facing")
        if node_type not in self.FACING_TYPES and facing is not None:
            raise ValueError(f"a {node_type.name} cannot have a facing")
        if facing is not None and (isinstance(facing, bool) or not isinstance(facing, (int, float))
                                   or not 0 <= facing < 360):
            raise ValueError("facing must be a number from 0 up to 360")
        super().__init__(node_id, node_type, coordinates)
        self.__facing = facing

    @property
    def facing(self) -> float | None:
        '''Returns the direction a person faces when stepping off at this node, or None.'''
        return self.__facing

    def is_valid_destination(self, gender: EnumGender, accessibility: EnumAccessibility,
                              role: EnumRole) -> bool:
        '''
        Determines if the node is a valid destination for a given user profile.
        Since pseudo nodes are not target destinations, this method always returns False.
        '''
        return False
