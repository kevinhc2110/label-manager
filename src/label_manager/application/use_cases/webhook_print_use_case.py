from src.label_manager.domain.entities.print_job import PrintJob


class WebhookPrintUseCase:

    def __init__(self, printer_repository, print_job_repository):
        self.printer_repository = printer_repository
        self.print_job_repository = print_job_repository

    async def execute(
        self,
        printer_id: str,
        text: str | None = None,
        qr_data: str | None = None,
        copies: int = 1,
        template_name: str | None = None,
        variables: dict | None = None,
    ) -> PrintJob:

        printer = await self.printer_repository.get_by_id(printer_id)
        if not printer:
            raise ValueError(f"Printer '{printer_id}' not found")

        job = PrintJob(
            id="",
            printer_id=printer_id,
            template_id=None,
            text=text,
            qr_data=qr_data,
            copies=copies,
            variables=variables,
            status="pending",
            retry_count=0,
            max_retries=3,
            error=None,
            created_at=None,
            processed_at=None,
        )

        return await self.print_job_repository.create(job)
