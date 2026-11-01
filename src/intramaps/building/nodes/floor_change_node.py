'''A pseudo node where a person changes floors, by stairs or by elevator.'''
from intramaps.building.geometry.coordinates import Coordinates
from intramaps.building.nodes.pseudo_node import PseudoNode
from intramaps.enums.enum_building import EnumNode, EnumStatus
from intramaps.enums.enum_user import EnumRole

class FloorChangeNode(PseudoNode):
    '''
    A pseudo node where a person takes the stairs or the elevator to another floor.
    e.g.: a stairs_entrance or an elevator_door.

    Attributes:
        id: Unique identifier for the node.
        coordinates: Coordinates of the node.
        type: Type of the node, defined by EnumNode.
        facing: Direction in degrees a person faces when stepping off the stairs or the elevator
            at this node, from 0 up to 360. It follows the axes of the floor plan: 0 is to the
            right, 90 is down, 180 is to the left and 270 is up.
        status: Whether the node can be used, defined by EnumStatus.
        role_restriction: The lowest role that can use the node, defined by EnumRole.
    '''

    TYPES = (EnumNode.STAIRS_ENTRANCE, EnumNode.ELEVATOR_DOOR)

    def __init__(self, node_id: int, node_type: EnumNode, coordinates: Coordinates, # pylint: disable=too-many-arguments,too-many-positional-arguments
                 facing: float, status: EnumStatus = EnumStatus.OK,
                 role_restriction: EnumRole = EnumRole.STUDENT):
        super().__init__(node_id, node_type, coordinates, status, role_restriction)
        if isinstance(facing, bool) or not isinstance(facing, (int, float)):
            raise ValueError("facing must be a number from 0 up to 360")
        if not 0 <= facing < 360:
            raise ValueError("facing must be a number from 0 up to 360")
        self.__facing = facing

    @property
    def facing(self) -> float:
        '''Returns the direction a person faces when stepping off at this node, in degrees.'''
        return self.__facing
