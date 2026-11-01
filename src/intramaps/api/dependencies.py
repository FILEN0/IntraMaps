'''FastAPI dependency functions.'''
from pathlib import Path

from fastapi import Depends, Header, HTTPException

from intramaps.database.database import Database
from intramaps.database.user_repository import UserRepository
from intramaps.services.auth_service import AuthService
from intramaps.users.user import User

_db: Database | None = None
_DB_PATH = Path(__file__).parent.parent.parent.parent / "data" / "intramaps.db"


def get_db() -> Database:
    '''Returns the shared database connection, creating it on first call.'''
    global _db
    if _db is None:
        _db = Database(str(_DB_PATH))
        _db.create_schema()
    return _db


def get_user_repository(db: Database = Depends(get_db)) -> UserRepository:
    '''Returns a UserRepository backed by the shared database.'''
    return UserRepository(db)


def get_auth_service(
    users: UserRepository = Depends(get_user_repository),
) -> AuthService:
    '''Returns an AuthService backed by the user repository.'''
    return AuthService(users)


def get_current_user(
    authorization: str = Header(...),
    auth: AuthService = Depends(get_auth_service),
) -> User:
    '''Returns the logged-in user from the Authorization header.

    Raises:
        HTTPException 401: If the token is missing, invalid or expired.
    '''
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="autenticação necessária")
    token = authorization.removeprefix("Bearer ")
    user = auth.get_user_from_token(token)
    if user is None:
        raise HTTPException(status_code=401, detail="token inválido ou expirado")
    return user


def get_current_token(
    authorization: str = Header(...),
    auth: AuthService = Depends(get_auth_service),
) -> str:
    '''Returns the raw token after confirming it is active.

    Raises:
        HTTPException 401: If the token is missing, invalid or expired.
    '''
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="autenticação necessária")
    token = authorization.removeprefix("Bearer ")
    if auth.get_user_from_token(token) is None:
        raise HTTPException(status_code=401, detail="token inválido ou expirado")
    return token