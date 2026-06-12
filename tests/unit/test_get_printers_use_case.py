import pytest

from label_manager.application.use_cases.get_printers_use_case import GetPrintersUseCase


class TestGetPrintersUseCase:
    @pytest.mark.asyncio
    async def test_execute_returns_list_of_dicts(self, mock_repository):
        use_case = GetPrintersUseCase(mock_repository)
        result = await use_case.execute()

        assert len(result) == 1
        assert result[0]["name"] == "Test Printer"
        assert result[0]["ip_address"] == "192.168.1.100"
        assert result[0]["port"] == 9100
        assert result[0]["is_active"] is True

    @pytest.mark.asyncio
    async def test_execute_calls_get_all(self, mock_repository):
        use_case = GetPrintersUseCase(mock_repository)
        await use_case.execute()
        mock_repository.get_all.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_execute_returns_empty_list(self, mock_repository):
        mock_repository.get_all.return_value = []
        use_case = GetPrintersUseCase(mock_repository)
        result = await use_case.execute()
        assert result == []
