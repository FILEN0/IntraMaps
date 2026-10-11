from enum import Enum

class EnumNode(Enum):
    """Enum for node types."""
    ROOM = "ROOM"
    CORRIDOR_END = "CORRIDOR_END"
    STAIRS_ENTRANCE = "STAIRS_ENTRANCE"
    ELEVATOR_DOOR = "ELEVATOR_DOOR"
    WASHROOM = "WASHROOM"
    CAFETERIA = "CAFETERIA"
    STUDY_SPACE = "STUDY_SPACE"
    PHOTO_SPOT = "PHOTO_SPOT"
    BUILDING_EXIT = "BUILDING_EXIT"
    DRINKING_FOUNTAIN = "DRINKING_FOUNTAIN"

class EnumConnection(Enum):
    """Enum for connection types."""
    CORRIDOR = "CORRIDOR"
    STAIRS = "STAIRS"
    ELEVATOR = "ELEVATOR"

