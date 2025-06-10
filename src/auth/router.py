from fastapi import APIRouter, Depends
from typing import Annotated

from auth.schemas import UserResponse
from auth.service import get_current_user, add_new_user, log_out_delete_cookie, log_in_user, update_user_name, update_user_password, update_permissions, delete_user
from auth.schemas import Token

auth_router = APIRouter(
    tags=["Auth"]
)

@auth_router.post("/signup", response_model=UserResponse)
async def sign_up(result: Annotated[UserResponse, Depends(add_new_user)],):
    return result

@auth_router.post("/login", response_model=Token)
async def login(token: Annotated[Token, Depends(log_in_user)],):
    return token

@auth_router.post("/logout")
async def logout(response: Annotated[None, Depends(log_out_delete_cookie)],):
    return response

@auth_router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: Annotated[UserResponse, Depends(get_current_user)],):
    return current_user

@auth_router.put("/change_name")
async def change_name(response: Annotated[None, Depends(update_user_name)],):
    return response

@auth_router.put("/change_password")
async def change_password(response: Annotated[None, Depends(update_user_password)],):
    return response

@auth_router.put("/grant_permissions")
async def grant_permissions(response: Annotated[None, Depends(update_permissions)],):
    return response

@auth_router.delete("/delete/{id}")
async def remove_user(response: Annotated[None, Depends(delete_user)],):
    return response