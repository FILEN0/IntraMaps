'''User routes.'''
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from intramaps.api.dependencies import get_auth_service, get_current_token, get_current_user
from intramaps.api.dtos import (
    ACCESSIBILITY_MAP, GENDER_MAP, ROLE_MAP, AccessibilitySlug, GenderSlug, RoleSlug, user_dto,
)
from intramaps.services.auth_service import AuthService
from intramaps.users.user import User

router = APIRouter(prefix="/users", tags=["users"])



class RegisterBody(BaseModel):
    '''Body for POST /users.'''
    username: str
    password: str
    gender: GenderSlug = GenderSlug.NONE
    accessibility: AccessibilitySlug = AccessibilitySlug.NONE
    role: RoleSlug = RoleSlug.STUDENT
    speed: float = Field(default=User.DEFAULT_SPEED, gt=0)


class LoginBody(BaseModel):
    '''Body for POST /users/login.'''
    username: str
    password: str


class UpdateBody(BaseModel):
    '''Body for PATCH /users/me.'''
    gender: GenderSlug | None = None
    accessibility: AccessibilitySlug | None = None
    role: RoleSlug | None = None
    speed: float | None = Field(default=None, gt=0)



@router.post("", status_code=201)
def register(body: RegisterBody, auth: AuthService = Depends(get_auth_service)):
    '''Creates a new user account.'''
    try:
        user = auth.register(
            body.username, body.password,
            GENDER_MAP[body.gender], ACCESSIBILITY_MAP[body.accessibility],
            ROLE_MAP[body.role], body.speed,
        )
        return user_dto(user)
    except ValueError as e:
        raise HTTPException(status_code=409, detail="username já existe") from e


@router.post("/login")
def login(body: LoginBody, auth: AuthService = Depends(get_auth_service)):
    '''Validates credentials and returns a session token.'''
    try:
        token, expires_at, user = auth.login(body.username, body.password)
        return {"token": token, "expires_at": expires_at, "user": user_dto(user)}
    except PermissionError as e:
        raise HTTPException(status_code=401, detail="usuário ou senha inválidos") from e


@router.post("/logout", status_code=204)
def logout(
    token: str = Depends(get_current_token),
    auth: AuthService = Depends(get_auth_service),
):
    '''Closes the current session.'''
    auth.logout(token)


@router.get("/me")
def get_me(user: User = Depends(get_current_user)):
    '''Returns the profile of the logged-in user.'''
    return user_dto(user)


@router.patch("/me")
def update_me(
    body: UpdateBody,
    user: User = Depends(get_current_user),
    auth: AuthService = Depends(get_auth_service),
):
    '''Updates one or more fields of the logged-in user profile.'''
    if all(v is None for v in (body.gender, body.accessibility, body.role, body.speed)):
        raise HTTPException(status_code=422, detail="informe ao menos um campo")
    if body.gender is not None:
        user.gender = GENDER_MAP[body.gender]
    if body.accessibility is not None:
        user.accessibility = ACCESSIBILITY_MAP[body.accessibility]
    if body.role is not None:
        user.role = ROLE_MAP[body.role]
    if body.speed is not None:
        user.speed = body.speed
    auth.update_user(user)
    return user_dto(user)


@router.delete("/me", status_code=204)
def delete_me(
    user: User = Depends(get_current_user),
    auth: AuthService = Depends(get_auth_service),
):
    '''Deletes the account of the logged-in user.'''
    auth.delete_user(user.id)


@router.get("/me/favorites")
def get_favorites(
    user: User = Depends(get_current_user),
    auth: AuthService = Depends(get_auth_service),
):
    '''Returns the ids of the user's favorite places.
    TODO: integrate with NodeService to return full PlaceDTOs.
    '''
    return auth.list_favorites(user.id)


@router.put("/me/favorites/{place_id}", status_code=204)
def add_favorite(
    place_id: int,
    user: User = Depends(get_current_user),
    auth: AuthService = Depends(get_auth_service),
):
    '''Adds a place to the user's favorites.'''
    auth.add_favorite(user.id, place_id)


@router.delete("/me/favorites/{place_id}", status_code=204)
def remove_favorite(
    place_id: int,
    user: User = Depends(get_current_user),
    auth: AuthService = Depends(get_auth_service),
):
    '''Removes a place from the user's favorites.'''
    auth.remove_favorite(user.id, place_id)


@router.get("/me/history")
def get_history(
    user: User = Depends(get_current_user),
    auth: AuthService = Depends(get_auth_service),
):
    '''Returns the user's route history, newest first.
    TODO: integrate with NodeService to return full PlaceDTOs in origin/destination.
    '''
    return auth.list_history(user.id)


@router.delete("/me/history/{history_id}", status_code=204)
def delete_history_item(
    history_id: int,
    user: User = Depends(get_current_user),
    auth: AuthService = Depends(get_auth_service),
):
    '''Deletes one history entry.'''
    found = auth.delete_history_item(user.id, history_id)
    if not found:
        raise HTTPException(
            status_code=404, detail=f"item {history_id} do histórico não encontrado"
        )


@router.delete("/me/history", status_code=204)
def clear_history(
    user: User = Depends(get_current_user),
    auth: AuthService = Depends(get_auth_service),
):
    '''Clears all history entries for the logged-in user.'''
    auth.clear_history(user.id)
    