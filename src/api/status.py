from datetime import datetime

from database import get_status
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

status_router = APIRouter()
templates = Jinja2Templates(directory="templates")


@status_router.get("/status")
async def status(request: Request):
    status = get_status()
    uptime = round((datetime.utcnow().timestamp() - status["start"]) / (60 * 60), 2)
    return templates.TemplateResponse(
        "status.html", {"request": request, **status, "uptime": uptime}
    )
