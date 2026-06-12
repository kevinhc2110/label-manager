from dataclasses import asdict


class GetPrintersUseCase:
    def __init__(
        self,
        printer_repository,
    ):
        self.printer_repository = printer_repository

    async def execute(self) -> list[dict]:
        printers = await self.printer_repository.get_all()
        return [asdict(printer) for printer in printers]
