'''Enums for user attributes.'''
from enum import Enum

class EnumGender(Enum):
    '''Enum for gender types.'''
    MALE = 0
    FEMALE = 1
    OTHER = 2

class EnumRole(Enum):
    '''Enum for user roles.'''
    STUDENT = 0
    FACULTY = 1
    STAFF = 2

class EnumAccessibility(Enum):
    '''Enum for accessibility needs.'''
    NONE = 0
    WHEELCHAIR = 1
    CRUTCHES = 2
