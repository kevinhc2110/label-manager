from label_manager.application.services.label_builder import LabelBuilder


class TestLabelBuilder:
    def test_build_returns_string(self):
        assert isinstance(LabelBuilder.build(), str)

    def test_build_default_text(self):
        zpl = LabelBuilder.build()
        assert "^FDHola Mundo^FS" in zpl
        assert "^PQ1" in zpl

    def test_build_custom_text(self):
        zpl = LabelBuilder.build(text="Hello World")
        assert "^FDHello World^FS" in zpl

    def test_build_with_qr(self):
        zpl = LabelBuilder.build(text="Item", qr_data="ABC-123")
        assert "^FDItem^FS" in zpl
        assert "^BQN" in zpl
        assert "ABC-123" in zpl

    def test_build_with_copies(self):
        zpl = LabelBuilder.build(text="Test", copies=5)
        assert "^PQ5" in zpl

    def test_build_no_qr_when_not_provided(self):
        zpl = LabelBuilder.build(text="No QR")
        assert "^BQN" not in zpl
