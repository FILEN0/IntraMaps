'''UserProfile class definition.'''
from intramaps.enums.enum_user import EnumGender, EnumAccessibility


class UserProfile:
    '''Temporary profile used to personalize routing for a session.

    Can be used by anonymous users or built from a logged-in User.
    Determines which bathrooms are shown and whether the route avoids stairs.

    Attributes:
        gender: Gender used to filter bathroom results.
        accessibility: Accessibility needs used to filter routes.
    '''

    def __init__(
        self,
        gender: EnumGender = EnumGender.NONE,
        accessibility: EnumAccessibility = EnumAccessibility.NONE,
    ) -> None:
        self.__gender = gender
        self.__accessibility = accessibility

    @property
    def gender(self) -> EnumGender:
        '''Returns the gender.'''
        return self.__gender

    @property
    def accessibility(self) -> EnumAccessibility:
        '''Returns the accessibility needs.'''
        return self.__accessibility

    @property
    def needs_accessible_route(self) -> bool:
        '''Returns True if the user needs a route without stairs.'''
        return self.__accessibility != EnumAccessibility.NONE