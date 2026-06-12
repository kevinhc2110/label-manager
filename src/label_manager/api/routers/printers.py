from fastapi import APIRouter, Depends, HTTPException

from label_manager.api.dependencies import (
    get_printers_use_case,
    get_print_label_use_case,
)
from label_manager.api.schemas.printer import PrinterResponse, PrintLabelResponse
from label_manager.application.use_cases.get_printers_use_case import GetPrintersUseCase
from label_manager.application.use_cases.print_label_use_case import PrintLabelUseCase

router = APIRouter(prefix="/printers", tags=["printers"])


@router.get("", response_model=list[PrinterResponse])
async def list_printers(
    use_case: GetPrintersUseCase = Depends(get_printers_use_case),
):
    return await use_case.execute()


@router.post("/{printer_id}/print", response_model=PrintLabelResponse)
async def print_label(
    printer_id: str,
    use_case: PrintLabelUseCase = Depends(get_print_label_use_case),
):
    try:
        await use_case.execute(printer_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return PrintLabelResponse(message="Label printed successfully", printer_id=printer_id)
