'''User class definition.'''
from intramaps.enums.enum_user import EnumGender, EnumRole, EnumAccessibility
class User: # pylint: disable=too-many-instance-attributes
    '''Represents a user profile with specific attributes.

    Attributes:
        id: Unique identifier for the user.
        name: Name of the user.
        gender: Gender of the user.
        accessibility: Accessibility needs of the user, which can influence navigation and access.
        role: Role of the user, which can influence access and permissions.
        speed: Walking speed of the user in meters per second, used to measure distances in time.
    '''

    DEFAULT_SPEED = 1.4
    MAX_SPEED = 10

    def __init__(self, user_id: int, user_name: str, user_gender: EnumGender, # pylint: disable=too-many-arguments,too-many-positional-arguments
                 user_accessibility: EnumAccessibility, user_role: EnumRole,
                 user_speed: float = DEFAULT_SPEED):
        if not isinstance(user_id, int):
            raise ValueError("id must be an integer")
        self.__id = user_id
        self.name = user_name
        self.gender = user_gender
        self.accessibility = user_accessibility
        self.role = user_role
        self.speed = user_speed

    @property
    def id(self) -> int:
        '''Returns the unique identifier for the user.'''
        return self.__id

    @property
    def name(self) -> str:
        '''Returns the name of the user.'''
        return self.__name

    @name.setter
    def name(self, user_name: str) -> None:
        if not isinstance(user_name, str):
            raise ValueError("name must be a string")
        self.__name = user_name

    @property
    def role(self) -> EnumRole:
        '''Returns the role of the user.'''
        return self.__role

    @role.setter
    def role(self, user_role: EnumRole) -> None:
        if not isinstance(user_role, EnumRole):
            raise ValueError("role must be an instance of EnumRole")
        self.__role = user_role

    @property
    def gender(self) -> EnumGender:
        '''Returns the gender of the user.'''
        return self.__gender

    @gender.setter
    def gender(self, user_gender: EnumGender) -> None:
        if not isinstance(user_gender, EnumGender):
            raise ValueError("gender must be an instance of EnumGender")
        self.__gender = user_gender

    @property
    def accessibility(self) -> EnumAccessibility:
        '''Returns the accessibility needs of the user.'''
        return self.__accessibility

    @accessibility.setter
    def accessibility(self, user_accessibility: EnumAccessibility) -> None:
        if not isinstance(user_accessibility, EnumAccessibility):
            raise ValueError("accessibility must be an instance of EnumAccessibility")
        self.__accessibility = user_accessibility

    @property
    def speed(self) -> float:
        '''Returns the walking speed of the user in meters per second.'''
        return self.__speed

    @speed.setter
    def speed(self, user_speed: float) -> None:
        if isinstance(user_speed, bool) or not isinstance(user_speed, (int, float)):
            raise ValueError("speed must be a number")
        if user_speed <= 0:
            raise ValueError("speed must be positive")
        self.__speed = user_speed
