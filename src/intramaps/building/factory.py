'''Building Models Factory. Parses database rows into objects.'''
from datetime import time
from intramaps.building.geometry.coordinates import Coordinates
from intramaps.building.nodes.floor_change_node import FloorChangeNode
from intramaps.building.nodes.node import Node
from intramaps.building.nodes.pseudo_node import PseudoNode
from intramaps.building.nodes.physical.bicycle_parking import BicycleParking
from intramaps.building.nodes.physical.building_exit import BuildingExit
from intramaps.building.nodes.physical.cafeteria import Cafeteria
from intramaps.building.nodes.physical.drinking_fountain import DrinkingFountain
from intramaps.building.nodes.physical.photo_spot import PhotoSpot
from intramaps.building.nodes.physical.room import Room
from intramaps.building.nodes.physical.study_space import StudySpace
from intramaps.building.nodes.physical.washroom import Washroom
from intramaps.building.opening_hours import OpeningHours
from intramaps.enums.enum_building import EnumNode, EnumStatus
from intramaps.enums.enum_user import EnumGender, EnumRole

PLACES_WITH_HOURS = {
    EnumNode.CAFETERIA: Cafeteria,
    EnumNode.BUILDING_EXIT: BuildingExit,
}

NAMED_PLACES = {
    EnumNode.STUDY_SPACE: StudySpace,
    EnumNode.PHOTO_SPOT: PhotoSpot,
    EnumNode.DRINKING_FOUNTAIN: DrinkingFountain,
    EnumNode.BICYCLE_PARKING: BicycleParking,
}

def make_coordinates(row) -> Coordinates:
    '''Parses row into coordinates'''
    return Coordinates(row["x"], row["y"], row["floor_id"])

def make_opening_hours(row) -> OpeningHours | None:
    '''Parses row into opening hours, or None when the place has no schedule'''
    if row["opens_at"] is None:
        return None
    return OpeningHours(time.fromisoformat(row["opens_at"]), time.fromisoformat(row["closes_at"]))

def make_node(row) -> Node:
    '''Parses row into specific node.

    Args:
        row: A row of the nodes table, readable by column name.

    Returns:
        A PseudoNode for corridor ends and ramp entrances, a FloorChangeNode for stairs
        entrances and elevator doors, a Washroom, a Cafeteria or a BuildingExit with their
        opening hours, one of the other named places (StudySpace, PhotoSpot, DrinkingFountain,
        BicycleParking) or a Room.
    '''
    node_type = EnumNode(row["type"])
    coordinates = make_coordinates(row)
    status = EnumStatus(row["status"])
    role = EnumRole(row["role_restriction"])
    match node_type:
        case EnumNode.CORRIDOR_END | EnumNode.RAMP_ENTRANCE:
            return PseudoNode(row["id"], node_type, coordinates, status, role)
        case EnumNode.STAIRS_ENTRANCE | EnumNode.ELEVATOR_DOOR:
            return FloorChangeNode(row["id"], node_type, coordinates, row["facing"], status, role)
        case EnumNode.WASHROOM:
            gender = EnumGender(row["gender_restriction"])
            return Washroom(row["id"], coordinates, row["name"], gender, status, role)
        case _ if node_type in PLACES_WITH_HOURS:
            hours = make_opening_hours(row)
            return PLACES_WITH_HOURS[node_type](row["id"], coordinates, row["name"], hours, status,
                                                role)
        case _ if node_type in NAMED_PLACES:
            return NAMED_PLACES[node_type](row["id"], coordinates, row["name"], status, role)
        case _:
            return Room(row["id"], coordinates, row["name"], row["number"], status, role)
