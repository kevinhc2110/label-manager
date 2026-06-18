from src.label_manager.domain.entities.label_template import LabelTemplate
from src.label_manager.domain.repositories.label_template_repository import LabelTemplateRepository


class PostgresLabelTemplateRepository(LabelTemplateRepository):

    def __init__(self, db):
        self.db = db

    async def get_all(self) -> list[LabelTemplate]:
        query = """
            SELECT id, name, content_template, created_at
            FROM label_template ORDER BY name
        """
        rows = await self.db.fetch(query)
        return [self._row_to_template(r) for r in rows]

    async def get_by_id(self, template_id: str) -> LabelTemplate | None:
        query = """
            SELECT id, name, content_template, created_at
            FROM label_template WHERE id = $1
        """
        rows = await self.db.fetch(query, template_id)
        if not rows:
            return None
        return self._row_to_template(rows[0])

    async def get_by_name(self, name: str) -> LabelTemplate | None:
        query = """
            SELECT id, name, content_template, created_at
            FROM label_template WHERE name = $1
        """
        rows = await self.db.fetch(query, name)
        if not rows:
            return None
        return self._row_to_template(rows[0])

    async def create(self, template: LabelTemplate) -> LabelTemplate:
        query = """
            INSERT INTO label_template (name, content_template)
            VALUES ($1, $2)
            RETURNING id, created_at
        """
        row = await self.db.fetch(query, template.name, template.content_template)
        r = row[0]
        template.id = str(r["id"])
        template.created_at = r["created_at"]
        return template

    def _row_to_template(self, row) -> LabelTemplate:
        return LabelTemplate(
            id=str(row["id"]),
            name=row["name"],
            content_template=row["content_template"],
            created_at=row["created_at"],
        )
