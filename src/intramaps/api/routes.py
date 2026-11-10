'''Route routes.'''
from fastapi import APIRouter, Depends, HTTPException

from intramaps.api.dependencies import (find_place, get_auth_service, get_node_service, get_profile,
                                        get_route_service)
from intramaps.api.dtos import PLACE_TYPES, PlaceTypeSlug, RouteDTO
from intramaps.routing.route import Route
from intramaps.services.auth_service import AuthService
from intramaps.services.node_service import NodeService
from intramaps.services.route_service import RouteService
from intramaps.users.user import User

router = APIRouter(prefix="/routes", tags=["routes"])


def _answer(route: Route, user: User, auth: AuthService) -> RouteDTO:
    '''Records the route in the history of a logged-in user and builds the response.'''
    if user.is_authenticated:
        auth.add_history(user.id, route.origin.id, route.destination.id)
    return RouteDTO.from_route(route)


@router.get("/{origin_id}/to/{destination_id}", response_model=RouteDTO)
def get_route( # pylint: disable=too-many-arguments,too-many-positional-arguments
    origin_id: int,
    destination_id: int,
    user: User = Depends(get_profile),
    nodes: NodeService = Depends(get_node_service),
    routes: RouteService = Depends(get_route_service),
    auth: AuthService = Depends(get_auth_service),
):
    '''Finds the fastest route between two places.'''
    find_place(nodes, origin_id)
    find_place(nodes, destination_id)
    if origin_id == destination_id:
        raise HTTPException(status_code=400, detail="origem e destino são o mesmo lugar")
    try:
        route = routes.find_route(origin_id, destination_id, user)
    except PermissionError as error:
        raise HTTPException(status_code=401, detail="você não pode ir a esse destino") from error
    except LookupError as error:
        raise HTTPException(
            status_code=404, detail=f"não existe rota de {origin_id} para {destination_id}"
        ) from error
    return _answer(route, user, auth)


@router.get("/{origin_id}/nearest/{place_type}", response_model=RouteDTO)
def get_nearest_route( # pylint: disable=too-many-arguments,too-many-positional-arguments
    origin_id: int,
    place_type: PlaceTypeSlug,
    user: User = Depends(get_profile),
    nodes: NodeService = Depends(get_node_service),
    routes: RouteService = Depends(get_route_service),
    auth: AuthService = Depends(get_auth_service),
):
    '''Finds the fastest route from a place to the nearest place of a type.'''
    find_place(nodes, origin_id)
    try:
        route = routes.find_nearest_route(origin_id, PLACE_TYPES[place_type], user)
    except LookupError as error:
        raise HTTPException(
            status_code=404,
            detail=f"nenhum lugar do tipo {place_type.value} alcançável a partir de {origin_id}",
        ) from error
    return _answer(route, user, auth)
