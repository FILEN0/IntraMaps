'''AuthService class definition.'''
import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from intramaps.database.user_repository import UserRepository
from intramaps.enums.enum_user import EnumGender, EnumRole, EnumAccessibility
from intramaps.users.user import User

_TOKEN_TTL_HOURS = 24


class AuthService:
    '''Handles user registration, authentication and account management.

    Args:
        users: The repository that stores users, sessions, favorites and history.
    '''

    def __init__(self, users: UserRepository) -> None:
        self.__users = users

    def register(self, username: str, password: str,
                 gender: EnumGender = EnumGender.NONE,
                 accessibility: EnumAccessibility = EnumAccessibility.NONE,
                 role: EnumRole = EnumRole.STUDENT,
                 speed: float = User.DEFAULT_SPEED) -> User:
        '''Creates a new user account.

        Args:
            username: Unique username.
            password: Plain-text password (hashed before storing).
            gender: Gender of the user.
            accessibility: Accessibility needs.
            role: Role of the user.
            speed: Walking speed in m/s.

        Returns:
            The new User object.

        Raises:
            ValueError: If the username is already taken.
        '''
        if self.__users.get_by_username(username) is not None:
            raise ValueError(f"username {username!r} already exists")
        user_id = self.__users.add(
            username, self.__hash(password), gender, role, accessibility, speed
        )
        return self.__users.get_by_id(user_id)

    def login(self, username: str, password: str) -> tuple[str, str, User]:
        '''Validates credentials and opens a session.

        Args:
            username: The username.
            password: Plain-text password.

        Returns:
            A tuple of (token, expires_at, user).

        Raises:
            PermissionError: If the credentials are wrong.
        '''
        stored_hash = self.__users.get_password_hash(username)
        if stored_hash is None or stored_hash != self.__hash(password):
            raise PermissionError("invalid username or password")
        user = self.__users.get_by_username(username)
        token = secrets.token_hex(32)
        expires_at = (
            datetime.now(timezone.utc) + timedelta(hours=_TOKEN_TTL_HOURS)
        ).isoformat()
        self.__users.add_session(token, user.id, expires_at)
        return token, expires_at, user

    def logout(self, token: str) -> None:
        '''Closes a session by deleting the token.

        Args:
            token: The session token to invalidate.
        '''
        self.__users.delete_session(token)

    def get_user_from_token(self, token: str) -> User | None:
        '''Returns the user for a valid, non-expired token.

        Args:
            token: The session token to look up.

        Returns:
            The User object, or None if the token is invalid or expired.
        '''
        session = self.__users.get_session(token)
        if session is None:
            return None
        expires_at = datetime.fromisoformat(session["expires_at"])
        if datetime.now(timezone.utc) > expires_at:
            self.__users.delete_session(token)
            return None
        return self.__users.get_by_id(session["user_id"])

    def update_user(self, user: User) -> None:
        '''Saves the updated user profile.

        Args:
            user: The user with the new values.
        '''
        self.__users.update(user)

    def delete_user(self, user_id: int) -> None:
        '''Deletes the user account and all related data.

        Args:
            user_id: The id of the user to delete.
        '''
        self.__users.delete(user_id)

    def add_favorite(self, user_id: int, node_id: int) -> None:
        '''Adds a place to the user's favorites.'''
        self.__users.add_favorite(user_id, node_id)

    def remove_favorite(self, user_id: int, node_id: int) -> None:
        '''Removes a place from the user's favorites.'''
        self.__users.remove_favorite(user_id, node_id)

    def list_favorites(self, user_id: int) -> list[int]:
        '''Returns the ids of the user's favorite places.'''
        return self.__users.list_favorites(user_id)

    def add_history(self, user_id: int, node_a_id: int, node_b_id: int) -> None:
        '''Records a route in the user's history.'''
        self.__users.add_history(user_id, node_a_id, node_b_id)

    def list_history(self, user_id: int) -> list[dict]:
        '''Returns the user's route history, newest first.'''
        return self.__users.list_history(user_id)

    def delete_history_item(self, user_id: int, history_id: int) -> bool:
        '''Deletes one history entry. Returns True if deleted, False if not found.'''
        return self.__users.delete_history_item(user_id, history_id)

    def clear_history(self, user_id: int) -> None:
        '''Deletes all history entries for the user.'''
        self.__users.clear_history(user_id)

    @staticmethod
    def __hash(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()