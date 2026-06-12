from contextlib import asynccontextmanager
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from label_manager.api.dependencies import (
    get_database,
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
        )
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
    return AsyncMock()


@pytest_asyncio.fixture
async def client(mock_db, mock_repository, mock_service):
    app.dependency_overrides[get_database] = lambda: mock_db
    app.dependency_overrides[get_printer_repository] = lambda: mock_repository
    app.dependency_overrides[get_printer_service] = lambda: mock_service
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
        assert len(data) == 1
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
        response = await client.post(f"/printers/{printer_id}/print")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Label printed successfully"
        assert data["printer_id"] == printer_id

    @pytest.mark.asyncio
    async def test_returns_404_for_missing_printer(self, client, mock_repository):
        mock_repository.get_by_id.return_value = None
        response = await client.post("/printers/nonexistent/print")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
