'''Shared slugs, converters and DTO builders for the API.'''
from enum import Enum

from intramaps.enums.enum_building import EnumConnection, EnumNode, EnumStatus
from intramaps.enums.enum_routing import EnumMovement
from intramaps.enums.enum_user import EnumAccessibility, EnumGender, EnumRole
from intramaps.routing.route import Route
from intramaps.routing.route_step import RouteStep
from intramaps.users.user import User


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


class NodeTypeSlug(str, Enum):
    '''Physical node type values as used in the API.'''
    ROOM = "room"
    WASHROOM = "washroom"
    STUDY_SPACE = "study-space"
    PHOTO_SPOT = "photo-spot"
    CAFETERIA = "cafeteria"
    BUILDING_EXIT = "building-exit"
    DRINKING_FOUNTAIN = "drinking-fountain"
    BICYCLE_PARKING = "bicycle-parking"


GENDER_MAP = {
    GenderSlug.NONE: EnumGender.NONE,
    GenderSlug.MALE: EnumGender.MALE,
    GenderSlug.FEMALE: EnumGender.FEMALE,
    GenderSlug.OTHER: EnumGender.OTHER,
}

ACCESSIBILITY_MAP = {
    AccessibilitySlug.NONE: EnumAccessibility.NONE,
    AccessibilitySlug.WHEELCHAIR: EnumAccessibility.WHEELCHAIR,
    AccessibilitySlug.CRUTCHES: EnumAccessibility.CRUTCHES,
}

ROLE_MAP = {
    RoleSlug.STUDENT: EnumRole.STUDENT,
    RoleSlug.FACULTY: EnumRole.FACULTY,
    RoleSlug.STAFF: EnumRole.STAFF,
}

NODE_TYPE_MAP = {
    NodeTypeSlug.ROOM: EnumNode.ROOM,
    NodeTypeSlug.WASHROOM: EnumNode.WASHROOM,
    NodeTypeSlug.STUDY_SPACE: EnumNode.STUDY_SPACE,
    NodeTypeSlug.PHOTO_SPOT: EnumNode.PHOTO_SPOT,
    NodeTypeSlug.CAFETERIA: EnumNode.CAFETERIA,
    NodeTypeSlug.BUILDING_EXIT: EnumNode.BUILDING_EXIT,
    NodeTypeSlug.DRINKING_FOUNTAIN: EnumNode.DRINKING_FOUNTAIN,
    NodeTypeSlug.BICYCLE_PARKING: EnumNode.BICYCLE_PARKING,
}



def _node_type_slug(node_type: EnumNode) -> str:
    return node_type.name.lower().replace('_', '-')


def _status_slug(status: EnumStatus) -> str:
    return status.name.lower()


def _connection_slug(conn_type: EnumConnection) -> str:
    return conn_type.name.lower()


def _movement_slug(movement: EnumMovement | None) -> str | None:
    if movement is None:
        return None
    return movement.name.lower().replace('_', '-')


def _node_label(node) -> str:
    return (getattr(node, "name", None) or getattr(node, "number", None)
            or f"{node.type.name.lower().replace('_', ' ')} {node.id}")


def _gender_restriction_slug(node) -> str | None:
    gender_restriction = getattr(node, 'gender_restriction', None)
    if gender_restriction is None or gender_restriction == EnumGender.NONE:
        return None
    return gender_restriction.name.lower()



def make_guest_user(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    gender: GenderSlug = GenderSlug.NONE,
    accessibility: AccessibilitySlug = AccessibilitySlug.NONE,
    role: RoleSlug = RoleSlug.STUDENT,
    speed: float = User.DEFAULT_SPEED,
) -> User:
    '''Creates a temporary User for unauthenticated requests.'''
    return User(
        user_id=0,
        user_name="guest",
        user_gender=GENDER_MAP[gender],
        user_accessibility=ACCESSIBILITY_MAP[accessibility],
        user_role=ROLE_MAP[role],
        user_speed=speed,
    )



def place_dto(node) -> dict:
    '''Builds a PlaceDTO dict from a Node.'''
    return {
        "id": node.id,
        "type": _node_type_slug(node.type),
        "name": getattr(node, "name", None),
        "number": getattr(node, "number", None),
        "floor_id": node.coordinates.floor_id,
        "x": node.coordinates.x,
        "y": node.coordinates.y,
        "status": _status_slug(node.status),
        "gender_restriction": _gender_restriction_slug(node),
        "role_restriction": node.role_restriction.name.lower(),
    }


def user_dto(user: User) -> dict:
    '''Builds a UserDTO dict from a User.'''
    return {
        "id": user.id,
        "username": user.name,
        "gender": user.gender.name.lower(),
        "accessibility": user.accessibility.name.lower(),
        "role": user.role.name.lower(),
        "speed": user.speed,
    }


def _step_dto(step: RouteStep, movement: EnumMovement | None) -> dict:
    return {
        "connection": _connection_slug(step.connection.type),
        "from": {"id": step.start.id, "label": _node_label(step.start)},
        "to": {"id": step.end.id, "label": _node_label(step.end)},
        "meters": step.meters,
        "seconds": step.seconds,
        "changes_floor": step.changes_floor,
        "points": [
            {"x": p.x, "y": p.y, "floor_id": p.floor_id}
            for p in step.points
        ],
        "movement": _movement_slug(movement),
    }


def route_dto(route: Route) -> dict:
    '''Builds a RouteDTO dict from a Route.'''
    movements = route.movements
    steps = [
        _step_dto(step, movements[i] if i < len(movements) else None)
        for i, step in enumerate(route.steps)
    ]
    return {
        "origin": place_dto(route.origin),
        "destination": place_dto(route.destination),
        "seconds": route.seconds,
        "meters": sum(s["meters"] or 0 for s in steps),
        "steps": steps,
    }


_MOVEMENT_TEXT = {
    None: "Siga em frente",
    EnumMovement.STRAIGHT: "Siga em frente",
    EnumMovement.SLIGHT_RIGHT: "Vire levemente à direita",
    EnumMovement.RIGHT: "Vire à direita",
    EnumMovement.SHARP_RIGHT: "Vire acentuadamente à direita",
    EnumMovement.SLIGHT_LEFT: "Vire levemente à esquerda",
    EnumMovement.LEFT: "Vire à esquerda",
    EnumMovement.SHARP_LEFT: "Vire acentuadamente à esquerda",
    EnumMovement.BACK: "Retorne na direção oposta",
}


def _instruction_text(step: RouteStep, movement: EnumMovement | None, is_last: bool) -> str:
    conn = step.connection.type
    if conn == EnumConnection.STAIRS:
        return "Siga pela escada para o próximo andar."
    if conn == EnumConnection.ELEVATOR:
        return "Pegue o elevador para o próximo andar."
    if conn == EnumConnection.RAMP:
        return "Siga pela rampa."
    meters = step.meters
    text = _MOVEMENT_TEXT.get(movement, "Siga")
    if meters:
        text += f" por {meters:.0f} m"
    text += "."
    if is_last:
        dest = getattr(step.end, "name", None) or getattr(step.end, "number", None)
        if dest:
            text += f" Você chegou: {dest}."
    return text


def instructions_dto(route: Route) -> dict:
    '''Builds an InstructionsDTO dict from a Route.'''
    movements = route.movements
    steps = route.steps
    return {
        "instructions": [
            {
                "step": i + 1,
                "text": _instruction_text(
                    step,
                    movements[i] if i < len(movements) else None,
                    i == len(steps) - 1,
                ),
            }
            for i, step in enumerate(steps)
        ]
    }
