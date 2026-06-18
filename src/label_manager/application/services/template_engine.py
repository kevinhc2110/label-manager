import re


class TemplateEngine:

    @staticmethod
    def resolve(template: str, variables: dict | None = None) -> str:
        if not variables:
            return template

        def _replace(match: re.Match) -> str:
            key = match.group(1)
            return str(variables.get(key, match.group(0)))

        return re.sub(r"\{\{(\w+)\}\}", _replace, template)
