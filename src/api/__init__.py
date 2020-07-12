from api.authentication import auth_router
from api.proxy import proxy_router
from fastapi import FastAPI

app = FastAPI()

app.include_router(auth_router)
app.include_router(proxy_router)
