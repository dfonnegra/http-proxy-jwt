import asyncio
import secrets
from datetime import datetime

import aiohttp
import jwt
from api.authentication import User, get_current_user
from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse

proxy_router = APIRouter()


# Normally these fields wouldn't go here but in a local settings managed for example by dynaconf or passed through
# an environment variable with docker.
SECRET_KEY = "a9ddbcaba8c0ac1a0a812dc0c2f08514b23f2db0a68343cb8199ebb38a6d91e4ebfb378e22ad39c2d01d0b4ec9c34aa91056862ddace3fbbd6852ee60c36acbf"
HASHING_ALGORITHM = "HS512"
ENDPOINT_URL = "https://postman-echo.com/post/"


@proxy_router.post("/")
async def proxy(user: User = Depends(get_current_user)):
    payload = {
        "iat": datetime.utcnow(),
        "jti": secrets.token_hex(32),
        "payload": {
            "user": user.username,
            "date": datetime.today().strftime("%Y-%m-%d"),
        },
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=HASHING_ALGORITHM)
    async with aiohttp.ClientSession() as session:
        try:
            response = await session.post(
                ENDPOINT_URL, headers={"x-my-jwt": token.decode("utf-8")},
            )
        except aiohttp.ClientConnectionError:
            return PlainTextResponse(
                "Failed when trying to connect to the remote service.", status_code=502
            )
    if response.status != 200:
        return PlainTextResponse(
            "The remote service returned status: {}".format(response.status),
            status_code=404,
        )
    return "Your request was succesfully processed"
