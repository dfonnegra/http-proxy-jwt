from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from pydantic import BaseModel

# Normally these fields wouldn't go here but in a local settings managed for example by dynaconf or passed through
# an environment variable with docker.
SECRET_KEY = "veryverysecretkey"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
HASHING_ALGORITHM = "HS512"

auth_router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


user_db = {
    "castlabs": {
        "username": "castlabs",
        # Hashed version of insane-safe-password
        "password": "$2b$12$0r4APMiy1T1x1aM7lXPD.OxqU9YYKHNk6Uqb/QciVEDMNpFMA3nvy",
    }
}


class Token(BaseModel):
    access_token: str
    token_type: str


class User(BaseModel):
    username: str
    password: str


def authenticate_user(username: str, password: str):
    return pwd_context.verify(password, user_db[username]["password"])


def hash_password(password: str):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_minutes: Optional[int] = 15):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=HASHING_ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[HASHING_ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        username = username.replace("username:", "")
    except jwt.PyJWTError:
        raise credentials_exception
    user_data = user_db.get(username)
    if user_data is None:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return User(**user_data)


@auth_router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username not in user_db:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    if not authenticate_user(form_data.username, form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = User(**user_db.get(form_data.username))
    access_token = create_access_token(
        {"sub": "username:{}".format(user.username)},
        expires_minutes=ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    return {"access_token": access_token, "token_type": "bearer"}
