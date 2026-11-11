'''Route routes.'''
from fastapi import APIRouter, Depends, HTTPException

from intramaps.api.dependencies import (find_place, get_auth_service, get_current_user,
                                        get_node_service, get_profile, get_route_service)
from intramaps.api.dtos import PLACE_TYPES, InstructionsDTO, PlaceTypeSlug, RouteDTO
from intramaps.routing.route import Route
from intramaps.services.auth_service import AuthService
from intramaps.services.node_service import NodeService
from intramaps.services.route_service import RouteService
from intramaps.users.user import User

router = APIRouter(prefix="/routes", tags=["routes"])


def _record(route: Route, user: User, auth: AuthService) -> Route:
    '''Records the route in the history of a logged-in user and gives the route back.'''
    if user.is_authenticated:
        auth.add_history(user.id, route.origin.id, route.destination.id)
    return route


def _find_route(routes: RouteService, origin_id: int, destination_id: int, user: User) -> Route:
    '''Finds the fastest route between two places, or answers with the error that fits.'''
    try:
        return routes.find_route(origin_id, destination_id, user)
    except PermissionError as error:
        raise HTTPException(status_code=401, detail="você não pode ir a esse destino") from error
    except LookupError as error:
        raise HTTPException(
            status_code=404, detail=f"não existe rota de {origin_id} para {destination_id}"
        ) from error


def route_to( # pylint: disable=too-many-arguments,too-many-positional-arguments
    origin_id: int,
    destination_id: int,
    user: User = Depends(get_profile),
    nodes: NodeService = Depends(get_node_service),
    routes: RouteService = Depends(get_route_service),
    auth: AuthService = Depends(get_auth_service),
) -> Route:
    '''Finds the fastest route between two places, and records it in the history.'''
    find_place(nodes, origin_id)
    find_place(nodes, destination_id)
    if origin_id == destination_id:
        raise HTTPException(status_code=400, detail="origem e destino são o mesmo lugar")
    return _record(_find_route(routes, origin_id, destination_id, user), user, auth)


def nearest_route( # pylint: disable=too-many-arguments,too-many-positional-arguments
    origin_id: int,
    place_type: PlaceTypeSlug,
    user: User = Depends(get_profile),
    nodes: NodeService = Depends(get_node_service),
    routes: RouteService = Depends(get_route_service),
    auth: AuthService = Depends(get_auth_service),
) -> Route:
    '''Finds the fastest route to the nearest place of a type, and records it in the history.'''
    find_place(nodes, origin_id)
    try:
        route = routes.find_nearest_route(origin_id, PLACE_TYPES[place_type], user)
    except LookupError as error:
        raise HTTPException(
            status_code=404,
            detail=f"nenhum lugar do tipo {place_type.value} alcançável a partir de {origin_id}",
        ) from error
    return _record(route, user, auth)


def history_route(
    history_id: int,
    user: User = Depends(get_current_user),
    routes: RouteService = Depends(get_route_service),
    auth: AuthService = Depends(get_auth_service),
) -> Route:
    '''Finds again the route of an item of the history, for the profile the user has now.'''
    item = auth.get_history_item(user.id, history_id)
    if item is None:
        raise HTTPException(
            status_code=404, detail=f"item {history_id} do histórico não encontrado"
        )
    return _find_route(routes, item["node_a_id"], item["node_b_id"], user)


@router.get("/{origin_id}/to/{destination_id}", response_model=RouteDTO)
def get_route(route: Route = Depends(route_to)):
    '''Returns the fastest route between two places.'''
    return RouteDTO.from_route(route)


@router.get("/{origin_id}/to/{destination_id}/instructions", response_model=InstructionsDTO)
def get_route_instructions(route: Route = Depends(route_to)):
    '''Returns the fastest route between two places, told in words.'''
    return InstructionsDTO.from_route(route)


@router.get("/{origin_id}/nearest/{place_type}", response_model=RouteDTO)
def get_nearest_route(route: Route = Depends(nearest_route)):
    '''Returns the fastest route from a place to the nearest place of a type.'''
    return RouteDTO.from_route(route)


@router.get("/{origin_id}/nearest/{place_type}/instructions", response_model=InstructionsDTO)
def get_nearest_instructions(route: Route = Depends(nearest_route)):
    '''Returns the fastest route from a place to the nearest place of a type, told in words.'''
    return InstructionsDTO.from_route(route)


@router.get("/history/{history_id}", response_model=RouteDTO)
def get_history_route(route: Route = Depends(history_route)):
    '''Returns the route of an item of the history, without recording it again.'''
    return RouteDTO.from_route(route)


@router.get("/history/{history_id}/instructions", response_model=InstructionsDTO)
def get_history_instructions(route: Route = Depends(history_route)):
    '''Returns the route of an item of the history, told in words, without recording it again.'''
    return InstructionsDTO.from_route(route)
