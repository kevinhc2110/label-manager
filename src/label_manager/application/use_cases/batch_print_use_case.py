from src.label_manager.domain.entities.print_job import PrintJob


class BatchPrintUseCase:

    def __init__(self, printer_repository, print_job_repository):
        self.printer_repository = printer_repository
        self.print_job_repository = print_job_repository

    async def execute(
        self,
        jobs: list[dict],
    ) -> list[PrintJob]:
        created = []
        for item in jobs:
            printer = await self.printer_repository.get_by_id(item["printer_id"])
            if not printer:
                raise ValueError(f"Printer '{item["printer_id"]}' not found")

            job = PrintJob(
                id="",
                printer_id=item["printer_id"],
                template_id=None,
                text=item.get("text"),
                qr_data=item.get("qr_data"),
                copies=item.get("copies", 1),
                variables=item.get("variables"),
                status="pending",
                retry_count=0,
                max_retries=3,
                error=None,
                created_at=None,
                processed_at=None,
            )
            created.append(await self.print_job_repository.create(job))

        return created
