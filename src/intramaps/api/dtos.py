'''Names the API uses in JSON for the enums, and the shapes of its responses.'''
from enum import Enum

from pydantic import BaseModel

from intramaps.building.nodes.node import Node
from intramaps.enums.enum_building import EnumNode
from intramaps.enums.enum_user import EnumAccessibility, EnumGender, EnumRole


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
