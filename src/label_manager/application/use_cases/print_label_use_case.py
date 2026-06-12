from src.label_manager.application.services.label_builder import LabelBuilder


class PrintLabelUseCase:

    def __init__(
        self,
        printer_repository,
        printer_service,
    ):
        self.printer_repository = printer_repository
        self.printer_service = printer_service

    async def execute(
        self,
        printer_id: str,
    ):

        printer = await self.printer_repository.get_by_id(printer_id)
        if not printer:
            raise ValueError(f"Printer '{printer_id}' not found")

        zpl = LabelBuilder.build()

        await self.printer_service.print(
            ip_address=printer.ip_address,
            port=printer.port,
            zpl=zpl,
        )
