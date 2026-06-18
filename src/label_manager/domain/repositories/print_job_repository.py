from abc import ABC, abstractmethod

from src.label_manager.domain.entities.print_job import PrintJob


class PrintJobRepository(ABC):

    @abstractmethod
    async def create(self, job: PrintJob) -> PrintJob:
        pass

    @abstractmethod
    async def get_by_id(self, job_id: str) -> PrintJob | None:
        pass

    @abstractmethod
    async def get_pending(self, limit: int = 10) -> list[PrintJob]:
        pass

    @abstractmethod
    async def update_status(
        self, job_id: str, status: str, error: str | None = None,
    ) -> None:
        pass

    @abstractmethod
    async def increment_retry(self, job_id: str, error: str) -> None:
        pass
