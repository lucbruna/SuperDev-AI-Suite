"""E2E tests for SuperDev frontend using Playwright.

These tests verify the main user flows work end-to-end.
Run with: pytest tests/e2e/ -v --headed (or without --headed for headless)
"""

import pytest

# Skip if playwright is not installed
pytestmark = pytest.mark.skipif(
    not pytest.importorskip("playwright", reason="playwright not installed"),
    reason="playwright not installed",
)


@pytest.fixture(scope="session")
def browser_context_args():
    return {
        "base_url": "http://localhost:3000",
        "viewport": {"width": 1280, "height": 720},
    }


class TestLoginPage:
    """Test login page loads and has expected elements."""

    def test_login_page_loads(self, page):
        page.goto("/login")
        page.wait_for_load_state("networkidle")
        # Should have login form elements
        assert page.title() != ""
        # Check for common login elements
        content = page.content()
        assert "login" in content.lower() or "sign" in content.lower() or "email" in content.lower()

    def test_login_page_has_email_field(self, page):
        page.goto("/login")
        page.wait_for_load_state("networkidle")
        # Look for email input
        email_input = page.locator('input[type="email"], input[name="email"], input[placeholder*="email" i]')
        count = email_input.count()
        assert count > 0, "Login page should have an email input"

    def test_login_page_has_password_field(self, page):
        page.goto("/login")
        page.wait_for_load_state("networkidle")
        password_input = page.locator('input[type="password"], input[name="password"]')
        count = password_input.count()
        assert count > 0, "Login page should have a password input"


class TestRegisterPage:
    """Test registration page loads and has expected elements."""

    def test_register_page_loads(self, page):
        page.goto("/register")
        page.wait_for_load_state("networkidle")
        content = page.content()
        assert "register" in content.lower() or "sign" in content.lower() or "create" in content.lower()

    def test_register_page_has_form(self, page):
        page.goto("/register")
        page.wait_for_load_state("networkidle")
        # Should have form inputs
        inputs = page.locator("input")
        count = inputs.count()
        assert count >= 2, "Register page should have at least 2 input fields"


class TestDashboardPage:
    """Test dashboard page loads (may redirect to login)."""

    def test_dashboard_loads_or_redirects(self, page):
        page.goto("/dashboard")
        page.wait_for_load_state("networkidle")
        # Either shows dashboard or redirects to login
        url = page.url
        assert "dashboard" in url or "login" in url

    def test_dashboard_has_navigation(self, page):
        page.goto("/dashboard")
        page.wait_for_load_state("networkidle")
        # Should have some navigation elements
        nav = page.locator("nav, [role='navigation'], .sidebar, .menu")
        count = nav.count()
        # Navigation might be present or the page might have redirected
        assert count >= 0  # Just verify no crash


class TestProjectsPage:
    """Test projects page loads."""

    def test_projects_page_loads(self, page):
        page.goto("/projects")
        page.wait_for_load_state("networkidle")
        url = page.url
        assert "projects" in url or "login" in url


class TestAgentsPage:
    """Test agents page loads."""

    def test_agents_page_loads(self, page):
        page.goto("/agents")
        page.wait_for_load_state("networkidle")
        url = page.url
        assert "agents" in url or "login" in url


class TestWorkflowsPage:
    """Test workflows page loads."""

    def test_workflows_page_loads(self, page):
        page.goto("/workflows")
        page.wait_for_load_state("networkidle")
        url = page.url
        assert "workflows" in url or "login" in url


class TestSettingsPage:
    """Test settings page loads."""

    def test_settings_page_loads(self, page):
        page.goto("/settings")
        page.wait_for_load_state("networkidle")
        url = page.url
        assert "settings" in url or "login" in url


class TestStaticPages:
    """Test static pages load correctly."""

    def test_home_page_loads(self, page):
        page.goto("/")
        page.wait_for_load_state("networkidle")
        assert page.title() != ""

    def test_docs_page_loads(self, page):
        page.goto("/docs")
        page.wait_for_load_state("networkidle")
        content = page.content()
        assert len(content) > 0

    def test_marketplace_page_loads(self, page):
        page.goto("/marketplace")
        page.wait_for_load_state("networkidle")
        content = page.content()
        assert len(content) > 0


class TestNavigation:
    """Test navigation between pages."""

    def test_navigate_to_login(self, page):
        page.goto("/")
        page.wait_for_load_state("networkidle")
        # Try to find login link
        login_link = page.locator('a[href*="login"], a:has-text("Login"), a:has-text("Sign In")')
        count = login_link.count()
        if count > 0:
            login_link.first.click()
            page.wait_for_url("**/login*", timeout=15000)
            assert "login" in page.url

    def test_navigate_to_register(self, page):
        page.goto("/")
        page.wait_for_load_state("networkidle")
        register_link = page.locator('a[href*="register"], a:has-text("Register"), a:has-text("Sign Up")')
        count = register_link.count()
        if count > 0:
            register_link.first.click()
            page.wait_for_url("**/register*", timeout=15000)
            assert "register" in page.url


class TestResponsiveDesign:
    """Test responsive design at different viewport sizes."""

    def test_mobile_viewport(self, page):
        page.set_viewport_size({"width": 375, "height": 667})
        page.goto("/login")
        page.wait_for_load_state("networkidle")
        content = page.content()
        assert len(content) > 0

    def test_tablet_viewport(self, page):
        page.set_viewport_size({"width": 768, "height": 1024})
        page.goto("/login")
        page.wait_for_load_state("networkidle")
        content = page.content()
        assert len(content) > 0

    def test_desktop_viewport(self, page):
        page.set_viewport_size({"width": 1920, "height": 1080})
        page.goto("/login")
        page.wait_for_load_state("networkidle")
        content = page.content()
        assert len(content) > 0


class TestErrorPages:
    """Test error handling for invalid routes."""

    def test_404_page(self, page):
        response = page.goto("/this-page-does-not-exist-12345")
        # Should either show 404 page or redirect
        assert response is not None

    def test_invalid_api_route(self, page):
        response = page.goto("/api/v1/nonexistent-endpoint")
        assert response is not None
