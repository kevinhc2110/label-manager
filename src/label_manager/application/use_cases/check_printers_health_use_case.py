import asyncio


class CheckPrintersHealthUseCase:

    def __init__(
        self,
        printer_repository,
        printer_service,
    ):
        self.printer_repository = printer_repository
        self.printer_service = printer_service

    async def execute(self) -> list[dict]:
        printers = await self.printer_repository.get_all()

        async def _check(printer):
            is_online, latency_ms = await self.printer_service.check_health(
                ip_address=printer.ip_address,
                port=printer.port,
            )
            return {
                "printer_id": printer.id,
                "name": printer.name,
                "ip_address": printer.ip_address,
                "port": printer.port,
                "is_online": is_online,
                "latency_ms": latency_ms,
            }

        results = await asyncio.gather(*[_check(p) for p in printers])
        return list(results)
