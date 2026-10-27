'''Enums for routes.'''
from enum import Enum

class EnumMovement(Enum):
    '''Enum for what to do where a step of a route meets the next one.'''
    STRAIGHT = 0
    RIGHT = 1
    LEFT = 2
    BACK = 3
    UP = 4
    DOWN = 5
    SLIGHT_RIGHT = 6
    SLIGHT_LEFT = 7
    SHARP_RIGHT = 8
    SHARP_LEFT = 9
