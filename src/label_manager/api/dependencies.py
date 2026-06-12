from fastapi import Depends
from starlette.requests import HTTPConnection

from label_manager.application.use_cases.get_printers_use_case import GetPrintersUseCase
from label_manager.application.use_cases.print_label_use_case import PrintLabelUseCase
from label_manager.infrastructure.data.repositories.postgres_printer_repository import (
    PostgresPrinterRepository,
)
from label_manager.infrastructure.services.zebra_printer_service import ZebraPrinterService


def get_database(request: HTTPConnection):
    return request.app.state.db


def get_printer_repository(db=Depends(get_database)) -> PostgresPrinterRepository:
    return PostgresPrinterRepository(db)


def get_printer_service() -> ZebraPrinterService:
    return ZebraPrinterService()


def get_printers_use_case(
    repo=Depends(get_printer_repository),
) -> GetPrintersUseCase:
    return GetPrintersUseCase(repo)


def get_print_label_use_case(
    repo=Depends(get_printer_repository),
    service=Depends(get_printer_service),
) -> PrintLabelUseCase:
    return PrintLabelUseCase(repo, service)
