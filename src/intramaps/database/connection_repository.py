'''ConnectionRepository class definition.'''
from collections import defaultdict
from intramaps.building.connections.connection import Connection
from intramaps.building.connections.corridor import Corridor
from intramaps.building.geometry.coordinates import Coordinates
from intramaps.building.nodes.node import Node
from intramaps.database.database import Database
from intramaps.enums.enum_building import EnumConnection, EnumStatus

class ConnectionRepository:
    '''Saves and loads connections.'''

    def __init__(self, conn: Database) -> None:
        self.__connection = conn

    def add(self, connection: Connection) -> None:
        '''Saves a connection with its waypoints and, when it has them, its children.

        The two ends and every child must already be saved in the nodes table.

        Args:
            connection: The connection to save.
        '''
        if not isinstance(connection, Connection):
            raise ValueError("connection must be an instance of Connection")
        self.__connection.execute(
            "INSERT INTO connections (id, type, node_a_id, node_b_id, status, accessible, rise_m, wait_time_s) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", # pylint: disable=line-too-long
            (connection.id, connection.type.value, connection.node_a.id, connection.node_b.id,
             connection.status.value, int(connection.accessible),
             getattr(connection, "rise_m", 0), getattr(connection, "wait_time_s", 0)),
        )
        for order, point in enumerate(connection.waypoints, start=1):
            self.__connection.execute(
                "INSERT INTO connection_waypoints (connection_id, waypoint_order, x, y) VALUES (?, ?, ?, ?)", # pylint: disable=line-too-long
                (connection.id, order, point.x, point.y),
            )
        for child, position in getattr(connection, "children", ()):
            self.__connection.execute(
                "INSERT INTO connection_children (node_id, connection_id, position) VALUES (?, ?, ?)", # pylint: disable=line-too-long
                (child.id, connection.id, position),
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
            "SELECT id, type, node_a_id, node_b_id, status, accessible FROM connections ORDER BY id"
        )
        for row in rows:
            if EnumConnection(row["type"]) != EnumConnection.CORRIDOR:
                raise ValueError("only corridors can be loaded for now")
            node_a = nodes[row["node_a_id"]]
            points = tuple(Coordinates(x, y, node_a.coordinates.floor_id)
                           for x, y in waypoints[row["id"]])
            corridors.append(Corridor(row["id"], node_a, nodes[row["node_b_id"]], points,
                                      tuple(children[row["id"]]), EnumStatus(row["status"]),
                                      bool(row["accessible"])))
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
