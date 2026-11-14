'''Loads the ICEx seed into the database.

Run it from the project folder, with the server stopped:

    python helpers/load_demo.py

It deletes data/intramaps.db first, so the database always restarts from the seed.
'''
import json
from pathlib import Path

from intramaps.building.factory import make_connection, make_node
from intramaps.building.floor import Floor
from intramaps.building.floor_plan import FloorPlan
from intramaps.building.nodes.node import Node
from intramaps.database.connection_repository import ConnectionRepository
from intramaps.database.database import Database
from intramaps.database.floor_repository import FloorRepository
from intramaps.database.node_repository import NodeRepository

DATA_DIR = Path(__file__).parent.parent / "data"
SEED_PATH = DATA_DIR / "seed_icex.json"
DATABASE_PATH = DATA_DIR / "intramaps.db"


def load_floors(seed: dict, repository: FloorRepository) -> dict[int, Floor]:
    '''Saves the floors with their plans. Returns the floors by id.'''
    floors = {}
    for item in seed["floors"]:
        if not (DATA_DIR / item["image"]).exists():
            raise FileNotFoundError(f"floor plan not found: {item['image']}")
        floor = Floor(item["id"], item["level"], item["building"], item["elevation_m"])
        width, height = item["size_px"]
        plan = FloorPlan(floor.id, item["image"], width, height, item["meters_per_pixel"])
        repository.add(floor, plan)
        floors[floor.id] = floor
    return floors


def load_nodes(seed: dict, scales: dict[int, float], repository: NodeRepository) -> dict[int, Node]:
    '''Saves the nodes, with the positions turned from pixels into meters. Returns them by id.'''
    nodes = {}
    for item in seed["nodes"]:
        scale = scales[item["floor_id"]]
        row = {
            "id": item["id"], "floor_id": item["floor_id"], "type": item["type"],
            "name": item.get("name"), "number": item.get("number"),
            "x": round(item["x"] * scale, 3), "y": round(item["y"] * scale, 3),
            "facing": item.get("facing"),
            "gender_restriction": item.get("gender_restriction", 0),
            "role_restriction": item.get("role_restriction", 0),
            "status": item.get("status", 0),
            "opens_at": item.get("opens_at"), "closes_at": item.get("closes_at"),
        }
        node = make_node(row)
        repository.add(node)
        nodes[node.id] = node
    return nodes


def rise_of(item: dict, floors: dict[int, Floor], node_a: Node, node_b: Node) -> float:
    '''Returns the height of a connection: the one in the seed, or the gap between the floors.'''
    if "rise_m" in item:
        return item["rise_m"]
    elevation_a = floors[node_a.coordinates.floor_id].elevation_m
    elevation_b = floors[node_b.coordinates.floor_id].elevation_m
    return abs(elevation_b - elevation_a)


def load_connections(seed: dict, scales: dict[int, float], floors: dict[int, Floor],
                     nodes: dict[int, Node], repository: ConnectionRepository) -> None:
    '''Saves the connections, with their waypoints and children.'''
    for item in seed["connections"]:
        node_a, node_b = nodes[item["from"]], nodes[item["to"]]
        scale = scales[node_a.coordinates.floor_id]
        row = {
            "id": item["id"], "type": item["type"],
            "node_a_id": item["from"], "node_b_id": item["to"], "status": item.get("status", 0),
            "rise_m": rise_of(item, floors, node_a, node_b),
            "wait_time_s": item.get("wait_time_s", 0),
        }
        waypoints = [(round(x * scale, 3), round(y * scale, 3))
                     for x, y in item.get("waypoints", [])]
        children = tuple((nodes[child["node"]], child["position"])
                         for child in item.get("children", []))
        repository.add(make_connection(row, nodes, waypoints, children))


def main() -> None:
    '''Recreates the database from the seed.'''
    seed = json.loads(SEED_PATH.read_text(encoding="utf-8"))
    scales = {floor["id"]: floor["meters_per_pixel"] for floor in seed["floors"]}
    DATABASE_PATH.unlink(missing_ok=True)
    database = Database(str(DATABASE_PATH))
    database.create_schema()
    floors = load_floors(seed, FloorRepository(database))
    nodes = load_nodes(seed, scales, NodeRepository(database))
    load_connections(seed, scales, floors, nodes, ConnectionRepository(database))
    database.close()
    print(f"{DATABASE_PATH.name}: {len(floors)} floors, {len(nodes)} nodes, "
          f"{len(seed['connections'])} connections")


if __name__ == "__main__":
    main()
