from fastapi import Depends, FastAPI
from fastapi.responses import HTMLResponse

from core.routers.v1.user import rout as user_router

from .database import getDbSession

app = FastAPI(
    title="CopChat",
    summary="CopChat is an secure app for the Cops.",
    version="0.0.1",
    servers=[
        {"url": "http://127.0.0.1:8000", "Local and Dev server": "Dev environment"},
    ],
    dependencies=[Depends(getDbSession)],
)

app.include_router(user_router)


@app.get("/health")
def health():
    return HTMLResponse(status_code=200, content="ok")
