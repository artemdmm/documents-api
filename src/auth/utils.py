import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import Depends
from sqlmodel import Session
from typing import Annotated
from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import datetime, timedelta, timezone

from auth.schemas import TokenData
from auth.models import UserModel
from auth.dependencies import oauth2_scheme, pwd_context
from auth.config import SECRET_KEY, ALGORITHM
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