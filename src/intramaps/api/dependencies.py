'''FastAPI dependency functions.'''
from pathlib import Path

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from intramaps.database.connection_repository import ConnectionRepository
from intramaps.database.database import Database
from intramaps.database.node_repository import NodeRepository
from intramaps.database.user_repository import UserRepository
from intramaps.services.auth_service import AuthService
from intramaps.services.connection_service import ConnectionService
from intramaps.services.graph_service import GraphService
from intramaps.services.node_service import NodeService
from intramaps.services.route_service import RouteService
from intramaps.users.user import User

_DB: Database | None = None
_DB_PATH = Path(__file__).parent.parent.parent.parent / "data" / "intramaps.db"
_BEARER = HTTPBearer()
_OPTIONAL_BEARER = HTTPBearer(auto_error=False)


def get_db() -> Database:
    '''Returns the shared database connection, creating it on first call.'''
    global _DB  # pylint: disable=global-statement
    if _DB is None:
        _DB = Database(str(_DB_PATH))
        _DB.create_schema()
    return _DB


def get_node_repository(db: Database = Depends(get_db)) -> NodeRepository:
    '''Returns a NodeRepository backed by the shared database.'''
    return NodeRepository(db)


def get_connection_repository(db: Database = Depends(get_db)) -> ConnectionRepository:
    '''Returns a ConnectionRepository backed by the shared database.'''
    return ConnectionRepository(db)


def get_node_service(nodes: NodeRepository = Depends(get_node_repository)) -> NodeService:
    '''Returns a NodeService backed by the node repository.'''
    return NodeService(nodes)


def get_connection_service(
    connections: ConnectionRepository = Depends(get_connection_repository),
    nodes: NodeService = Depends(get_node_service),
) -> ConnectionService:
    '''Returns a ConnectionService backed by connection and node repositories.'''
    return ConnectionService(connections, nodes)


def get_graph_service(
    connections: ConnectionService = Depends(get_connection_service),
) -> GraphService:
    '''Returns a GraphService backed by the connection service.'''
    return GraphService(connections)


def get_route_service(
    nodes: NodeService = Depends(get_node_service),
    graph: GraphService = Depends(get_graph_service),
) -> RouteService:
    '''Returns a RouteService backed by the node and graph services.'''
    return RouteService(nodes, graph)


def get_user_repository(db: Database = Depends(get_db)) -> UserRepository:
    '''Returns a UserRepository backed by the shared database.'''
    return UserRepository(db)


def get_auth_service(
    users: UserRepository = Depends(get_user_repository),
) -> AuthService:
    '''Returns an AuthService backed by the user repository.'''
    return AuthService(users)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_BEARER),
    auth: AuthService = Depends(get_auth_service),
) -> User:
    '''Returns the logged-in user from the Authorization header.

    Raises:
        HTTPException 401: If the token is missing, invalid or expired.
    '''
    user = auth.get_user_from_token(credentials.credentials)
    if user is None:
        raise HTTPException(status_code=401, detail="token inválido ou expirado")
    return user


def get_current_token(
    credentials: HTTPAuthorizationCredentials = Depends(_BEARER),
    auth: AuthService = Depends(get_auth_service),
) -> str:
    '''Returns the raw token after confirming it is active.

    Raises:
        HTTPException 401: If the token is missing, invalid or expired.
    '''
    token = credentials.credentials
    if auth.get_user_from_token(token) is None:
        raise HTTPException(status_code=401, detail="token inválido ou expirado")
    return token


def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_OPTIONAL_BEARER),
    auth: AuthService = Depends(get_auth_service),
) -> User | None:
    '''Returns the logged-in user if a token is present, or None for anonymous requests.'''
    if credentials is None:
        return None
    return auth.get_user_from_token(credentials.credentials)
