import asyncio
import time

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

    async def check_health(
        self,
        ip_address: str,
        port: int,
    ) -> tuple[bool, float | None]:
        start = time.monotonic()
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(ip_address, port),
                timeout=5.0,
            )
            elapsed = (time.monotonic() - start) * 1000
            writer.close()
            await writer.wait_closed()
            return True, round(elapsed, 1)
        except (OSError, asyncio.TimeoutError, ConnectionError):
            return False, None
