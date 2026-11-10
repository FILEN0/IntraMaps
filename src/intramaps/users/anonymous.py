'''Anonymous class definition.'''
from intramaps.enums.enum_user import EnumAccessibility, EnumGender, EnumRole
from intramaps.users.user import User


class Anonymous(User):
    '''A visitor without login. It has a profile for the routes, but no id and no name.'''

    def __init__(self, user_gender: EnumGender, user_accessibility: EnumAccessibility, # pylint: disable=super-init-not-called
                 user_role: EnumRole, user_speed: float = User.DEFAULT_SPEED):
        self.gender = user_gender
        self.accessibility = user_accessibility
        self.role = user_role
        self.speed = user_speed

    @property
    def id(self) -> None:
        '''Returns None, an anonymous has no id.'''
        return None

    @property
    def name(self) -> None:
        '''Returns None, an anonymous has no name.'''
        return None

    @property
    def is_authenticated(self) -> bool:
        '''Returns False, an anonymous is not logged in.'''
        return False
