'''User class definition.'''
from intramaps.enums.enum_user import EnumGender, EnumRole, EnumAccessibility
class User:
    '''Represents a user profile with specific attributes.

    Attributes:
        id: Unique identifier for the user.
        name: Name of the user.
        gender: Gender of the user.
        accessibility: Accessibility needs of the user, which can influence navigation and access.
        role: Role of the user, which can influence access and permissions.
    '''

    def __init__(self, user_id: int, user_name: str, user_gender: EnumGender
                 , user_accessibility: EnumAccessibility, user_role: EnumRole):
        if not isinstance(user_id, int):
            raise ValueError("id must be an integer")
        if not isinstance(user_name, str):
            raise ValueError("name must be a string")
        if not isinstance(user_gender, EnumGender):
            raise ValueError("gender must be an instance of EnumGender")
        if not isinstance(user_accessibility, EnumAccessibility):
            raise ValueError("accessibility must be an instance of EnumAccessibility")
        if not isinstance(user_role, EnumRole):
            raise ValueError("role must be an instance of EnumRole")
        self.__id = user_id
        self.__name = user_name
        self.__gender = user_gender
        self.__accessibility = user_accessibility
        self.__role = user_role

    @property
    def id(self) -> int:
        '''Returns the unique identifier for the user.'''
        return self.__id

    @property
    def name(self) -> str:
        '''Returns the name of the user.'''
        return self.__name

    @property
    def role(self) -> EnumRole:
        '''Returns the role of the user.'''
        return self.__role

    @property
    def gender(self) -> EnumGender:
        '''Returns the gender of the user.'''
        return self.__gender

    @property
    def accessibility(self) -> EnumAccessibility:
        '''Returns the accessibility needs of the user.'''
        return self.__accessibility
