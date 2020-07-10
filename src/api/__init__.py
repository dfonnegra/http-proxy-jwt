from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from passlib.context import CryptContext


SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


user_db = {
    "castlabs": {
        "username": "castlabs",
        "password": "hashed_pass",
    }
}



class User(BaseModel):
    username: str
    password: str


@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_data = user_db.get(form_data.username)
    if user_data is None:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = User(**user_data)
    if form_data.password != user.password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return {"access_token": user.username, "token_type": "bearer"}


@app.post("/")
async def proxy(token: str = Depends(oauth2_scheme)):
    pass