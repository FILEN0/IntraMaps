'''IntraMaps API entry point.'''
from fastapi import FastAPI
from starlette.middleware.gzip import GZipMiddleware

from intramaps.api.routes import router as api_routes_router
from intramaps.api.users import router as api_users_router
from intramaps.building.router import router as building_router
from intramaps.routing.router import router as routing_router

app = FastAPI(
    title="IntraMaps",
    description="Navegação interna de prédios da UFMG",
    version="0.1.0",
)

app.add_middleware(GZipMiddleware, minimum_size=500)

app.include_router(building_router)
app.include_router(routing_router)
app.include_router(api_users_router, prefix="/api/v1")
app.include_router(api_routes_router, prefix="/api/v1")


@app.get("/")
def root():
    '''Health check.'''
    return {"message": "IntraMaps API rodando"}
