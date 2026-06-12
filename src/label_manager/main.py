from contextlib import asynccontextmanager

from fastapi import FastAPI

from label_manager.api.routers.printers import router as printers_router
from label_manager.infrastructure.data.postgres import PostgresDatabase
from label_manager.infrastructure.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):

    db = PostgresDatabase(dsn=settings.postgres_dsn)
    await db.connect()

    app.state.db = db

    yield

    await db.disconnect()

app = FastAPI(
    title=settings.app_name,
    lifespan=lifespan,
)

app.include_router(printers_router)


@app.get("/health")
async def health():
    return {"status": "ok"}


