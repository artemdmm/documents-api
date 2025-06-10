import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from typing import Annotated
from fastapi import Depends, HTTPException, status, Response
from sqlmodel import Session, select
from datetime import datetime, timedelta, timezone
from loguru import logger

from auth.schemas import UserRegistration, UserNameChange, UserBase, UserPermissions, TokenData, Token
from auth.models import UserModel
from auth.dependencies import oauth2_scheme, pwd_context
from auth.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from database import get_session

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(session, user_email: str):
    user = session.exec(select(UserModel).where(UserModel.email==user_email)).first()
    if user:
        return user

def authenticate_user(session, email: str, password: str):
    user = get_user(session, email)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)],
                           session: Session = Depends(get_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token,
                             SECRET_KEY,
                             algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(username=email)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(session, user_email=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def add_new_user(user: UserRegistration,
                       session: Session = Depends(get_session)):
    result = UserModel(email=user.email,
                       password=user.password,
                       name=user.name)
    result.password = get_password_hash(result.password)
    session.add(result)
    session.commit()
    session.refresh(result)
    logger.info(f"New user {result.email} was created")
    return result

async def log_in_user(response: Response,
                      form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                      session: Session = Depends(get_session)):
    user = authenticate_user(session,
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

async def update_user_name(current_user: Annotated[UserModel, Depends(get_current_user)],
                           user: UserNameChange,
                           session: Session = Depends(get_session)):
    if current_user.permissions == 3 or user.email == current_user.email:
        user_edit = get_user(session, user.email)
        if user_edit:
            old_name = user_edit.name
            user_edit.name = user.name
            session.add(user_edit)
            session.commit()
            session.refresh(user_edit)
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

async def update_user_password(current_user: Annotated[UserModel, Depends(get_current_user)],
                               user: UserBase,
                               session: Session = Depends(get_session)):
    if current_user.permissions == 3 or user.email == current_user.email:
        user_edit = get_user(session, user.email)
        if user_edit:
            user_edit.password = get_password_hash(user.password)
            session.add(user_edit)
            session.commit()
            session.refresh(user_edit)
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

async def update_permissions(current_user: Annotated[UserModel, Depends(get_current_user)],
                             user: UserPermissions,
                             session: Session = Depends(get_session)):
    if current_user.permissions == 3 or user.email == current_user.email:
        user_edit = get_user(session, user.email)
        if user_edit:
            user_edit.permissions = user.permissions
            session.add(user_edit)
            session.commit()
            session.refresh(user_edit)
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

async def delete_user(current_user: Annotated[UserModel, Depends(get_current_user)],
                      id: int,
                      session: Session = Depends(get_session)):
    if current_user.permissions == 3 or id == current_user.id:
        user = session.get(UserModel, id)
        if user:
            session.delete(user)
            session.commit()
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