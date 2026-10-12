'''Enums for building elements.'''
from enum import Enum

class EnumNode(Enum):
    '''Enum for node types.'''
    NONE = "NONE"
    '''Physical nodes are places where the user search for to get to.'''
    ROOM = "ROOM"
    WASHROOM = "WASHROOM"
    STUDY_SPACE = "STUDY_SPACE"
    PHOTO_SPOT = "PHOTO_SPOT"
    CAFETERIA = "CAFETERIA"
    BUILDING_EXIT = "BUILDING_EXIT"
    DRINKING_FOUNTAIN = "DRINKING_FOUNTAIN"
    '''Pseudo nodes are places where the user navigate through, but not target destinations.'''
    CORRIDOR_END = "CORRIDOR_END"
    STAIRS_ENTRANCE = "STAIRS_ENTRANCE"
    RAMP_ENTRANCE = "RAMP_ENTRANCE"
    ELEVATOR_DOOR = "ELEVATOR_DOOR"

class EnumConnection(Enum):
    '''Enum for connection types.'''
    CORRIDOR = "CORRIDOR"
    STAIRS = "STAIRS"
    ELEVATOR = "ELEVATOR"
    RAMP = "RAMP"
