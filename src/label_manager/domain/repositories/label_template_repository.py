from abc import ABC, abstractmethod

from src.label_manager.domain.entities.label_template import LabelTemplate


class LabelTemplateRepository(ABC):

    @abstractmethod
    async def get_all(self) -> list[LabelTemplate]:
        pass

    @abstractmethod
    async def get_by_id(self, template_id: str) -> LabelTemplate | None:
        pass

    @abstractmethod
    async def get_by_name(self, name: str) -> LabelTemplate | None:
        pass

    @abstractmethod
    async def create(self, template: LabelTemplate) -> LabelTemplate:
        pass
