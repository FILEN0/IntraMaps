from fastapi import APIRouter, Query

router = APIRouter(prefix="/api/v1/finder", tags=["finder"])


@router.get("/search")
def buscar_por_nome(
    query: str = Query(..., description="Nome ou tipo do lugar (ex: 'sala 2010', 'banheiro')"),
):
    # TODO: return building_service.buscar(query)
    return {"results": []}


@router.get("/nearest/{node_type}")
def mais_proximo(
    node_type: str,
    origin_id: int = Query(..., description="ID do ponto de origem"),
    gender: str = Query(None, description="Filtro de banheiro: male, female, all"),
    no_stairs: bool = Query(False, description="True para evitar escadas"),
):
    # TODO: return building_service.nearest(node_type, origin_id, gender, no_stairs)
    return {"node": None, "distance": None}


@router.get("/nearest/{node_type}/plot")
def imagem_mais_proximo(
    node_type: str,
    origin_id: int = Query(...),
    gender: str = Query(None),
    no_stairs: bool = Query(False),
):
    # TODO: return plotting_service.gerar_imagem_nearest(node_type, origin_id, gender, no_stairs)
    return {"image_url": "placeholder"}
