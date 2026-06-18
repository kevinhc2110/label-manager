from contextlib import asynccontextmanager
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from label_manager.api.dependencies import (
    get_database,
    get_label_template_repository,
    get_print_job_repository,
    get_printer_repository,
    get_printer_service,
)
from label_manager.domain.entities.printer import Printer
from label_manager.main import app


@asynccontextmanager
async def _noop_lifespan(_):
    yield


@pytest.fixture(autouse=True)
def _mock_lifespan():
    app.router.lifespan_context = _noop_lifespan
    yield


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def mock_repository():
    repo = AsyncMock()
    repo.get_all.return_value = [
        Printer(
            id="550e8400-e29b-41d4-a716-446655440000",
            name="Test Printer",
            ip_address="192.168.1.100",
            port=9100,
            location="Warehouse",
            is_active=True,
        ),
        Printer(
            id="660e8400-e29b-41d4-a716-446655440001",
            name="Offline Printer",
            ip_address="192.168.1.200",
            port=9100,
            location="Remote",
            is_active=False,
        ),
    ]
    repo.get_by_id.return_value = Printer(
        id="550e8400-e29b-41d4-a716-446655440000",
        name="Test Printer",
        ip_address="192.168.1.100",
        port=9100,
        location="Warehouse",
        is_active=True,
    )
    return repo


@pytest.fixture
def mock_service():
    svc = AsyncMock()
    svc.check_health = AsyncMock()
    return svc


@pytest.fixture
def mock_print_job_repo():
    repo = AsyncMock()
    repo.create = AsyncMock()
    repo.get_pending = AsyncMock(return_value=[])
    repo.get_by_id = AsyncMock(return_value=None)
    repo.update_status = AsyncMock()
    repo.increment_retry = AsyncMock()
    return repo


@pytest.fixture
def mock_template_repo():
    repo = AsyncMock()
    repo.get_all = AsyncMock(return_value=[])
    repo.get_by_id = AsyncMock(return_value=None)
    repo.get_by_name = AsyncMock(return_value=None)
    repo.create = AsyncMock()
    return repo


@pytest_asyncio.fixture
async def client(mock_db, mock_repository, mock_service, mock_print_job_repo, mock_template_repo):
    app.dependency_overrides[get_database] = lambda: mock_db
    app.dependency_overrides[get_printer_repository] = lambda: mock_repository
    app.dependency_overrides[get_printer_service] = lambda: mock_service
    app.dependency_overrides[get_print_job_repository] = lambda: mock_print_job_repo
    app.dependency_overrides[get_label_template_repository] = lambda: mock_template_repo
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


class TestListPrinters:
    @pytest.mark.asyncio
    async def test_returns_printers(self, client):
        response = await client.get("/printers")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "Test Printer"
        assert data[0]["ip_address"] == "192.168.1.100"
        assert data[0]["port"] == 9100
        assert data[0]["location"] == "Warehouse"
        assert data[0]["is_active"] is True

    @pytest.mark.asyncio
    async def test_returns_empty_list(self, client, mock_repository):
        mock_repository.get_all.return_value = []
        response = await client.get("/printers")
        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_returns_200_on_get(self, client):
        response = await client.get("/printers")
        assert response.status_code == 200


class TestPrintLabel:
    @pytest.mark.asyncio
    async def test_prints_label_successfully(self, client):
        printer_id = "550e8400-e29b-41d4-a716-446655440000"
        response = await client.post(
            f"/printers/{printer_id}/print",
            json={"text": "Hello World", "copies": 2},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Label printed successfully"
        assert data["printer_id"] == printer_id

    @pytest.mark.asyncio
    async def test_prints_with_qr(self, client):
        printer_id = "550e8400-e29b-41d4-a716-446655440000"
        response = await client.post(
            f"/printers/{printer_id}/print",
            json={"text": "Item", "qr_data": "QR-CODE-123"},
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_prints_default_text_when_not_provided(self, client):
        printer_id = "550e8400-e29b-41d4-a716-446655440000"
        response = await client.post(
            f"/printers/{printer_id}/print",
            json={},
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_returns_404_for_missing_printer(self, client, mock_repository):
        mock_repository.get_by_id.return_value = None
        response = await client.post(
            "/printers/nonexistent/print",
            json={"text": "Test"},
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestPrinterHealth:
    @pytest.mark.asyncio
    async def test_returns_health_for_all_printers(self, client, mock_service):
        mock_service.check_health.side_effect = [
            (True, 4.2),
            (False, None),
        ]
        response = await client.get("/printers/health")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["printer_id"] == "550e8400-e29b-41d4-a716-446655440000"
        assert data[0]["is_online"] is True
        assert data[0]["latency_ms"] == 4.2
        assert data[1]["printer_id"] == "660e8400-e29b-41d4-a716-446655440001"
        assert data[1]["is_online"] is False
        assert data[1]["latency_ms"] is None

    @pytest.mark.asyncio
    async def test_returns_empty_when_no_printers(self, client, mock_repository, mock_service):
        mock_repository.get_all.return_value = []
        response = await client.get("/printers/health")
        assert response.status_code == 200
        assert response.json() == []


class TestWebhook:
    @pytest.mark.asyncio
    async def test_webhook_creates_job(self, client, mock_print_job_repo):
        from label_manager.domain.entities.print_job import PrintJob
        mock_print_job_repo.create.return_value = PrintJob(
            id="job-w-1", printer_id="550e8400-e29b-41d4-a716-446655440000",
            template_id=None, text="ERP Label", qr_data=None, copies=1,
            variables=None, status="pending", retry_count=0, max_retries=3,
            error=None, created_at=None, processed_at=None,
        )
        response = await client.post("/webhook/print", json={
            "printer_id": "550e8400-e29b-41d4-a716-446655440000",
            "text": "ERP Label",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "job-w-1"
        assert data["status"] == "pending"

    @pytest.mark.asyncio
    async def test_webhook_returns_404_for_bad_printer(self, client, mock_repository):
        mock_repository.get_by_id.return_value = None
        response = await client.post("/webhook/print", json={
            "printer_id": "bad-id",
            "text": "Test",
        })
        assert response.status_code == 404


class TestBatchPrint:
    @pytest.mark.asyncio
    async def test_batch_creates_jobs(self, client, mock_print_job_repo):
        from label_manager.domain.entities.print_job import PrintJob
        mock_print_job_repo.create.side_effect = [
            PrintJob(id="b1", printer_id="550e8400-e29b-41d4-a716-446655440000", template_id=None, text="Box 1", qr_data=None, copies=1, variables=None, status="pending", retry_count=0, max_retries=3, error=None, created_at=None, processed_at=None),
            PrintJob(id="b2", printer_id="550e8400-e29b-41d4-a716-446655440000", template_id=None, text="Box 2", qr_data="Q2", copies=2, variables=None, status="pending", retry_count=0, max_retries=3, error=None, created_at=None, processed_at=None),
        ]
        response = await client.post("/printers/batch/print", json={
            "jobs": [
                {"printer_id": "550e8400-e29b-41d4-a716-446655440000", "text": "Box 1"},
                {"printer_id": "550e8400-e29b-41d4-a716-446655440000", "text": "Box 2", "qr_data": "Q2", "copies": 2},
            ],
        })
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["id"] == "b1"
        assert data[1]["copies"] == 2

    @pytest.mark.asyncio
    async def test_batch_returns_404_for_bad_printer(self, client, mock_repository):
        mock_repository.get_by_id.side_effect = [None]
        response = await client.post("/printers/batch/print", json={
            "jobs": [{"printer_id": "bad-id", "text": "X"}],
        })
        assert response.status_code == 404


class TestTemplates:
    @pytest.mark.asyncio
    async def test_list_templates(self, client, mock_template_repo):
        from label_manager.domain.entities.label_template import LabelTemplate
        mock_template_repo.get_all.return_value = [
            LabelTemplate(id="t1", name="default", content_template="Standard", created_at=None),
        ]
        response = await client.get("/printers/templates")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "default"

    @pytest.mark.asyncio
    async def test_create_template(self, client, mock_template_repo):
        from label_manager.domain.entities.label_template import LabelTemplate
        mock_template_repo.create.return_value = LabelTemplate(
            id="new-t", name="custom", content_template="Order {{id}}", created_at=None,
        )
        response = await client.post("/printers/templates", json={
            "name": "custom",
            "content_template": "Order {{id}}",
        })
        assert response.status_code == 201
        assert response.json()["name"] == "custom"
