'''Names the API uses in JSON for the enums, and the shapes of its responses.'''
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from intramaps.building.nodes.node import Node
from intramaps.enums.enum_building import EnumNode
from intramaps.enums.enum_routing import EnumMovement
from intramaps.enums.enum_user import EnumAccessibility, EnumGender, EnumRole
from intramaps.routing.instructions import write_instructions
from intramaps.routing.route import Route
from intramaps.routing.route_step import RouteStep, node_label


class GenderSlug(str, Enum):
    '''Gender values as used in the API.'''
    NONE = "none"
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class AccessibilitySlug(str, Enum):
    '''Accessibility values as used in the API.'''
    NONE = "none"
    WHEELCHAIR = "wheelchair"
    CRUTCHES = "crutches"


class RoleSlug(str, Enum):
    '''Role values as used in the API.'''
    STUDENT = "student"
    FACULTY = "faculty"
    STAFF = "staff"


class PlaceTypeSlug(str, Enum):
    '''Place types as used in the API. The corner and door points are not places.'''
    ROOM = "room"
    WASHROOM = "washroom"
    STUDY_SPACE = "study-space"
    PHOTO_SPOT = "photo-spot"
    CAFETERIA = "cafeteria"
    BUILDING_EXIT = "building-exit"
    DRINKING_FOUNTAIN = "drinking-fountain"
    BICYCLE_PARKING = "bicycle-parking"


class StatusSlug(str, Enum):
    '''Status values as used in the API.'''
    OK = "ok"
    MAINTENANCE = "maintenance"
    CLOSED = "closed"


class ConnectionSlug(str, Enum):
    '''Connection types as used in the API.'''
    CORRIDOR = "corridor"
    STAIRS = "stairs"
    ELEVATOR = "elevator"
    RAMP = "ramp"


class MovementSlug(str, Enum):
    '''Movements as used in the API.'''
    STRAIGHT = "straight"
    SLIGHT_RIGHT = "slight-right"
    RIGHT = "right"
    SHARP_RIGHT = "sharp-right"
    SLIGHT_LEFT = "slight-left"
    LEFT = "left"
    SHARP_LEFT = "sharp-left"
    BACK = "back"
    UP = "up"
    DOWN = "down"


GENDERS = {
    GenderSlug.NONE: EnumGender.NONE,
    GenderSlug.MALE: EnumGender.MALE,
    GenderSlug.FEMALE: EnumGender.FEMALE,
    GenderSlug.OTHER: EnumGender.OTHER,
}
ACCESSIBILITIES = {
    AccessibilitySlug.NONE: EnumAccessibility.NONE,
    AccessibilitySlug.WHEELCHAIR: EnumAccessibility.WHEELCHAIR,
    AccessibilitySlug.CRUTCHES: EnumAccessibility.CRUTCHES,
}
ROLES = {
    RoleSlug.STUDENT: EnumRole.STUDENT,
    RoleSlug.FACULTY: EnumRole.FACULTY,
    RoleSlug.STAFF: EnumRole.STAFF,
}
PLACE_TYPES = {slug: EnumNode[slug.name] for slug in PlaceTypeSlug}


class FloorDTO(BaseModel):
    '''A floor with the size and the scale of its plan, so the client can draw on it.'''
    id: int
    level: int
    building: str
    elevation_m: float
    width_px: int
    height_px: int
    meters_per_pixel: float
    plan_url: str


class PlaceDTO(BaseModel):
    '''A place of the building. The x and y are in meters, on the plan of its floor.'''
    id: int
    type: PlaceTypeSlug
    name: str | None
    number: str | None
    floor_id: int
    x: float
    y: float
    status: StatusSlug
    gender_restriction: GenderSlug | None
    role_restriction: RoleSlug

    @classmethod
    def from_node(cls, node: Node) -> 'PlaceDTO':
        '''Builds the DTO of a place.'''
        gender = getattr(node, "gender_restriction", None)
        has_gender = gender not in (None, EnumGender.NONE)
        return cls(
            id=node.id, type=PlaceTypeSlug[node.type.name],
            name=getattr(node, "name", None), number=getattr(node, "number", None),
            floor_id=node.coordinates.floor_id, x=node.coordinates.x, y=node.coordinates.y,
            status=StatusSlug[node.status.name],
            gender_restriction=GenderSlug[gender.name] if has_gender else None,
            role_restriction=RoleSlug[node.role_restriction.name],
        )


class PointDTO(BaseModel):
    '''A point of a step, in meters, on the plan of its floor.'''
    x: float
    y: float
    floor_id: int


class StepEndDTO(BaseModel):
    '''The node where a step begins or ends.'''
    id: int
    label: str


class StepDTO(BaseModel):
    '''One stretch of a route, walked along a single connection.'''
    model_config = ConfigDict(validate_by_name=True)

    connection: ConnectionSlug
    from_: StepEndDTO = Field(alias="from")
    to: StepEndDTO
    meters: float | None
    seconds: float
    changes_floor: bool
    points: list[PointDTO]
    movement: MovementSlug | None

    @classmethod
    def from_step(cls, step: RouteStep, movement: EnumMovement | None) -> 'StepDTO':
        '''Builds the DTO of a step. The movement is what to do where the step ends.'''
        return cls(
            connection=ConnectionSlug[step.connection.type.name],
            from_=StepEndDTO(id=step.start.id, label=node_label(step.start)),
            to=StepEndDTO(id=step.end.id, label=node_label(step.end)),
            meters=step.meters, seconds=step.seconds, changes_floor=step.changes_floor,
            points=[PointDTO(x=point.x, y=point.y, floor_id=point.floor_id)
                    for point in step.points],
            movement=None if movement is None else MovementSlug[movement.name],
        )


class RouteDTO(BaseModel):
    '''The fastest way between two places, as consecutive steps.'''
    origin: PlaceDTO
    destination: PlaceDTO
    seconds: float
    meters: float
    steps: list[StepDTO]

    @classmethod
    def from_route(cls, route: Route) -> 'RouteDTO':
        '''Builds the DTO of a route.'''
        movements = (*route.movements, None)
        return cls(
            origin=PlaceDTO.from_node(route.origin),
            destination=PlaceDTO.from_node(route.destination),
            seconds=route.seconds, meters=route.meters,
            steps=[StepDTO.from_step(step, movement)
                   for step, movement in zip(route.steps, movements)],
        )


class InstructionDTO(BaseModel):
    '''The sentence that tells how to walk one step of a route.'''
    step: int
    text: str


class HistoryDTO(BaseModel):
    '''A route that a user asked for, with its two places.'''
    id: int
    origin: PlaceDTO
    destination: PlaceDTO
    created_at: str

    @classmethod
    def from_search(cls, search: dict, places: dict[int, Node]) -> 'HistoryDTO':
        '''Builds the DTO of a search of the history, with the places found by id.'''
        return cls(id=search["id"], origin=PlaceDTO.from_node(places[search["node_a_id"]]),
                   destination=PlaceDTO.from_node(places[search["node_b_id"]]),
                   created_at=search["created_at"])


class InstructionsDTO(BaseModel):
    '''A route told in words, with one sentence for each step.'''
    instructions: list[InstructionDTO]

    @classmethod
    def from_route(cls, route: Route) -> 'InstructionsDTO':
        '''Builds the DTO of the instructions of a route.'''
        return cls(instructions=[InstructionDTO(step=index, text=text)
                                 for index, text in enumerate(write_instructions(route))])
