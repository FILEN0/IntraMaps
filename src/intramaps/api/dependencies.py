'''FastAPI dependency functions.'''
from pathlib import Path

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from intramaps.database.database import Database
from intramaps.database.user_repository import UserRepository
from intramaps.services.auth_service import AuthService
from intramaps.users.user import User

_DB: Database | None = None
_DB_PATH = Path(__file__).parent.parent.parent.parent / "data" / "intramaps.db"
_BEARER = HTTPBearer(auto_error=False)


def get_db() -> Database:
    '''Returns the shared database connection, creating it on first call.'''
    global _DB  # pylint: disable=global-statement
    if _DB is None:
        _DB = Database(str(_DB_PATH))
        _DB.create_schema()
    return _DB


def get_user_repository(db: Database = Depends(get_db)) -> UserRepository:
    '''Returns a UserRepository backed by the shared database.'''
    return UserRepository(db)


def get_auth_service(
    users: UserRepository = Depends(get_user_repository),
) -> AuthService:
    '''Returns an AuthService backed by the user repository.'''
    return AuthService(users)


def _token_from(credentials: HTTPAuthorizationCredentials | None) -> str:
    '''Returns the token from the Authorization header, or answers 401 if there is none.'''
    if credentials is None:
        raise HTTPException(status_code=401, detail="autenticação necessária")
    return credentials.credentials


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_BEARER),
    auth: AuthService = Depends(get_auth_service),
) -> User:
    '''Returns the logged-in user from the Authorization header.

    Raises:
        HTTPException 401: If the token is missing, invalid or expired.
    '''
    user = auth.get_user_from_token(_token_from(credentials))
    if user is None:
        raise HTTPException(status_code=401, detail="token inválido ou expirado")
    return user


def get_current_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(_BEARER),
    auth: AuthService = Depends(get_auth_service),
) -> str:
    '''Returns the raw token after confirming it is active.

    Raises:
        HTTPException 401: If the token is missing, invalid or expired.
    '''
    token = _token_from(credentials)
    if auth.get_user_from_token(token) is None:
        raise HTTPException(status_code=401, detail="token inválido ou expirado")
    return token
