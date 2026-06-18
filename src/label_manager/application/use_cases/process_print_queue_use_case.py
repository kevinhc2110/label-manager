import asyncio
import json
import logging

from src.label_manager.application.services.label_builder import LabelBuilder
from src.label_manager.application.services.template_engine import TemplateEngine

logger = logging.getLogger(__name__)


class ProcessPrintQueueUseCase:

    def __init__(self, print_job_repository, printer_repository, label_template_repository, printer_service):
        self.print_job_repository = print_job_repository
        self.printer_repository = printer_repository
        self.label_template_repository = label_template_repository
        self.printer_service = printer_service

    async def process_next_batch(self, limit: int = 5) -> int:
        jobs = await self.print_job_repository.get_pending(limit=limit)
        processed = 0

        for job in jobs:
            try:
                await self._process_job(job)
                processed += 1
            except Exception as e:
                logger.error("Failed to process job %s: %s", job.id, e)

        return processed

    async def _process_job(self, job) -> None:
        printer = await self.printer_repository.get_by_id(job.printer_id)
        if not printer:
            await self.print_job_repository.update_status(
                job.id, "failed", error="Printer not found",
            )
            return

        # Resolve template if needed
        text = job.text or "Hola Mundo"
        if job.variables:
            template_obj = None
            if job.template_id:
                template_obj = await self.label_template_repository.get_by_id(job.template_id)
            if template_obj:
                text = TemplateEngine.resolve(template_obj.content_template, job.variables)

        zpl = LabelBuilder.build(text=text, qr_data=job.qr_data, copies=job.copies)

        try:
            await self.printer_service.print(
                ip_address=printer.ip_address,
                port=printer.port,
                zpl=zpl,
            )
            await self.print_job_repository.update_status(job.id, "done")
        except (OSError, asyncio.TimeoutError, ConnectionError) as e:
            error_msg = str(e)
            await self.print_job_repository.increment_retry(job.id, error=error_msg)
