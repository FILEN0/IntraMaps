from fastapi import APIRouter
from pydantic import BaseModel
from intramaps.enums.enum_user import EnumGender, EnumAccessibility, EnumRole

router = APIRouter(prefix="/api/v1/users", tags=["users"])


class RegisterInput(BaseModel):
    name: str
    gender: EnumGender
    accessibility: EnumAccessibility
    role: EnumRole
    password: str


class LoginInput(BaseModel):
    name: str
    password: str


class UpdateProfileInput(BaseModel):
    name: str | None = None
    gender: EnumGender | None = None
    accessibility: EnumAccessibility | None = None


@router.post("/register")
def cadastrar(body: RegisterInput):
    # TODO: return auth_service.register(body)
    return {"message": "conta criada"}


@router.post("/login")
def login(body: LoginInput):
    # TODO: return auth_service.login(body)
    return {"token": "placeholder_jwt"}


@router.post("/logout")
def logout():
    return {"message": "logout realizado"}


@router.get("/profile")
def ver_perfil():
    # TODO: return user_service.get_profile(token_do_header)
    return {"user": None}


@router.put("/profile")
def alterar_perfil(body: UpdateProfileInput):
    # TODO: return user_service.update_profile(body)
    return {"message": "perfil atualizado"}


@router.get("/history")
def historico():
    # TODO: return user_repository.get_history(user_id)
    return {"history": []}


@router.get("/favorites")
def favoritos():
    # TODO: return user_repository.get_favorites(user_id)
    return {"favorites": []}


@router.post("/favorites/{node_id}")
def adicionar_favorito(node_id: int):
    # TODO: user_repository.add_favorite(user_id, node_id)
    return {"message": f"node {node_id} adicionado aos favoritos"}


@router.delete("/favorites/{node_id}")
def remover_favorito(node_id: int):
    # TODO: user_repository.remove_favorite(user_id, node_id)
    return {"message": f"node {node_id} removido dos favoritos"}