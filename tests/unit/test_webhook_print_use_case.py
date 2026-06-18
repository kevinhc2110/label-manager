import pytest

from label_manager.application.use_cases.webhook_print_use_case import WebhookPrintUseCase
from label_manager.domain.entities.print_job import PrintJob


class TestWebhookPrintUseCase:
    @pytest.mark.asyncio
    async def test_creates_pending_job(self, mock_repository, mock_print_job_repository):
        created = PrintJob(
            id="job-123",
            printer_id="550e8400-e29b-41d4-a716-446655440000",
            template_id=None,
            text="Test label",
            qr_data=None,
            copies=1,
            variables=None,
            status="pending",
            retry_count=0,
            max_retries=3,
            error=None,
            created_at=None,
            processed_at=None,
        )
        mock_print_job_repository.create.return_value = created

        use_case = WebhookPrintUseCase(mock_repository, mock_print_job_repository)
        job = await use_case.execute(
            printer_id="550e8400-e29b-41d4-a716-446655440000",
            text="Test label",
        )

        assert job.id == "job-123"
        assert job.status == "pending"
        mock_print_job_repository.create.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_raises_error_for_missing_printer(self, mock_repository, mock_print_job_repository):
        mock_repository.get_by_id.return_value = None
        use_case = WebhookPrintUseCase(mock_repository, mock_print_job_repository)

        with pytest.raises(ValueError, match="Printer 'bad-id' not found"):
            await use_case.execute(printer_id="bad-id")
