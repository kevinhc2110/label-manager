from abc import ABC, abstractmethod

from src.label_manager.domain.entities.printer import Printer


class PrinterRepository(ABC):

    @abstractmethod
    async def get_all(self) -> list[Printer]:
        pass

    @abstractmethod
    async def get_by_id(self, printer_id: str) -> Printer | None:
        pass
