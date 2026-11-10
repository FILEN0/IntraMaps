'''FloorService class definition.'''
from intramaps.building.floor import Floor
from intramaps.building.floor_plan import FloorPlan
from intramaps.database.floor_repository import FloorRepository


class FloorService:
    '''Finds the floors of the building and their plans.

    Args:
        floor_repository: The repository that loads the floors and their plans.
    '''

    def __init__(self, floor_repository: FloorRepository) -> None:
        self.__floor_repository = floor_repository

    def list_floors(self) -> list[tuple[Floor, FloorPlan]]:
        '''Returns every floor with its plan, in id order.'''
        return [(floor, self.__floor_repository.get_plan(floor.id))
                for floor in self.__floor_repository.list_all()]

    def get_plan(self, floor_id: int) -> FloorPlan | None:
        '''Returns the plan of a floor, or None if there is no floor with this id.'''
        return self.__floor_repository.get_plan(floor_id)

    def exists(self, floor_id: int) -> bool:
        '''Returns whether there is a floor with this id.'''
        return self.__floor_repository.get_plan(floor_id) is not None
