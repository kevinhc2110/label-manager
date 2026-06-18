from unittest.mock import AsyncMock

import pytest

from label_manager.domain.entities.printer import Printer


@pytest.fixture
def mock_printer():
    return Printer(
        id="550e8400-e29b-41d4-a716-446655440000",
        name="Test Printer",
        ip_address="192.168.1.100",
        port=9100,
        location="Warehouse",
        is_active=True,
    )


@pytest.fixture
def mock_printer_offline():
    return Printer(
        id="660e8400-e29b-41d4-a716-446655440001",
        name="Offline Printer",
        ip_address="192.168.1.200",
        port=9100,
        location="Remote",
        is_active=False,
    )


@pytest.fixture
def mock_repository(mock_printer, mock_printer_offline):
    repo = AsyncMock()
    repo.get_all.return_value = [mock_printer, mock_printer_offline]
    repo.get_by_id.return_value = mock_printer
    return repo


@pytest.fixture
def mock_printer_service():
    svc = AsyncMock()
    svc.check_health = AsyncMock()
    return svc


@pytest.fixture
def mock_print_job_repository():
    repo = AsyncMock()
    repo.create = AsyncMock()
    repo.get_by_id = AsyncMock()
    repo.get_pending = AsyncMock(return_value=[])
    repo.update_status = AsyncMock()
    repo.increment_retry = AsyncMock()
    return repo


@pytest.fixture
def mock_label_template_repository():
    repo = AsyncMock()
    repo.get_all = AsyncMock(return_value=[])
    repo.get_by_id = AsyncMock(return_value=None)
    repo.get_by_name = AsyncMock(return_value=None)
    repo.create = AsyncMock()
    return repo
