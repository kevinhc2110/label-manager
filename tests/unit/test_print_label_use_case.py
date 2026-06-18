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
        mock_printer_service.print.assert_awaited_once()
        call_kwargs = mock_printer_service.print.call_args.kwargs
        assert call_kwargs["ip_address"] == "192.168.1.100"
        assert call_kwargs["port"] == 9100
        assert "^FDHola Mundo^FS" in call_kwargs["zpl"]

    @pytest.mark.asyncio
    async def test_execute_custom_text(
        self, mock_repository, mock_printer_service
    ):
        use_case = PrintLabelUseCase(mock_repository, mock_printer_service)
        await use_case.execute(
            "550e8400-e29b-41d4-a716-446655440000",
            text="Custom Label",
            copies=3,
        )

        call_kwargs = mock_printer_service.print.call_args.kwargs
        assert "^FDCustom Label^FS" in call_kwargs["zpl"]
        assert "^PQ3" in call_kwargs["zpl"]

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
