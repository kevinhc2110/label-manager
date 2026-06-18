from fastapi import APIRouter, Depends, HTTPException

from label_manager.api.dependencies import (
    get_batch_print_use_case,
    get_check_printers_health_use_case,
    get_label_template_repository,
    get_print_job_repository,
    get_print_label_use_case,
    get_printers_use_case,
    get_webhook_print_use_case,
)
from label_manager.api.schemas.printer import (
    BatchPrintRequest,
    LabelTemplateCreate,
    LabelTemplateResponse,
    PrinterHealthResponse,
    PrintJobResponse,
    PrintLabelRequest,
    PrintLabelResponse,
    PrinterResponse,
    WebhookPrintRequest,
)
from label_manager.application.use_cases.batch_print_use_case import BatchPrintUseCase
from label_manager.application.use_cases.check_printers_health_use_case import (
    CheckPrintersHealthUseCase,
)
from label_manager.application.use_cases.get_printers_use_case import GetPrintersUseCase
from label_manager.application.use_cases.print_label_use_case import PrintLabelUseCase
from label_manager.application.use_cases.webhook_print_use_case import WebhookPrintUseCase
from label_manager.domain.repositories.label_template_repository import LabelTemplateRepository
from label_manager.domain.repositories.print_job_repository import PrintJobRepository

router = APIRouter(prefix="/printers", tags=["printers"])


@router.get("", response_model=list[PrinterResponse])
async def list_printers(
    use_case: GetPrintersUseCase = Depends(get_printers_use_case),
):
    return await use_case.execute()


@router.get("/health", response_model=list[PrinterHealthResponse])
async def printers_health(
    use_case: CheckPrintersHealthUseCase = Depends(get_check_printers_health_use_case),
):
    return await use_case.execute()


@router.post("/batch/print", response_model=list[PrintJobResponse])
async def batch_print(
    body: BatchPrintRequest,
    use_case: BatchPrintUseCase = Depends(get_batch_print_use_case),
):
    try:
        jobs = await use_case.execute(
            [item.model_dump() for item in body.jobs],
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return [
        PrintJobResponse(
            id=j.id,
            printer_id=j.printer_id,
            text=j.text,
            qr_data=j.qr_data,
            copies=j.copies,
            status=j.status,
            retry_count=j.retry_count,
            error=j.error,
            created_at=j.created_at,
            processed_at=j.processed_at,
        )
        for j in jobs
    ]


@router.post("/{printer_id}/print", response_model=PrintLabelResponse)
async def print_label(
    printer_id: str,
    body: PrintLabelRequest,
    use_case: PrintLabelUseCase = Depends(get_print_label_use_case),
):
    try:
        await use_case.execute(
            printer_id,
            text=body.text,
            qr_data=body.qr_data,
            copies=body.copies,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return PrintLabelResponse(message="Label printed successfully", printer_id=printer_id)


@router.get("/jobs", response_model=list[PrintJobResponse])
async def list_jobs(
    repo: PrintJobRepository = Depends(get_print_job_repository),
):
    jobs = await repo.get_pending(limit=50)
    return [
        PrintJobResponse(
            id=j.id,
            printer_id=j.printer_id,
            text=j.text,
            qr_data=j.qr_data,
            copies=j.copies,
            status=j.status,
            retry_count=j.retry_count,
            error=j.error,
            created_at=j.created_at,
            processed_at=j.processed_at,
        )
        for j in jobs
    ]


@router.get("/jobs/{job_id}", response_model=PrintJobResponse)
async def get_job(
    job_id: str,
    repo: PrintJobRepository = Depends(get_print_job_repository),
):
    job = await repo.get_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return PrintJobResponse(
        id=job.id,
        printer_id=job.printer_id,
        text=job.text,
        qr_data=job.qr_data,
        copies=job.copies,
        status=job.status,
        retry_count=job.retry_count,
        error=job.error,
        created_at=job.created_at,
        processed_at=job.processed_at,
    )


@router.get("/templates", response_model=list[LabelTemplateResponse])
async def list_templates(
    repo: LabelTemplateRepository = Depends(get_label_template_repository),
):
    templates = await repo.get_all()
    return [
        LabelTemplateResponse(
            id=t.id,
            name=t.name,
            content_template=t.content_template,
            created_at=t.created_at,
        )
        for t in templates
    ]


@router.post("/templates", response_model=LabelTemplateResponse, status_code=201)
async def create_template(
    body: LabelTemplateCreate,
    repo: LabelTemplateRepository = Depends(get_label_template_repository),
):
    from label_manager.domain.entities.label_template import LabelTemplate
    template = LabelTemplate(
        id="",
        name=body.name,
        content_template=body.content_template,
        created_at=None,
    )
    created = await repo.create(template)
    return LabelTemplateResponse(
        id=created.id,
        name=created.name,
        content_template=created.content_template,
        created_at=created.created_at,
    )


# --- Webhook (standalone path for ERP integration) ---

webhook_router = APIRouter(prefix="/webhook", tags=["webhook"])


@webhook_router.post("/print", response_model=PrintJobResponse)
async def webhook_print(
    body: WebhookPrintRequest,
    use_case: WebhookPrintUseCase = Depends(get_webhook_print_use_case),
):
    try:
        job = await use_case.execute(
            printer_id=body.printer_id,
            text=body.text,
            qr_data=body.qr_data,
            copies=body.copies,
            template_name=body.template_name,
            variables=body.variables,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return PrintJobResponse(
        id=job.id,
        printer_id=job.printer_id,
        text=job.text,
        qr_data=job.qr_data,
        copies=job.copies,
        status=job.status,
        retry_count=job.retry_count,
        error=job.error,
        created_at=job.created_at,
        processed_at=job.processed_at,
    )
