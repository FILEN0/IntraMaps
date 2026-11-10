'''RouteStep class definition.'''
import math
from intramaps.building.connections.connection import Connection
from intramaps.building.geometry.coordinates import Coordinates
from intramaps.building.geometry.geometry import Geometry
from intramaps.building.nodes.node import Node
from intramaps.enums.enum_routing import EnumMovement

def node_label(node: Node) -> str:
    '''Returns the name or number of a node, or its type and id when it has neither.'''
    return (getattr(node, "name", None) or getattr(node, "number", None)
            or f"{node.type.name.lower().replace('_', ' ')} {node.id}")

class RouteStep: # pylint: disable=too-many-arguments,too-many-positional-arguments
    '''One stretch of a route, walked along a single connection.

    Attributes:
        connection: The connection the stretch is walked along.
        start: The node where the stretch begins.
        end: The node where the stretch ends.
        geometry: The line of the stretch, in travel order.
        points: The points of the line.
        changes_floor: Whether the stretch goes from one floor to another.
        meters: Length of the stretch in meters, or None when it changes floors.
        rise_m: Height climbed or descended along the stretch, in meters.
        seconds: Time to walk the stretch, in seconds.
    '''

    STRAIGHT_LIMIT = 20
    SLIGHT_LIMIT = 60
    SHARP_LIMIT = 120
    BACK_LIMIT = 160

    def __init__(self, connection: Connection, start: Node, end: Node,
                 geometry: Geometry, seconds: float, rise_m: float = 0.0):
        if not isinstance(connection, Connection):
            raise ValueError("connection must be an instance of Connection")
        if not isinstance(start, Node) or not isinstance(end, Node):
            raise ValueError("start and end must be nodes")
        if not isinstance(geometry, Geometry):
            raise ValueError("geometry must be an instance of Geometry")
        if isinstance(seconds, bool) or not isinstance(seconds, (int, float)) or seconds < 0:
            raise ValueError("seconds must be a number that is not negative")
        self.__connection = connection
        self.__start = start
        self.__end = end
        self.__geometry = geometry
        self.__seconds = seconds
        self.__rise_m = rise_m

    @property
    def connection(self) -> Connection:
        '''Returns the connection the stretch is walked along.'''
        return self.__connection

    @property
    def start(self) -> Node:
        '''Returns the node where the stretch begins.'''
        return self.__start

    @property
    def end(self) -> Node:
        '''Returns the node where the stretch ends.'''
        return self.__end

    @property
    def geometry(self) -> Geometry:
        '''Returns the line of the stretch.'''
        return self.__geometry

    @property
    def points(self) -> tuple[Coordinates, ...]:
        '''Returns the points of the stretch in travel order.'''
        return self.__geometry.points

    @property
    def changes_floor(self) -> bool:
        '''Returns whether the stretch goes from one floor to another, like stairs and elevators.'''
        return len({point.floor_id for point in self.__geometry.points}) > 1

    @property
    def meters(self) -> float | None:
        '''Returns the length of the stretch in meters, or None when it changes floors.'''
        if self.changes_floor:
            return None
        return self.__geometry.length

    @property
    def rise_m(self) -> float:
        '''Returns the height climbed, or descended if negative, in meters.'''
        return self.__rise_m

    def go_to(self, following: 'RouteStep') -> EnumMovement | None:
        '''Finds what to do where this step meets the one that comes next.

        Only the junction counts, and not the corners inside each step. When this step changes
        floors, the turn is measured from the facing of the node where it ends. The size of the
        turn, in degrees, decides the movement: up to STRAIGHT_LIMIT is straight on, up to
        SLIGHT_LIMIT is slightly to a side, up to SHARP_LIMIT is to a side, up to BACK_LIMIT is
        sharply to a side, and more than that is going back.

        Args:
            following: The step that starts where this one ends.

        Returns:
            STRAIGHT, SLIGHT_RIGHT, RIGHT, SHARP_RIGHT, BACK or the same three to the left.
            UP or DOWN when the following step changes floors. It is None when there is no
            direction to compare, like a step with no length.
        '''
        if not isinstance(following, RouteStep):
            raise ValueError("following must be a RouteStep object")
        print("go_to", self.end.id, following.end.id, following.rise_m)
        if following.rise_m > 0:
            return EnumMovement.UP
        if following.rise_m < 0:
            return EnumMovement.DOWN
        angle = self.__angle_to(following)
        return None if angle is None else self.__movement(angle)

    def __angle_to(self, following: 'RouteStep') -> float | None:
        if following.changes_floor or following.geometry.length == 0:
            return None
        if self.changes_floor:
            facing = getattr(self.end, "facing", None)
            if facing is None:
                return None
            delta_x, delta_y = following.geometry.departure_point - following.points[0]
            heading = math.degrees(math.atan2(delta_y, delta_x))
            print("go_to leaving", self.end.id, "facing", facing, "heading", heading)
            return (heading - facing + 180) % 360 - 180
        if self.geometry.length == 0:
            return None
        junction = self.points[-1]
        if following.points[0] != junction:
            raise ValueError("the steps do not meet at the same point")
        angle = junction.turn_angle(self.geometry.approach_point,
                                    following.geometry.departure_point)
        return angle

    def __movement(self, angle: float) -> EnumMovement:
        size = abs(angle)
        right = angle > 0
        if size <= self.STRAIGHT_LIMIT:
            return EnumMovement.STRAIGHT
        if size > self.BACK_LIMIT:
            return EnumMovement.BACK
        if size <= self.SLIGHT_LIMIT:
            return EnumMovement.SLIGHT_RIGHT if right else EnumMovement.SLIGHT_LEFT
        if size <= self.SHARP_LIMIT:
            return EnumMovement.RIGHT if right else EnumMovement.LEFT
        return EnumMovement.SHARP_RIGHT if right else EnumMovement.SHARP_LEFT

    @property
    def seconds(self) -> float:
        '''Returns the time to walk the stretch, in seconds.'''
        return self.__seconds
