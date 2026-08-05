"""Unit tests for API docs configuration."""

from starlette.applications import Starlette


class TestAPIDocs:
    def test_setup_docs_configures_metadata(self):
        from backend.api.docs import setup_docs

        app = Starlette()
        setup_docs(app)

        assert app.title == "SuperDev AI Suite"
        assert app.version == "6.0.0"
        assert "Enterprise" in app.description

    def test_setup_docs_configures_tags(self):
        from backend.api.docs import setup_docs

        app = Starlette()
        setup_docs(app)

        tag_names = [t["name"] for t in app.openapi_tags]
        assert "Authentication" in tag_names
        assert "Workflows" in tag_names
        assert "Agents" in tag_names
        assert "Health" in tag_names
        assert "Plugins" in tag_names

    def test_setup_docs_has_contact(self):
        from backend.api.docs import setup_docs

        app = Starlette()
        setup_docs(app)

        assert app.contact["name"] == "SuperDev Team"

    def test_setup_docs_has_license(self):
        from backend.api.docs import setup_docs

        app = Starlette()
        setup_docs(app)

        assert app.license_info["name"] == "MIT"
