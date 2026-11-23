'''IntraMaps API entry point.'''
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware

from intramaps.api.floors import router as floors_router
from intramaps.api.places import router as places_router
from intramaps.api.routes import router as routes_router
from intramaps.api.users import router as users_router

app = FastAPI(
    title="IntraMaps",
    description="Navegação interna de prédios da UFMG",
    version="0.1.0",
)

app.add_middleware(GZipMiddleware, minimum_size=500)
# "null" is the origin of a page opened from a file, like web/index.html
app.add_middleware(CORSMiddleware, allow_origins=["null"], allow_methods=["*"], allow_headers=["*"])

api = APIRouter(prefix="/api/v1")
api.include_router(users_router)
api.include_router(floors_router)
api.include_router(places_router)
api.include_router(routes_router)
app.include_router(api)


@app.get("/")
def root():
    '''Health check.'''
    return {"message": "IntraMaps API rodando"}
