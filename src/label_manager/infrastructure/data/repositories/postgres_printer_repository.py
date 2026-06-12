from src.label_manager.domain.entities.printer import Printer
from src.label_manager.domain.repositories.printer_repository import PrinterRepository


class PostgresPrinterRepository(PrinterRepository):

    def __init__(self, db):
        self.db = db

    async def get_all(self) -> list[Printer]:
        query = """
            SELECT id, name, ip_address, port, location, is_active
            FROM printer
        """
        rows = await self.db.fetch(query)
        return [
            Printer(
                id=str(row["id"]),
                name=row["name"],
                ip_address=row["ip_address"],
                port=row["port"],
                location=row["location"],
                is_active=row["is_active"],
            )
            for row in rows
        ]

    async def get_by_id(self, printer_id: str) -> Printer | None:
        query = """
            SELECT id, name, ip_address, port, location, is_active
            FROM printer
            WHERE id = $1
        """
        rows = await self.db.fetch(query, printer_id)
        if not rows:
            return None
        row = rows[0]
        return Printer(
            id=str(row["id"]),
            name=row["name"],
            ip_address=row["ip_address"],
            port=row["port"],
            location=row["location"],
            is_active=row["is_active"],
        )
