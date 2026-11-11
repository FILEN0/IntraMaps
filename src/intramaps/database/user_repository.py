'''UserRepository class definition.'''
from intramaps.database.database import Database
from intramaps.users.user import User
from intramaps.enums.enum_user import EnumGender, EnumRole, EnumAccessibility


class UserRepository:
    '''Saves and loads users, sessions, favorites and history.'''

    def __init__(self, conn: Database) -> None:
        self.__connection = conn

    def add(self, username: str, password_hash: str, gender: EnumGender,  # pylint: disable=too-many-arguments,too-many-positional-arguments
            role: EnumRole, accessibility: EnumAccessibility,
            speed: float = User.DEFAULT_SPEED) -> int:
        '''Saves a new user in the users table.

        Args:
            username: Unique username.
            password_hash: Hashed password (never store plain text).
            gender: Gender of the user.
            role: Role of the user.
            accessibility: Accessibility needs of the user.
            speed: Walking speed in m/s.

        Returns:
            The id of the new user.
        '''
        cursor = self.__connection.execute(
            "INSERT INTO users (username, password_hash, gender, role, accessibility, speed)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (username, password_hash, gender.value, role.value, accessibility.value, speed),
        )
        return cursor.lastrowid

    def get_by_id(self, user_id: int) -> User | None:
        '''Loads a user by id.

        Args:
            user_id: The user id.

        Returns:
            The User object, or None if not found.
        '''
        rows = self.__connection.fetch(
            "SELECT id, username, gender, role, accessibility, speed FROM users WHERE id = ?",
            (user_id,),
            count=1,
        )
        return self.__row_to_user(rows[0]) if rows else None

    def get_by_username(self, username: str) -> User | None:
        '''Loads a user by username.

        Args:
            username: The username to look up.

        Returns:
            The User object, or None if not found.
        '''
        rows = self.__connection.fetch(
            "SELECT id, username, gender, role, accessibility, speed FROM users WHERE username = ?",
            (username,),
            count=1,
        )
        return self.__row_to_user(rows[0]) if rows else None

    def get_password_hash(self, username: str) -> str | None:
        '''Returns the stored password hash for a given username.

        Args:
            username: The username to look up.

        Returns:
            The password hash string, or None if the username does not exist.
        '''
        rows = self.__connection.fetch(
            "SELECT password_hash FROM users WHERE username = ?",
            (username,),
            count=1,
        )
        return rows[0]["password_hash"] if rows else None

    def update(self, user: User) -> None:
        '''Overwrites the saved user that has the same id.

        Args:
            user: The user with the new values.
        '''
        cursor = self.__connection.execute(
            "UPDATE users SET gender = ?, accessibility = ?, role = ?, speed = ? WHERE id = ?",
            (user.gender.value, user.accessibility.value, user.role.value, user.speed, user.id),
        )
        if cursor.rowcount == 0:
            raise ValueError(f"user {user.id} not found")

    def delete(self, user_id: int) -> None:
        '''Deletes a user and all their data (sessions, favorites and history cascade).

        Args:
            user_id: The id of the user to delete.
        '''
        self.__connection.execute(
            "DELETE FROM users WHERE id = ?",
            (user_id,),
        )

    def add_session(self, token: str, user_id: int, expires_at: str) -> None:
        '''Saves a new session token.

        Args:
            token: The session token.
            user_id: The user this session belongs to.
            expires_at: ISO 8601 expiry datetime string.
        '''
        self.__connection.execute(
            "INSERT INTO sessions (token, user_id, expires_at) VALUES (?, ?, ?)",
            (token, user_id, expires_at),
        )

    def get_session(self, token: str) -> dict | None:
        '''Loads a session by token.

        Args:
            token: The session token to look up.

        Returns:
            Dict with token, user_id and expires_at, or None if not found.
        '''
        rows = self.__connection.fetch(
            "SELECT token, user_id, expires_at FROM sessions WHERE token = ?",
            (token,),
            count=1,
        )
        if not rows:
            return None
        return {
            "token": rows[0]["token"],
            "user_id": rows[0]["user_id"],
            "expires_at": rows[0]["expires_at"],
        }

    def delete_session(self, token: str) -> None:
        '''Deletes a session token (logout).

        Args:
            token: The token to delete.
        '''
        self.__connection.execute(
            "DELETE FROM sessions WHERE token = ?",
            (token,),
        )

    def add_favorite(self, user_id: int, node_id: int) -> None:
        '''Adds a node to the user's favorites.

        Args:
            user_id: The user.
            node_id: The node to favorite.
        '''
        self.__connection.execute(
            "INSERT OR IGNORE INTO favorites (user_id, node_id) VALUES (?, ?)",
            (user_id, node_id),
        )

    def remove_favorite(self, user_id: int, node_id: int) -> None:
        '''Removes a node from the user's favorites.

        Args:
            user_id: The user.
            node_id: The node to remove.
        '''
        self.__connection.execute(
            "DELETE FROM favorites WHERE user_id = ? AND node_id = ?",
            (user_id, node_id),
        )

    def list_favorites(self, user_id: int) -> list[int]:
        '''Returns the node ids of the user's favorites, ordered by id.

        Args:
            user_id: The user.

        Returns:
            List of node ids.
        '''
        rows = self.__connection.fetch(
            "SELECT node_id FROM favorites WHERE user_id = ? ORDER BY node_id",
            (user_id,),
        )
        return [row["node_id"] for row in rows]

    def add_history(self, user_id: int, node_a_id: int, node_b_id: int) -> None:
        '''Adds a route to the history, unless it repeats the latest entry.

        Args:
            user_id: The user.
            node_a_id: Origin node id.
            node_b_id: Destination node id.
        '''
        last = self.__connection.fetch(
            "SELECT node_a_id, node_b_id FROM history"
            " WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,),
            count=1,
        )
        if last and last[0]["node_a_id"] == node_a_id and last[0]["node_b_id"] == node_b_id:
            return
        self.__connection.execute(
            "INSERT INTO history (user_id, node_a_id, node_b_id) VALUES (?, ?, ?)",
            (user_id, node_a_id, node_b_id),
        )

    def list_history(self, user_id: int) -> list[dict]:
        '''Returns the user's route history, newest first.

        Args:
            user_id: The user.

        Returns:
            List of dicts with id, node_a_id, node_b_id and created_at.
        '''
        rows = self.__connection.fetch(
            "SELECT id, node_a_id, node_b_id, created_at FROM history"
            " WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,),
        )
        return [
            {
                "id": row["id"],
                "node_a_id": row["node_a_id"],
                "node_b_id": row["node_b_id"],
                "created_at": row["created_at"],
            }
            for row in rows
        ]

    def get_history_item(self, user_id: int, history_id: int) -> dict | None:
        '''Returns one history entry by id for a given user.

        Args:
            user_id: The user (prevents accessing another person's history).
            history_id: The history entry id.

        Returns:
            Dict with id, node_a_id, node_b_id and created_at, or None if not found.
        '''
        rows = self.__connection.fetch(
            "SELECT id, node_a_id, node_b_id, created_at FROM history"
            " WHERE id = ? AND user_id = ?",
            (history_id, user_id),
            count=1,
        )
        if not rows:
            return None
        return {
            "id": rows[0]["id"],
            "node_a_id": rows[0]["node_a_id"],
            "node_b_id": rows[0]["node_b_id"],
            "created_at": rows[0]["created_at"],
        }

    def delete_history_item(self, user_id: int, history_id: int) -> bool:
        '''Deletes one history entry belonging to the user.

        Args:
            user_id: The user (prevents deleting another person's entry).
            history_id: The history entry id.

        Returns:
            True if deleted, False if not found.
        '''
        cursor = self.__connection.execute(
            "DELETE FROM history WHERE id = ? AND user_id = ?",
            (history_id, user_id),
        )
        return cursor.rowcount > 0

    def clear_history(self, user_id: int) -> None:
        '''Deletes all history entries for a user.

        Args:
            user_id: The user.
        '''
        self.__connection.execute(
            "DELETE FROM history WHERE user_id = ?",
            (user_id,),
        )

    def __row_to_user(self, row) -> User:
        return User(
            user_id=row["id"],
            user_name=row["username"],
            user_gender=EnumGender(row["gender"]),
            user_accessibility=EnumAccessibility(row["accessibility"]),
            user_role=EnumRole(row["role"]),
            user_speed=row["speed"],
        )
    