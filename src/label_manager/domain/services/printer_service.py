from abc import ABC, abstractmethod


class PrinterService(ABC):

    @abstractmethod
    async def print(
        self,
        ip_address: str,
        port: int,
        zpl: str,
    ) -> None:
        pass
