'''Floor class definition.'''

class Floor:
    '''A floor of a building.

    Attributes:
        id: Unique identifier for the floor, the one stored in Coordinates.floor_id.
        level: Level of the floor in its building (1 is the first floor above the ground).
        building: Name of the building the floor belongs to.
        elevation_m: Height of the floor surface above the ground floor, in meters.
    '''

    def __init__(self, floor_id: int, level: int, building: str, elevation_m: float):
        if not isinstance(floor_id, int):
            raise ValueError("id must be an integer")
        if not isinstance(level, int):
            raise ValueError("level must be an integer")
        if not isinstance(building, str) or not building.strip():
            raise ValueError("building must be a non-empty string")
        if isinstance(elevation_m, bool) or not isinstance(elevation_m, (int, float)):
            raise ValueError("elevation must be a number")
        self.__id = floor_id
        self.__level = level
        self.__building = building
        self.__elevation_m = elevation_m

    @property
    def id(self) -> int:
        '''Returns the unique identifier for the floor.'''
        return self.__id

    @property
    def level(self) -> int:
        '''Returns the level of the floor in its building.'''
        return self.__level

    @property
    def building(self) -> str:
        '''Returns the name of the building.'''
        return self.__building

    @property
    def elevation_m(self) -> float:
        '''Returns the height of the floor above the ground floor, in meters.'''
        return self.__elevation_m

    def __repr__(self) -> str:
        return (f"Floor(id={self.id}, level={self.level}, building={self.building}, "
                f"elevation_m={self.elevation_m})")
