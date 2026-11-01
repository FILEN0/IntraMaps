'''FloorRepository class definition.'''
from intramaps.building.floor import Floor
from intramaps.database.database import Database
from intramaps.building.floor_plan import FloorPlan

class FloorRepository:
    '''Saves and loads floors and their plans.'''

    def __init__(self, database: Database) -> None:
        self.__database = database

    def add(self, floor: Floor, plan: FloorPlan) -> None:
        '''Saves a floor and its plan in the floors table.

        Args:
            floor: The floor to save.
            plan: The image and scale of the floor.
        '''
        if plan.floor_id != floor.id:
            raise ValueError("the plan belongs to another floor")
        values = (
            floor.id,
            floor.level,
            floor.building,
            floor.elevation_m,
            plan.image_path,
            plan.width_px,
            plan.height_px,
            plan.meters_per_pixel,
        )
        self.__database.execute(
            "INSERT INTO floors (id, level, building, elevation_m, image_path, width_px, height_px, meters_per_pixel) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", # pylint: disable=line-too-long
            values,
        )

    def list_all(self) -> list[Floor]:
        '''Loads every floor, ordered by id.

        Returns:
            The floors as objects.
        '''
        rows = self.__database.fetch(
            "SELECT id, level, building, elevation_m FROM floors ORDER BY id"
        )
        return [Floor(row["id"], row["level"], row["building"], row["elevation_m"])
                for row in rows]

    def get_plan(self, floor_id: int) -> FloorPlan | None:
        '''Loads the plan of a floor.

        Args:
            floor_id: The identifier of the floor.

        Returns:
            The plan, or None if there is no floor with this id.
        '''
        rows = self.__database.fetch(
            "SELECT id, image_path, width_px, height_px, meters_per_pixel FROM floors WHERE id = ?", # pylint: disable=line-too-long
            (floor_id,),
            1,
        )
        if not rows:
            return None
        row = rows[0]
        return FloorPlan(row["id"], row["image_path"], row["width_px"], row["height_px"],
                         row["meters_per_pixel"])
