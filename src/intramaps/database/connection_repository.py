'''ConnectionRepository class definition.'''
from collections import defaultdict
from intramaps.building.connections.corridor import Corridor
from intramaps.building.geometry.coordinates import Coordinates
from intramaps.building.nodes.node import Node
from intramaps.database.database import Database
from intramaps.enums.enum_building import EnumConnection, EnumStatus

class ConnectionRepository:
    '''Saves and loads connections.'''

    def __init__(self, conn: Database) -> None:
        self.__connection = conn

    def add(self, corridor: Corridor) -> None:
        '''Saves a corridor with its waypoints and children.

        The two ends and every child must already be saved in the nodes table.

        Args:
            corridor: The corridor to save.
        '''
        if not isinstance(corridor, Corridor):
            raise ValueError("only corridors can be saved for now")
        self.__connection.execute(
            "INSERT INTO connections (id, type, node_a_id, node_b_id, status, accessible) VALUES (?, ?, ?, ?, ?, 1)", # pylint: disable=line-too-long
            (corridor.id, corridor.type.value, corridor.node_a.id, corridor.node_b.id,
             corridor.status.value),
        )
        for order, point in enumerate(corridor.waypoints, start=1):
            self.__connection.execute(
                "INSERT INTO connection_waypoints (connection_id, waypoint_order, x, y) VALUES (?, ?, ?, ?)", # pylint: disable=line-too-long
                (corridor.id, order, point.x, point.y),
            )
        for child, position in corridor.children:
            self.__connection.execute(
                "INSERT INTO connection_children (node_id, connection_id, position) VALUES (?, ?, ?)", # pylint: disable=line-too-long
                (child.id, corridor.id, position),
            )

    def list_all(self, nodes: dict[int, Node]) -> list[Corridor]:
        '''Loads every connection, ordered by id.

        Args:
            nodes: The saved nodes by id, used as the ends and children of the connections.

        Returns:
            The corridors as objects, with their ends, waypoints and children.
        '''
        waypoints = self.__load_waypoints()
        children = self.__load_children(nodes)
        corridors = []
        rows = self.__connection.fetch(
            "SELECT id, type, node_a_id, node_b_id, status FROM connections ORDER BY id"
        )
        for row in rows:
            if EnumConnection(row["type"]) != EnumConnection.CORRIDOR:
                raise ValueError("only corridors can be loaded for now")
            node_a = nodes[row["node_a_id"]]
            points = tuple(Coordinates(x, y, node_a.coordinates.floor_id)
                           for x, y in waypoints[row["id"]])
            corridors.append(Corridor(row["id"], node_a, nodes[row["node_b_id"]], points,
                                      tuple(children[row["id"]]), EnumStatus(row["status"])))
        return corridors

    def __load_waypoints(self) -> dict:
        '''Returns the (x, y) points of every connection, in order, by connection id.'''
        waypoints = defaultdict(list)
        rows = self.__connection.fetch(
            "SELECT connection_id, x, y FROM connection_waypoints ORDER BY connection_id, waypoint_order" # pylint: disable=line-too-long
        )
        for row in rows:
            waypoints[row["connection_id"]].append((row["x"], row["y"]))
        return waypoints

    def __load_children(self, nodes: dict) -> dict:
        '''Returns the (node, position) pairs of every connection, by connection id.'''
        children = defaultdict(list)
        rows = self.__connection.fetch(
            "SELECT node_id, connection_id, position FROM connection_children ORDER BY connection_id, position" # pylint: disable=line-too-long
        )
        for row in rows:
            children[row["connection_id"]].append((nodes[row["node_id"]], row["position"]))
        return children
