'''Route endpoints.'''
from fastapi import APIRouter, Depends, HTTPException, Query

from intramaps.api.dependencies import (
    get_auth_service, get_current_user, get_optional_user, get_route_service,
)
from intramaps.api.dtos import (
    NODE_TYPE_MAP, AccessibilitySlug, GenderSlug, NodeTypeSlug, RoleSlug,
    instructions_dto, make_guest_user, route_dto,
)
from intramaps.services.auth_service import AuthService
from intramaps.services.route_service import RouteService
from intramaps.users.user import User

router = APIRouter(prefix="/routes", tags=["routes"])



def _resolve_user(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    optional_user: User | None,
    gender: GenderSlug,
    accessibility: AccessibilitySlug,
    role: RoleSlug,
    speed: float,
) -> User:
    '''Returns the logged-in user or builds a guest user from query params.'''
    return optional_user or make_guest_user(gender, accessibility, role, speed)


def _handle_errors(origin_id: int, destination_id: int, error: Exception) -> None:  # pylint: disable=too-many-branches
    '''Converts service exceptions to HTTPExceptions.'''
    msg = str(error)
    if isinstance(error, ValueError):
        raise HTTPException(status_code=422, detail="origem e destino são o mesmo lugar")
    if isinstance(error, PermissionError):
        if "destination" in msg:
            raise HTTPException(status_code=401, detail="o destino exige um papel maior que o seu")
        raise HTTPException(status_code=401, detail="a origem exige um papel maior que o seu")
    if isinstance(error, LookupError):
        node_id = origin_id if str(origin_id) in msg else destination_id
        raise HTTPException(status_code=404, detail=f"lugar {node_id} não encontrado")
    raise HTTPException(
        status_code=404,
        detail=f"não existe rota de {origin_id} para {destination_id} para o seu perfil",
    )



@router.get("/history/{history_id}")
def get_history_route(
    history_id: int,
    user: User = Depends(get_current_user),
    auth: AuthService = Depends(get_auth_service),
    route_service: RouteService = Depends(get_route_service),
):
    '''Returns a past route from the user's history, recalculated with the current profile.'''
    item = auth.get_history_item(user.id, history_id)
    if item is None:
        raise HTTPException(
            status_code=404, detail=f"item {history_id} do histórico não encontrado"
        )
    try:
        return route_dto(route_service.find_route(item["node_a_id"], item["node_b_id"], user))
    except Exception as e:  # pylint: disable=broad-except
        _handle_errors(item["node_a_id"], item["node_b_id"], e)


@router.get("/history/{history_id}/instructions")
def get_history_instructions(
    history_id: int,
    user: User = Depends(get_current_user),
    auth: AuthService = Depends(get_auth_service),
    route_service: RouteService = Depends(get_route_service),
):
    '''Returns instructions for a past route from the user's history.'''
    item = auth.get_history_item(user.id, history_id)
    if item is None:
        raise HTTPException(
            status_code=404, detail=f"item {history_id} do histórico não encontrado"
        )
    try:
        return instructions_dto(
            route_service.find_route(item["node_a_id"], item["node_b_id"], user)
        )
    except Exception as e:  # pylint: disable=broad-except
        _handle_errors(item["node_a_id"], item["node_b_id"], e)


@router.get("/history/{history_id}/plot")
def get_history_plot(history_id: int, scale: int = Query(1)):
    '''Returns an image of a past route. Not implemented yet.'''
    raise HTTPException(status_code=501, detail="não implementado ainda")


@router.get("/history/{history_id}/plot/{floor_id}")
def get_history_plot_floor(history_id: int, floor_id: int, scale: int = Query(1)):
    '''Returns an image of a past route for one floor. Not implemented yet.'''
    raise HTTPException(status_code=501, detail="não implementado ainda")


@router.get("/history/{history_id}/gif")
def get_history_gif(history_id: int, scale: int = Query(1)):
    '''Returns a GIF of a past route. Not implemented yet.'''
    raise HTTPException(status_code=501, detail="não implementado ainda")



@router.get("/{a}/to/{b}")
def get_route(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    a: int, b: int,
    gender: GenderSlug = Query(GenderSlug.NONE),
    accessibility: AccessibilitySlug = Query(AccessibilitySlug.NONE),
    role: RoleSlug = Query(RoleSlug.STUDENT),
    speed: float = Query(User.DEFAULT_SPEED, gt=0),
    optional_user: User | None = Depends(get_optional_user),
    route_service: RouteService = Depends(get_route_service),
    auth: AuthService = Depends(get_auth_service),
):
    '''Returns the fastest route between two places.'''
    user = _resolve_user(optional_user, gender, accessibility, role, speed)
    try:
        route = route_service.find_route(a, b, user)
        if optional_user is not None:
            auth.add_history(optional_user.id, a, b)
        return route_dto(route)
    except Exception as e:  # pylint: disable=broad-except
        _handle_errors(a, b, e)


@router.get("/{a}/to/{b}/instructions")
def get_route_instructions(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    a: int, b: int,
    gender: GenderSlug = Query(GenderSlug.NONE),
    accessibility: AccessibilitySlug = Query(AccessibilitySlug.NONE),
    role: RoleSlug = Query(RoleSlug.STUDENT),
    speed: float = Query(User.DEFAULT_SPEED, gt=0),
    optional_user: User | None = Depends(get_optional_user),
    route_service: RouteService = Depends(get_route_service),
    auth: AuthService = Depends(get_auth_service),
):
    '''Returns step-by-step instructions for the route between two places.'''
    user = _resolve_user(optional_user, gender, accessibility, role, speed)
    try:
        route = route_service.find_route(a, b, user)
        if optional_user is not None:
            auth.add_history(optional_user.id, a, b)
        return instructions_dto(route)
    except Exception as e:  # pylint: disable=broad-except
        _handle_errors(a, b, e)


@router.get("/{a}/to/{b}/plot")
def get_route_plot(a: int, b: int, scale: int = Query(1)):
    '''Returns an image of the route. Not implemented yet.'''
    raise HTTPException(status_code=501, detail="não implementado ainda")


@router.get("/{a}/to/{b}/plot/{floor_id}")
def get_route_plot_floor(a: int, b: int, floor_id: int, scale: int = Query(1)):
    '''Returns an image of the route for one floor. Not implemented yet.'''
    raise HTTPException(status_code=501, detail="não implementado ainda")


@router.get("/{a}/to/{b}/gif")
def get_route_gif(a: int, b: int, scale: int = Query(1)):
    '''Returns a GIF of the route. Not implemented yet.'''
    raise HTTPException(status_code=501, detail="não implementado ainda")



@router.get("/{origin}/nearest/{node_type}")
def get_nearest(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    origin: int, node_type: NodeTypeSlug,
    gender: GenderSlug = Query(GenderSlug.NONE),
    accessibility: AccessibilitySlug = Query(AccessibilitySlug.NONE),
    role: RoleSlug = Query(RoleSlug.STUDENT),
    speed: float = Query(User.DEFAULT_SPEED, gt=0),
    optional_user: User | None = Depends(get_optional_user),
    route_service: RouteService = Depends(get_route_service),
    auth: AuthService = Depends(get_auth_service),
):
    '''Returns the fastest route to the nearest place of a given type.'''
    user = _resolve_user(optional_user, gender, accessibility, role, speed)
    try:
        route = route_service.find_nearest_route(origin, NODE_TYPE_MAP[node_type], user)
        if optional_user is not None:
            auth.add_history(optional_user.id, origin, route.destination.id)
        return route_dto(route)
    except LookupError:
        raise HTTPException(
            status_code=404,
            detail=f"nenhum lugar do tipo {node_type.value} alcançável a partir de {origin}",
        )
    except Exception as e:  # pylint: disable=broad-except
        _handle_errors(origin, origin, e)


@router.get("/{origin}/nearest/{node_type}/instructions")
def get_nearest_instructions(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    origin: int, node_type: NodeTypeSlug,
    gender: GenderSlug = Query(GenderSlug.NONE),
    accessibility: AccessibilitySlug = Query(AccessibilitySlug.NONE),
    role: RoleSlug = Query(RoleSlug.STUDENT),
    speed: float = Query(User.DEFAULT_SPEED, gt=0),
    optional_user: User | None = Depends(get_optional_user),
    route_service: RouteService = Depends(get_route_service),
    auth: AuthService = Depends(get_auth_service),
):
    '''Returns instructions for the route to the nearest place of a given type.'''
    user = _resolve_user(optional_user, gender, accessibility, role, speed)
    try:
        route = route_service.find_nearest_route(origin, NODE_TYPE_MAP[node_type], user)
        if optional_user is not None:
            auth.add_history(optional_user.id, origin, route.destination.id)
        return instructions_dto(route)
    except LookupError:
        raise HTTPException(
            status_code=404,
            detail=f"nenhum lugar do tipo {node_type.value} alcançável a partir de {origin}",
        )
    except Exception as e:  # pylint: disable=broad-except
        _handle_errors(origin, origin, e)


@router.get("/{origin}/nearest/{node_type}/plot")
def get_nearest_plot(origin: int, node_type: NodeTypeSlug, scale: int = Query(1)):
    '''Returns an image of the route to the nearest place. Not implemented yet.'''
    raise HTTPException(status_code=501, detail="não implementado ainda")


@router.get("/{origin}/nearest/{node_type}/plot/{floor_id}")
def get_nearest_plot_floor(
    origin: int, node_type: NodeTypeSlug, floor_id: int, scale: int = Query(1)
):
    '''Returns an image of the route to the nearest place for one floor. Not implemented yet.'''
    raise HTTPException(status_code=501, detail="não implementado ainda")


@router.get("/{origin}/nearest/{node_type}/gif")
def get_nearest_gif(origin: int, node_type: NodeTypeSlug, scale: int = Query(1)):
    '''Returns a GIF of the route to the nearest place. Not implemented yet.'''
    raise HTTPException(status_code=501, detail="não implementado ainda")
