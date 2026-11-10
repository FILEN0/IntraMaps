'''Names the API uses in JSON for the enums, and the shapes of its responses.'''
from enum import Enum

from pydantic import BaseModel

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
