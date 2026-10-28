'''OpeningHours class definition.'''
from datetime import datetime, time

class OpeningHours:
    '''The hours of the day when a place is open, the same every day.

    A place that closes after midnight has closes_at earlier than opens_at, like 18:00 to 02:00.

    Attributes:
        opens_at: Time of the day when the place opens.
        closes_at: Time of the day when the place closes.
    '''

    def __init__(self, opens_at: time, closes_at: time):
        if not isinstance(opens_at, time) or not isinstance(closes_at, time):
            raise ValueError("opens_at and closes_at must be time objects")
        if opens_at == closes_at:
            raise ValueError("opens_at and closes_at must be different")
        self.__opens_at = opens_at
        self.__closes_at = closes_at

    @property
    def opens_at(self) -> time:
        '''Returns the time of the day when the place opens.'''
        return self.__opens_at

    @property
    def closes_at(self) -> time:
        '''Returns the time of the day when the place closes.'''
        return self.__closes_at

    def is_open(self, at: time | None = None) -> bool:
        '''Determines if the place is open at a time of the day.

        Args:
            at: The time of the day to check. When it is not given, the time now.
        '''
        moment = datetime.now().time() if at is None else at
        if self.__opens_at < self.__closes_at:
            return self.__opens_at <= moment < self.__closes_at
        return moment >= self.__opens_at or moment < self.__closes_at
