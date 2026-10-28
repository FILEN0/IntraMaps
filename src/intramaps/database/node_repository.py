'''NodeRepository class definition.'''
from intramaps.database.database import Database
from intramaps.building.nodes.node import Node
from intramaps.enums.enum_building import EnumNode
from intramaps.enums.enum_user import EnumGender
from intramaps.building.factory import make_node
class NodeRepository:
    '''Saves and loads nodes.'''

    def __init__(self, conn: Database) -> None:
        self.__connection = conn

    def add(self, node) -> None:
        '''Saves a node in the nodes table.

        Args:
            node: The node to save. Its name, number, facing, gender restriction and opening
                hours are saved if the class has them.
        '''

        hours = getattr(node, "opening_hours", None)
        values = (
            node.id,
            node.coordinates.floor_id,
            getattr(node, "name", None),
            getattr(node, "number", None),
            node.type.value,
            node.coordinates.x,
            node.coordinates.y,
            getattr(node, "facing", None),
            getattr(node, "gender_restriction", EnumGender.NONE).value,
            node.role_restriction.value,
            node.status.value,
            None if hours is None else hours.opens_at.strftime("%H:%M"),
            None if hours is None else hours.closes_at.strftime("%H:%M"),
        )

        self.__connection.execute(
            "INSERT INTO nodes (id, floor_id, name, number, type, x, y, facing, gender_restriction, role_restriction, status, opens_at, closes_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", # pylint: disable=line-too-long
            values
        )

    def list_all(self, floor_id: int | None = None,
                 node_type: EnumNode | None = None) -> list[Node]:
        '''Loads the nodes, ordered by id.

        Args:
            floor_id: If given, only the nodes of this floor.
            node_type: If given, only the nodes of this type.

        Returns:
            The nodes as objects (Room, PseudoNode...).
        '''

        conditions = []
        params = []

        if floor_id is not None:
            conditions.append("floor_id = ?")
            params.append(floor_id)

        if node_type is not None:
            conditions.append("type = ?")
            params.append(node_type.value)

        where = " WHERE " + " AND ".join(conditions) if conditions else ""

        rows = self.__connection.fetch(
            "SELECT id, floor_id, name, number, type, x, y, facing, gender_restriction, role_restriction, status, opens_at, closes_at FROM nodes" + where + " ORDER BY id", # pylint: disable=line-too-long
            tuple(params),
        )

        return [make_node(row) for row in rows]

    def update(self, node: Node) -> None:
        '''Overwrites the saved node that has the same id.

        Args:
            node: The node with the new values.
        '''
        values = (
            node.coordinates.floor_id,
            getattr(node, "name", None),
            getattr(node, "number", None),
            node.type.value,
            node.coordinates.x,
            node.coordinates.y,
            getattr(node, "facing", None),
            node.id,
        )
        cursor = self.__connection.execute(
            "UPDATE nodes SET floor_id = ?, name = ?, number = ?, type = ?, x = ?, y = ?, facing = ? WHERE id = ?", # pylint: disable=line-too-long
            values,
        )
        if cursor.rowcount == 0:
            raise ValueError(f"node {node.id} not found")
