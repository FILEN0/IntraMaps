from fastapi import FastAPI

from intramaps.building.router import router as building_router
from intramaps.routing.router import router as routing_router
from intramaps.users.router import router as users_router

app = FastAPI(
    title="IntraMaps",
    description="Navegação interna de prédios da UFMG",
    version="0.1.0",
)

app.include_router(building_router)
app.include_router(routing_router)
app.include_router(users_router)


@app.get("/")
def root():
    return {"message": "IntraMaps API rodando"}