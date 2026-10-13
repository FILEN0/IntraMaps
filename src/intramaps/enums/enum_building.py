'''Enums for building elements.'''
from enum import Enum

class EnumNode(Enum):
    '''Enum for node types.'''
    NONE = 0
    '''Physical nodes are places where the user search for to get to.'''
    ROOM = 1
    WASHROOM = 2
    STUDY_SPACE = 3
    PHOTO_SPOT = 4
    CAFETERIA = 5
    BUILDING_EXIT = 6
    DRINKING_FOUNTAIN = 7
    BICYCLE_PARKING = 8
    '''Pseudo nodes are places where the user navigate through, but not target destinations.'''
    CORRIDOR_END = 9
    STAIRS_ENTRANCE = 10
    RAMP_ENTRANCE = 11
    ELEVATOR_DOOR = 12

class EnumConnection(Enum):
    '''Enum for connection types.'''
    CORRIDOR = 0
    STAIRS = 1
    ELEVATOR = 2
    RAMP = 3

class EnumStatus(Enum):
    '''Enum for node and connection status'''
    OK = 0
    MAINTENANCE = 1
    CLOSED = 2
