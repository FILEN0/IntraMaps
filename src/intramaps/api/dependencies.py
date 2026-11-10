'''FastAPI dependency functions.'''
from pathlib import Path

from fastapi import Depends, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from intramaps.api.dtos import (ACCESSIBILITIES, GENDERS, ROLES, AccessibilitySlug, GenderSlug,
                                RoleSlug)
from intramaps.building.nodes.node import Node
from intramaps.database.connection_repository import ConnectionRepository
from intramaps.database.database import Database
from intramaps.database.floor_repository import FloorRepository
from intramaps.database.node_repository import NodeRepository
from intramaps.database.user_repository import UserRepository
from intramaps.services.auth_service import AuthService
from intramaps.services.connection_service import ConnectionService
from intramaps.services.floor_service import FloorService
from intramaps.services.graph_service import GraphService
from intramaps.services.node_service import NodeService
from intramaps.services.route_service import RouteService
from intramaps.users.anonymous import Anonymous
from intramaps.users.user import User

_DB: Database | None = None
DATA_DIR = Path(__file__).parent.parent.parent.parent / "data"
_DB_PATH = DATA_DIR / "intramaps.db"
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


def get_floor_service(db: Database = Depends(get_db)) -> FloorService:
    '''Returns a FloorService backed by the shared database.'''
    return FloorService(FloorRepository(db))


def get_node_service(db: Database = Depends(get_db)) -> NodeService:
    '''Returns a NodeService backed by the shared database.'''
    return NodeService(NodeRepository(db))


def get_route_service(db: Database = Depends(get_db),
                      nodes: NodeService = Depends(get_node_service)) -> RouteService:
    '''Returns a RouteService backed by the shared database.'''
    graph = GraphService(ConnectionService(ConnectionRepository(db), nodes))
    return RouteService(nodes, graph)


def find_place(nodes: NodeService, place_id: int) -> Node:
    '''Returns the place with this id, or answers 404 if there is none.'''
    place = nodes.get_place(place_id)
    if place is None:
        raise HTTPException(status_code=404, detail=f"lugar {place_id} não encontrado")
    return place


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


def get_profile( # pylint: disable=too-many-arguments,too-many-positional-arguments
    credentials: HTTPAuthorizationCredentials | None = Depends(_BEARER),
    auth: AuthService = Depends(get_auth_service),
    gender: GenderSlug = GenderSlug.NONE,
    accessibility: AccessibilitySlug = AccessibilitySlug.NONE,
    role: RoleSlug = RoleSlug.STUDENT,
    speed: float = Query(default=User.DEFAULT_SPEED, gt=0, le=User.MAX_SPEED),
) -> User:
    '''Returns the logged-in user, or an Anonymous with the profile of the query.'''
    if credentials is None:
        return Anonymous(GENDERS[gender], ACCESSIBILITIES[accessibility], ROLES[role], speed)
    return get_current_user(credentials, auth)


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
