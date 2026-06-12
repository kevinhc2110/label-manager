import asyncio

from src.label_manager.domain.services.printer_service import PrinterService


class ZebraPrinterService(PrinterService):

    async def print(
        self,
        ip_address: str,
        port: int,
        zpl: str,
    ) -> None:
        reader, writer = await asyncio.open_connection(ip_address, port)
        writer.write(zpl.encode())
        await writer.drain()
        writer.close()
        await writer.wait_closed()
