from api.authentication import auth_router
from api.proxy import proxy_router
from api.status import status_router
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth_router)
app.include_router(proxy_router)
app.include_router(status_router)
