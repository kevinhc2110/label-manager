from label_manager.application.services.label_builder import LabelBuilder
from label_manager.infrastructure.constants import ZPL_LABEL


class TestLabelBuilder:
    def test_build_returns_zpl_label(self):
        assert LabelBuilder.build() == ZPL_LABEL

    def test_build_returns_string(self):
        assert isinstance(LabelBuilder.build(), str)
