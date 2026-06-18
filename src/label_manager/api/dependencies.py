from fastapi import Depends
from starlette.requests import HTTPConnection

from label_manager.application.use_cases.batch_print_use_case import BatchPrintUseCase
from label_manager.application.use_cases.check_printers_health_use_case import (
    CheckPrintersHealthUseCase,
)
from label_manager.application.use_cases.get_printers_use_case import GetPrintersUseCase
from label_manager.application.use_cases.print_label_use_case import PrintLabelUseCase
from label_manager.application.use_cases.webhook_print_use_case import WebhookPrintUseCase
from label_manager.infrastructure.data.repositories.postgres_label_template_repository import (
    PostgresLabelTemplateRepository,
)
from label_manager.infrastructure.data.repositories.postgres_print_job_repository import (
    PostgresPrintJobRepository,
)
from label_manager.infrastructure.data.repositories.postgres_printer_repository import (
    PostgresPrinterRepository,
)
from label_manager.infrastructure.services.zebra_printer_service import ZebraPrinterService


def get_database(request: HTTPConnection):
    return request.app.state.db


def get_printer_repository(db=Depends(get_database)) -> PostgresPrinterRepository:
    return PostgresPrinterRepository(db)


def get_print_job_repository(db=Depends(get_database)) -> PostgresPrintJobRepository:
    return PostgresPrintJobRepository(db)


def get_label_template_repository(db=Depends(get_database)) -> PostgresLabelTemplateRepository:
    return PostgresLabelTemplateRepository(db)


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


def get_check_printers_health_use_case(
    repo=Depends(get_printer_repository),
    service=Depends(get_printer_service),
) -> CheckPrintersHealthUseCase:
    return CheckPrintersHealthUseCase(repo, service)


def get_webhook_print_use_case(
    printer_repo=Depends(get_printer_repository),
    job_repo=Depends(get_print_job_repository),
) -> WebhookPrintUseCase:
    return WebhookPrintUseCase(printer_repo, job_repo)


def get_batch_print_use_case(
    printer_repo=Depends(get_printer_repository),
    job_repo=Depends(get_print_job_repository),
) -> BatchPrintUseCase:
    return BatchPrintUseCase(printer_repo, job_repo)
