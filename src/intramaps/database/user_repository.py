'''UserRepository class definition.'''
from intramaps.database.database import Database
from intramaps.users.user import User
from intramaps.enums.enum_user import EnumGender, EnumRole, EnumAccessibility


class UserRepository:
    '''Saves and loads users, sessions, favorites and history.'''

    def __init__(self, conn: Database) -> None:
        self.__connection = conn

    def add(self, username: str, password_hash: str, gender: EnumGender,
            role: EnumRole, accessibility: EnumAccessibility) -> int:
        '''Saves a new user in the users table.

        Args:
            username: Unique username.
            password_hash: Hashed password (never store plain text).
            gender: Gender of the user.
            role: Role of the user.
            accessibility: Accessibility needs of the user.

        Returns:
            The id of the new user.
        '''
        cursor = self.__connection.execute(
            "INSERT INTO users (username, password_hash, gender, role, accessibility)"
            " VALUES (?, ?, ?, ?, ?)",
            (username, password_hash, gender.value, role.value, accessibility.value),
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
            "SELECT id, username, gender, role, accessibility FROM users WHERE id = ?",
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
            "SELECT id, username, gender, role, accessibility FROM users WHERE username = ?",
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
            "UPDATE users SET gender = ?, accessibility = ? WHERE id = ?",
            (user.gender.value, user.accessibility.value, user.id),
        )
        if cursor.rowcount == 0:
            raise ValueError(f"user {user.id} not found")


    def add_session(self, token: str, user_id: int, expires_at: str) -> None:
        '''Saves a new session token.

        Args:
            token: The session token (JWT or UUID).
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
        '''Adds a node to the user\'s favorites.

        Args:
            user_id: The user.
            node_id: The node to favorite.
        '''
        self.__connection.execute(
            "INSERT OR IGNORE INTO favorites (user_id, node_id) VALUES (?, ?)",
            (user_id, node_id),
        )

    def remove_favorite(self, user_id: int, node_id: int) -> None:
        '''Removes a node from the user\'s favorites.

        Args:
            user_id: The user.
            node_id: The node to remove.
        '''
        self.__connection.execute(
            "DELETE FROM favorites WHERE user_id = ? AND node_id = ?",
            (user_id, node_id),
        )

    def list_favorites(self, user_id: int) -> list[int]:
        '''Returns the node ids of the user\'s favorites.

        Args:
            user_id: The user.

        Returns:
            List of node ids, ordered by id.
        '''
        rows = self.__connection.fetch(
            "SELECT node_id FROM favorites WHERE user_id = ? ORDER BY node_id",
            (user_id,),
        )
        return [row["node_id"] for row in rows]


    def add_history(self, user_id: int, node_a_id: int, node_b_id: int) -> None:
        '''Adds a route to the user\'s history.

        Args:
            user_id: The user.
            node_a_id: Origin node id.
            node_b_id: Destination node id.
        '''
        self.__connection.execute(
            "INSERT INTO history (user_id, node_a_id, node_b_id) VALUES (?, ?, ?)",
            (user_id, node_a_id, node_b_id),
        )

    def list_history(self, user_id: int) -> list[dict]:
        '''Returns the user\'s route history, newest first.

        Args:
            user_id: The user.

        Returns:
            List of dicts with node_a_id, node_b_id and created_at.
        '''
        rows = self.__connection.fetch(
            "SELECT node_a_id, node_b_id, created_at FROM history"
            " WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,),
        )
        return [
            {
                "node_a_id": row["node_a_id"],
                "node_b_id": row["node_b_id"],
                "created_at": row["created_at"],
            }
            for row in rows
        ]


    def __row_to_user(self, row) -> User:
        return User(
            user_id=row["id"],
            user_name=row["username"],
            user_gender=EnumGender(row["gender"]),
            user_accessibility=EnumAccessibility(row["accessibility"]),
            user_role=EnumRole(row["role"]),
        )