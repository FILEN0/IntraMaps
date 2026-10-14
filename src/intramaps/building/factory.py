'''Building Models Factory. Parses database rows into objects.'''
from intramaps.building.geometry.coordinates import Coordinates
from intramaps.building.nodes.node import Node
from intramaps.building.nodes.pseudo_node import PseudoNode
from intramaps.building.nodes.physical.room import Room
from intramaps.enums.enum_building import EnumNode

def make_coordinates(row) -> Coordinates:
    '''Parses row into coordinates'''
    return Coordinates(row["x"], row["y"], row["floor_id"])

def make_node(row) -> Node:
    '''Parses row into specific node.

    Args:
        row: A row of the nodes table, readable by column name.

    Returns:
        A PseudoNode for pass-through types, or a Room for every physical type
        (physical types without a class of their own yet are rooms).

    Raises:
        ValueError: If the type is unknown, or a room has no name.
    '''
    node_type = EnumNode(row["type"])
    coordinates = make_coordinates(row)
    match node_type:
        case (EnumNode.CORRIDOR_END | EnumNode.STAIRS_ENTRANCE
              | EnumNode.RAMP_ENTRANCE | EnumNode.ELEVATOR_DOOR):
            return PseudoNode(row["id"], node_type, coordinates)
        case _:
            return Room(row["id"], coordinates, row["name"])
