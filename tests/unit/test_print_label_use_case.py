import pytest

from label_manager.application.use_cases.print_label_use_case import PrintLabelUseCase


class TestPrintLabelUseCase:
    @pytest.mark.asyncio
    async def test_execute_calls_print_on_service(
        self, mock_repository, mock_printer_service
    ):
        use_case = PrintLabelUseCase(mock_repository, mock_printer_service)
        await use_case.execute("550e8400-e29b-41d4-a716-446655440000")

        mock_repository.get_by_id.assert_awaited_once_with(
            "550e8400-e29b-41d4-a716-446655440000"
        )
        mock_printer_service.print.assert_awaited_once_with(
            ip_address="192.168.1.100",
            port=9100,
            zpl="\n^XA\n^FO50,50^A0N,40,40^FDHola Mundo^FS\n^XZ\n",
        )

    @pytest.mark.asyncio
    async def test_execute_raises_value_error_for_missing_printer(
        self, mock_repository, mock_printer_service
    ):
        mock_repository.get_by_id.return_value = None
        use_case = PrintLabelUseCase(mock_repository, mock_printer_service)

        with pytest.raises(ValueError, match="Printer 'nonexistent-id' not found"):
            await use_case.execute("nonexistent-id")

        mock_printer_service.print.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_execute_raises_value_error_when_none_returned(
        self, mock_repository, mock_printer_service
    ):
        mock_repository.get_by_id.return_value = None
        use_case = PrintLabelUseCase(mock_repository, mock_printer_service)

        with pytest.raises(ValueError):
            await use_case.execute("missing")
