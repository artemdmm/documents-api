from fastapi import APIRouter, HTTPException, Depends, status, Response
from sqlmodel import Session, select, exists, text
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from datetime import datetime, timedelta, timezone

from models.users import UserModel, UserRegistration, UserResponse, UserBase, UserNameChange, UserPermissions
from models.documents import DocumentModel
from database.connection import get_session
from utils.auth import get_password_hash, authenticate_user, create_access_token, get_current_user, Token, ACCESS_TOKEN_EXPIRE_MINUTES

user_router = APIRouter(
    tags=["User"]
)

@user_router.post("/signup", response_model=UserResponse)
async def sign_up(user: UserRegistration, session: Session = Depends(get_session)) -> dict:
    result = UserModel(email=user.email,
                           password=user.password,
                           name=user.name)
    result.password = get_password_hash(result.password)
    session.add(result)
    session.commit()
    session.refresh(result)
    return result

@user_router.post("/login")
async def login(response: Response, form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: Session = Depends(get_session)) -> Token:
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    response.set_cookie(key="access_token",value=f"Bearer {access_token}", httponly=True)
    return Token(access_token=access_token, token_type="bearer")

@user_router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"status":"success"}

@user_router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: Annotated[UserModel, Depends(get_current_user)],):
    return current_user

@user_router.put("/update", response_model=UserBase)
async def update_password(current_user: Annotated[UserModel, Depends(get_current_user)],
                          user: UserBase, session: Session = Depends(get_session)):
    if current_user.permissions == 3 or user.email == current_user.email:
        user_edit = session.exec(select(UserModel).where(UserModel.email == user.email)).all()
        if user_edit:
            new_user_data = user_edit[0]
            new_user_data.password = get_password_hash(user.password)
            session.add(new_user_data)
            session.commit()
            session.refresh(new_user_data)
            return new_user_data
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="N/A"
        )
    raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed"
        )

@user_router.put("/change_name", response_model=UserNameChange)
async def change_name(current_user: Annotated[UserModel, Depends(get_current_user)],
                      user: UserNameChange, session: Session = Depends(get_session)):
    if current_user.permissions == 3 or user.email == current_user.email:
        user_edit = session.exec(select(UserModel).where(UserModel.email == user.email)).all()
        if user_edit:
            new_user_data = user_edit[0]
            new_user_data.name = user.name
            session.add(new_user_data)
            session.commit()
            session.refresh(new_user_data)
            return new_user_data
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="N/A"
        )
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Not allowed"
    )

@user_router.delete("/delete/{id}")
async def delete_user(current_user: Annotated[UserModel, Depends(get_current_user)], id: int,
                 session: Session = Depends(get_session)):
    if current_user.permissions == 3 or id == current_user.id:
        user = session.get(UserModel, id)
        if user:
            session.delete(user)
            session.commit()
            return {"message": "Success"}
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="N/A"
        )
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Not allowed"
    )

@user_router.put("/grant-permissions")
async def grant_permissions(current_user: Annotated[UserModel, Depends(get_current_user)],
                            user: UserPermissions, session: Session = Depends(get_session)):
    if current_user.permissions == 3 or user.email == current_user.email:
        user_edit = session.exec(select(UserModel).where(UserModel.email == user.email)).all()
        if user_edit:
            new_user_data = user_edit[0]
            new_user_data.permissions = user.permissions
            session.add(new_user_data)
            session.commit()
            session.refresh(new_user_data)
            return {"message": "Success"}
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="N/A"
        )
    raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed"
        )