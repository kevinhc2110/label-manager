import json
from datetime import datetime

from src.label_manager.domain.entities.print_job import PrintJob
from src.label_manager.domain.repositories.print_job_repository import PrintJobRepository


class PostgresPrintJobRepository(PrintJobRepository):

    def __init__(self, db):
        self.db = db

    async def create(self, job: PrintJob) -> PrintJob:
        query = """
            INSERT INTO print_job (printer_id, template_id, text, qr_data, copies, variables, status, max_retries)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING id, created_at
        """
        row = await self.db.fetch(
            query,
            job.printer_id,
            job.template_id,
            job.text,
            job.qr_data,
            job.copies,
            json.dumps(job.variables) if job.variables else None,
            job.status,
            job.max_retries,
        )
        r = row[0]
        job.id = str(r["id"])
        job.created_at = r["created_at"]
        return job

    async def get_by_id(self, job_id: str) -> PrintJob | None:
        query = """
            SELECT id, printer_id, template_id, text, qr_data, copies,
                   variables, status, retry_count, max_retries, error,
                   created_at, processed_at
            FROM print_job WHERE id = $1
        """
        rows = await self.db.fetch(query, job_id)
        if not rows:
            return None
        return self._row_to_job(rows[0])

    async def get_pending(self, limit: int = 10) -> list[PrintJob]:
        query = """
            SELECT id, printer_id, template_id, text, qr_data, copies,
                   variables, status, retry_count, max_retries, error,
                   created_at, processed_at
            FROM print_job
            WHERE status = 'pending' AND retry_count < max_retries
            ORDER BY created_at ASC
            LIMIT $1
        """
        rows = await self.db.fetch(query, limit)
        return [self._row_to_job(r) for r in rows]

    async def update_status(
        self, job_id: str, status: str, error: str | None = None,
    ) -> None:
        query = """
            UPDATE print_job
            SET status = $2, error = $3, processed_at = NOW()
            WHERE id = $1
        """
        await self.db.execute(query, job_id, status, error)

    async def increment_retry(self, job_id: str, error: str) -> None:
        query = """
            UPDATE print_job
            SET retry_count = retry_count + 1,
                error = $2,
                status = CASE WHEN retry_count + 1 >= max_retries THEN 'failed' ELSE 'pending' END
            WHERE id = $1
        """
        await self.db.execute(query, job_id, error)

    def _row_to_job(self, row) -> PrintJob:
        return PrintJob(
            id=str(row["id"]),
            printer_id=str(row["printer_id"]),
            template_id=str(row["template_id"]) if row["template_id"] else None,
            text=row["text"],
            qr_data=row["qr_data"],
            copies=row["copies"],
            variables=json.loads(row["variables"]) if row["variables"] else None,
            status=row["status"],
            retry_count=row["retry_count"],
            max_retries=row["max_retries"],
            error=row["error"],
            created_at=row["created_at"],
            processed_at=row["processed_at"],
        )
