'''Enums for user attributes.'''
from enum import Enum

class EnumGender(Enum):
    '''Enum for gender types.'''
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"

class EnumRole(Enum):
    '''Enum for user roles.'''
    STUDENT = "STUDENT"
    FACULTY = "FACULTY"
    STAFF = "STAFF"

class EnumAccessibility(Enum):
    '''Enum for accessibility needs.'''
    NONE = "NONE"
    WHEELCHAIR = "WHEELCHAIR"
    CRUTCHES = "CRUTCHES"
