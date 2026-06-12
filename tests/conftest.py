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
def mock_repository(mock_printer):
    repo = AsyncMock()
    repo.get_all.return_value = [mock_printer]
    repo.get_by_id.return_value = mock_printer
    return repo


@pytest.fixture
def mock_printer_service():
    return AsyncMock()
