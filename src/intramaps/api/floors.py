'''Floor routes.'''
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse

from intramaps.api.dependencies import DATA_DIR, get_floor_service
from intramaps.api.dtos import FloorDTO
from intramaps.building.floor import Floor
from intramaps.building.floor_plan import FloorPlan
from intramaps.services.floor_service import FloorService

router = APIRouter(prefix="/floors", tags=["floors"])


def _floor_dto(floor: Floor, plan: FloorPlan, request: Request) -> FloorDTO:
    return FloorDTO(
        id=floor.id, level=floor.level, building=floor.building, elevation_m=floor.elevation_m,
        width_px=plan.width_px, height_px=plan.height_px,
        meters_per_pixel=plan.meters_per_pixel,
        plan_url=str(request.url_for("get_floor_plan", floor_id=floor.id)),
    )


@router.get("", response_model=list[FloorDTO])
def list_floors(request: Request, floors: FloorService = Depends(get_floor_service)):
    '''Returns every floor with the size and the scale of its plan.'''
    return [_floor_dto(floor, plan, request) for floor, plan in floors.list_floors()]


@router.get("/{floor_id}/plan", response_class=FileResponse)
def get_floor_plan(floor_id: int, floors: FloorService = Depends(get_floor_service)):
    '''Returns the image of the plan of a floor.'''
    plan = floors.get_plan(floor_id)
    if plan is None:
        raise HTTPException(status_code=404, detail=f"andar {floor_id} não existe")
    return FileResponse(DATA_DIR / plan.image_path, media_type="image/png")
