from api.authentication import User, get_current_user, oauth2_scheme
from fastapi import APIRouter, Depends

proxy_router = APIRouter()


@proxy_router.post("/")
async def proxy(user: User = Depends(get_current_user)):
    pass
