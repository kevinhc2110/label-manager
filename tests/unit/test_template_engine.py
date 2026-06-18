from label_manager.application.services.template_engine import TemplateEngine


class TestTemplateEngine:
    def test_resolve_no_variables(self):
        result = TemplateEngine.resolve("Hello World")
        assert result == "Hello World"

    def test_resolve_with_variables(self):
        result = TemplateEngine.resolve(
            "Order {{order_id}} - {{customer}}",
            {"order_id": "12345", "customer": "Acme"},
        )
        assert result == "Order 12345 - Acme"

    def test_resolve_missing_variable_keeps_placeholder(self):
        result = TemplateEngine.resolve(
            "Hello {{name}}",
            {},
        )
        assert result == "Hello {{name}}"

    def test_resolve_empty_variables(self):
        result = TemplateEngine.resolve("Hello {{name}}", None)
        assert result == "Hello {{name}}"

    def test_resolve_multiple_occurrences(self):
        result = TemplateEngine.resolve(
            "{{x}}-{{x}}-{{x}}",
            {"x": "foo"},
        )
        assert result == "foo-foo-foo"
