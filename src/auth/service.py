from fastapi.security import OAuth2PasswordRequestForm
from fastapi import HTTPException, status, Response
from datetime import timedelta
from loguru import logger

from auth.schemas import UserRegistration, UserNameChange, UserBase, UserPermissions, Token
from auth.models import UserModel
from auth.utils import get_session, get_password_hash, get_user, authenticate_user, create_access_token
from auth.config import ACCESS_TOKEN_EXPIRE_MINUTES
from database import get_session

class AuthService:
    session: str
    
    def __init__(self):
        self.session = next(get_session())

    async def add_new_user(self,
                           user: UserRegistration):
        result = UserModel(email=user.email,
                           password=user.password,
                           name=user.name)
        result.password = get_password_hash(result.password)
        self.session.add(result)
        self.session.commit()
        self.session.refresh(result)
        logger.info(f"New user {result.email} was created")
        return result

    async def log_in_user(self,
                          response: Response,
                          form_data: OAuth2PasswordRequestForm):
        user = authenticate_user(self.session,
                                 form_data.username,
                                 form_data.password)
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

    async def log_out_delete_cookie(response: Response):
        response.delete_cookie(key="access_token")
        return {"status":"Success"}

    async def update_user_name(self,
                               current_user: UserModel,
                               user: UserNameChange):
        if current_user.permissions == 3 or user.email == current_user.email:
            user_edit = get_user(self.session, user.email)
            if user_edit:
                old_name = user_edit.name
                user_edit.name = user.name
                self.session.add(user_edit)
                self.session.commit()
                self.session.refresh(user_edit)
                logger.info(f"User {user_edit.email} changed his name from {old_name} to {user_edit.name}")
                return {"status":"Success"}
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="N/A"
            )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permissions"
        )

    async def update_user_password(self,
                                   current_user: UserModel,
                                   user: UserBase):
        if current_user.permissions == 3 or user.email == current_user.email:
            user_edit = get_user(self.session, user.email)
            if user_edit:
                user_edit.password = get_password_hash(user.password)
                self.session.add(user_edit)
                self.session.commit()
                self.session.refresh(user_edit)
                logger.info(f"User {user_edit.email} changed his password")
                return {"status": "Success"}
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="N/A"
            )
        raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No permissions"
            )

    async def update_permissions(self,
                                 current_user: UserModel,
                                 user: UserPermissions):
        if current_user.permissions == 3:
            user_edit = get_user(self.session, user.email)
            if user_edit:
                user_edit.permissions = user.permissions
                self.session.add(user_edit)
                self.session.commit()
                self.session.refresh(user_edit)
                logger.info(f"User {current_user.email} changed {user_edit.email} permissions level to {user_edit.permissions}")
                return {"status": "Success"}
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="N/A"
            )
        raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No permissions"
            )

    async def delete_user(self,
                          current_user: UserModel,
                          id: int):
        if current_user.permissions == 3 or id == current_user.id:
            user = self.session.get(UserModel, id)
            if user:
                self.session.delete(user)
                self.session.commit()
                logger.info(f"User {current_user.email} deleted {user.email} account")
                return {"status": "Success"}
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="N/A"
            )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permissions"
        )