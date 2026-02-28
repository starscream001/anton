import logging

from fastapi import FastAPI

from app.api.routes import router
from app.db.session import init_db

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Auto Poster")
app.include_router(router)


@app.on_event("startup")
def startup_event() -> None:
    init_db()
