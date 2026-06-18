import pytest

from label_manager.application.use_cases.batch_print_use_case import BatchPrintUseCase
from label_manager.domain.entities.print_job import PrintJob


class TestBatchPrintUseCase:
    @pytest.mark.asyncio
    async def test_creates_multiple_jobs(self, mock_repository, mock_print_job_repository):
        mock_print_job_repository.create.side_effect = [
            PrintJob(id="job-1", printer_id="550e8400-e29b-41d4-a716-446655440000", template_id=None, text="Box 1", qr_data=None, copies=1, variables=None, status="pending", retry_count=0, max_retries=3, error=None, created_at=None, processed_at=None),
            PrintJob(id="job-2", printer_id="550e8400-e29b-41d4-a716-446655440000", template_id=None, text="Box 2", qr_data="QR2", copies=2, variables=None, status="pending", retry_count=0, max_retries=3, error=None, created_at=None, processed_at=None),
        ]

        use_case = BatchPrintUseCase(mock_repository, mock_print_job_repository)
        jobs = await use_case.execute([
            {"printer_id": "550e8400-e29b-41d4-a716-446655440000", "text": "Box 1"},
            {"printer_id": "550e8400-e29b-41d4-a716-446655440000", "text": "Box 2", "qr_data": "QR2", "copies": 2},
        ])

        assert len(jobs) == 2
        assert jobs[0].id == "job-1"
        assert jobs[1].copies == 2
        assert jobs[1].qr_data == "QR2"
        assert mock_print_job_repository.create.await_count == 2

    @pytest.mark.asyncio
    async def test_raises_error_for_missing_printer(self, mock_repository, mock_print_job_repository):
        mock_repository.get_by_id.side_effect = [None]
        use_case = BatchPrintUseCase(mock_repository, mock_print_job_repository)

        with pytest.raises(ValueError, match="Printer 'bad-id' not found"):
            await use_case.execute([
                {"printer_id": "bad-id", "text": "Test"},
            ])
