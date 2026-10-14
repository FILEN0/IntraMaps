from fastapi import APIRouter, Query

router = APIRouter(prefix="/api/v1/routing", tags=["routing"])


@router.get("/route")
def calcular_rota(
    origin_id: int = Query(..., description="ID do ponto de partida"),
    destination_id: int = Query(..., description="ID do destino"),
    no_stairs: bool = Query(False, description="True para evitar escadas"),
):
    # TODO: return route_service.calcular(origin_id, destination_id, no_stairs)
    return {"steps": [], "total_time_seconds": 0}


@router.get("/route/plot")
def imagem_rota(
    origin_id: int = Query(...),
    destination_id: int = Query(...),
    no_stairs: bool = Query(False),
):
    # TODO: return route_image_service.gerar_imagem(origin_id, destination_id, no_stairs)
    return {"image_url": "placeholder"}


@router.get("/route/gif")
def gif_rota(
    origin_id: int = Query(...),
    destination_id: int = Query(...),
    no_stairs: bool = Query(False),
):
    # TODO: return route_image_service.gerar_gif(origin_id, destination_id, no_stairs)
    return {"gif_url": "placeholder"}