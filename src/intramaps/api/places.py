'''Place routes.'''
from fastapi import APIRouter, Depends, HTTPException, Query

from intramaps.api.dependencies import get_floor_service, get_node_service
from intramaps.api.dtos import PLACE_TYPES, PlaceDTO, PlaceTypeSlug
from intramaps.services.floor_service import FloorService
from intramaps.services.node_service import NodeService

router = APIRouter(prefix="/places", tags=["places"])


@router.get("", response_model=list[PlaceDTO])
def list_places(
    text: str | None = None,
    place_type: PlaceTypeSlug | None = Query(default=None, alias="type"),
    floor: int | None = None,
    nodes: NodeService = Depends(get_node_service),
    floors: FloorService = Depends(get_floor_service),
):
    '''Returns the places, filtered by text, type and floor. Every filter is optional.'''
    if floor is not None and not floors.exists(floor):
        raise HTTPException(status_code=400, detail=f"andar {floor} não existe")
    node_type = None if place_type is None else PLACE_TYPES[place_type]
    return [PlaceDTO.from_node(place) for place in nodes.find_places(text, node_type, floor)]


@router.get("/{place_id}", response_model=PlaceDTO)
def get_place(place_id: int, nodes: NodeService = Depends(get_node_service)):
    '''Returns one place.'''
    place = nodes.get_place(place_id)
    if place is None:
        raise HTTPException(status_code=404, detail=f"lugar {place_id} não encontrado")
    return PlaceDTO.from_node(place)
