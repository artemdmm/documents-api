from fastapi import APIRouter, Depends, Response
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

from auth.models import UserModel
from auth.schemas import UserResponse, UserRegistration, UserNameChange, UserBase, UserPermissions
from auth.service import AuthService
from auth.schemas import Token
from auth.utils import get_current_user

auth_router = APIRouter(
    tags=["Auth"]
)

@auth_router.post("/signup", response_model=UserResponse)
async def sign_up(response: Annotated[AuthService, Depends(AuthService)],
                  user: UserRegistration):
    return await response.add_new_user(user)

@auth_router.post("/login", response_model=Token)
async def login(response_api: Annotated[AuthService, Depends(AuthService)],
                response: Response,
                form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    return await response_api.log_in_user(response, form_data)

@auth_router.post("/logout")
async def logout(response_api: Annotated[AuthService, Depends(AuthService)],
                 response: Response):
    return await response_api.log_out_delete_cookie(response)

@auth_router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: Annotated[UserResponse, Depends(get_current_user)]):
    return current_user

@auth_router.put("/change_name")
async def change_name(response: Annotated[AuthService, Depends(AuthService)],
                      current_user: Annotated[UserModel, Depends(get_current_user)],
                      user: UserNameChange):
    return await response.update_user_name(current_user, user)

@auth_router.put("/change_password")
async def change_password(response: Annotated[AuthService, Depends(AuthService)],
                          current_user: Annotated[UserModel, Depends(get_current_user)],
                          user: UserBase):
    return await response.update_user_password(current_user, user)

@auth_router.put("/grant_permissions")
async def grant_permissions(response: Annotated[AuthService, Depends(AuthService)],
                            current_user: Annotated[UserModel, Depends(get_current_user)],
                            user: UserPermissions):
    return await response.update_permissions(current_user, user)

@auth_router.delete("/delete/{id}")
async def remove_user(response: Annotated[AuthService, Depends(AuthService)],
                      current_user: Annotated[UserModel, Depends(get_current_user)],
                      id: int):
    return await response.delete_user(current_user, id)