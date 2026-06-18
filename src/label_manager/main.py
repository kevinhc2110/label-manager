import asyncio
import logging

from contextlib import asynccontextmanager

from fastapi import FastAPI

from label_manager.api.routers.printers import router as printers_router
from label_manager.api.routers.printers import webhook_router
from label_manager.application.use_cases.process_print_queue_use_case import (
    ProcessPrintQueueUseCase,
)
from label_manager.infrastructure.data.postgres import PostgresDatabase
from label_manager.infrastructure.data.repositories.postgres_label_template_repository import (
    PostgresLabelTemplateRepository,
)
from label_manager.infrastructure.data.repositories.postgres_print_job_repository import (
    PostgresPrintJobRepository,
)
from label_manager.infrastructure.data.repositories.postgres_printer_repository import (
    PostgresPrinterRepository,
)
from label_manager.infrastructure.services.zebra_printer_service import ZebraPrinterService
from label_manager.infrastructure.settings import settings

logger = logging.getLogger(__name__)


_background_task = None


async def _queue_worker(db: PostgresDatabase):
    printer_repo = PostgresPrinterRepository(db)
    job_repo = PostgresPrintJobRepository(db)
    template_repo = PostgresLabelTemplateRepository(db)
    service = ZebraPrinterService()
    use_case = ProcessPrintQueueUseCase(job_repo, printer_repo, template_repo, service)

    # Dedicated connection for LISTEN/NOTIFY
    try:
        listen_conn = await asyncio.wait_for(
            __import__("asyncpg").connect(dsn=settings.postgres_dsn),
            timeout=10,
        )
        await listen_conn.execute("LISTEN print_jobs")

        def _on_notification(_):
            pass  # wake-up signal, processing happens below

        listen_conn.add_listener("print_jobs", _on_notification)
    except Exception:
        logger.warning("LISTEN/NOTIFY not available, using polling only")

    while True:
        try:
            processed = await use_case.process_next_batch(limit=5)
            if processed == 0:
                await asyncio.sleep(3)
        except Exception:
            await asyncio.sleep(5)


@asynccontextmanager
async def lifespan(app: FastAPI):

    db = PostgresDatabase(dsn=settings.postgres_dsn)
    await db.connect()

    app.state.db = db

    global _background_task
    _background_task = asyncio.create_task(_queue_worker(db))

    yield

    if _background_task:
        _background_task.cancel()
        try:
            await _background_task
        except asyncio.CancelledError:
            pass

    await db.disconnect()


app = FastAPI(
    title=settings.app_name,
    lifespan=lifespan,
)

app.include_router(printers_router)
app.include_router(webhook_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
