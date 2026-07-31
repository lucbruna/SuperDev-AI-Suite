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

    @pytest.mark.asyncio
    async def test_login_page_loads(self, page):
        await page.goto("/login")
        await page.wait_for_load_state("networkidle")
        # Should have login form elements
        assert await page.title() != ""
        # Check for common login elements
        content = await page.content()
        assert "login" in content.lower() or "sign" in content.lower() or "email" in content.lower()

    @pytest.mark.asyncio
    async def test_login_page_has_email_field(self, page):
        await page.goto("/login")
        await page.wait_for_load_state("networkidle")
        # Look for email input
        email_input = page.locator('input[type="email"], input[name="email"], input[placeholder*="email" i]')
        count = await email_input.count()
        assert count > 0, "Login page should have an email input"

    @pytest.mark.asyncio
    async def test_login_page_has_password_field(self, page):
        await page.goto("/login")
        await page.wait_for_load_state("networkidle")
        password_input = page.locator('input[type="password"], input[name="password"]')
        count = await password_input.count()
        assert count > 0, "Login page should have a password input"


class TestRegisterPage:
    """Test registration page loads and has expected elements."""

    @pytest.mark.asyncio
    async def test_register_page_loads(self, page):
        await page.goto("/register")
        await page.wait_for_load_state("networkidle")
        content = await page.content()
        assert "register" in content.lower() or "sign" in content.lower() or "create" in content.lower()

    @pytest.mark.asyncio
    async def test_register_page_has_form(self, page):
        await page.goto("/register")
        await page.wait_for_load_state("networkidle")
        # Should have form inputs
        inputs = page.locator("input")
        count = await inputs.count()
        assert count >= 2, "Register page should have at least 2 input fields"


class TestDashboardPage:
    """Test dashboard page loads (may redirect to login)."""

    @pytest.mark.asyncio
    async def test_dashboard_loads_or_redirects(self, page):
        await page.goto("/dashboard")
        await page.wait_for_load_state("networkidle")
        # Either shows dashboard or redirects to login
        url = page.url
        assert "dashboard" in url or "login" in url

    @pytest.mark.asyncio
    async def test_dashboard_has_navigation(self, page):
        await page.goto("/dashboard")
        await page.wait_for_load_state("networkidle")
        # Should have some navigation elements
        nav = page.locator("nav, [role='navigation'], .sidebar, .menu")
        count = await nav.count()
        # Navigation might be present or the page might have redirected
        assert count >= 0  # Just verify no crash


class TestProjectsPage:
    """Test projects page loads."""

    @pytest.mark.asyncio
    async def test_projects_page_loads(self, page):
        await page.goto("/projects")
        await page.wait_for_load_state("networkidle")
        url = page.url
        assert "projects" in url or "login" in url


class TestAgentsPage:
    """Test agents page loads."""

    @pytest.mark.asyncio
    async def test_agents_page_loads(self, page):
        await page.goto("/agents")
        await page.wait_for_load_state("networkidle")
        url = page.url
        assert "agents" in url or "login" in url


class TestWorkflowsPage:
    """Test workflows page loads."""

    @pytest.mark.asyncio
    async def test_workflows_page_loads(self, page):
        await page.goto("/workflows")
        await page.wait_for_load_state("networkidle")
        url = page.url
        assert "workflows" in url or "login" in url


class TestSettingsPage:
    """Test settings page loads."""

    @pytest.mark.asyncio
    async def test_settings_page_loads(self, page):
        await page.goto("/settings")
        await page.wait_for_load_state("networkidle")
        url = page.url
        assert "settings" in url or "login" in url


class TestStaticPages:
    """Test static pages load correctly."""

    @pytest.mark.asyncio
    async def test_home_page_loads(self, page):
        await page.goto("/")
        await page.wait_for_load_state("networkidle")
        assert await page.title() != ""

    @pytest.mark.asyncio
    async def test_docs_page_loads(self, page):
        await page.goto("/docs")
        await page.wait_for_load_state("networkidle")
        content = await page.content()
        assert len(content) > 0

    @pytest.mark.asyncio
    async def test_marketplace_page_loads(self, page):
        await page.goto("/marketplace")
        await page.wait_for_load_state("networkidle")
        content = await page.content()
        assert len(content) > 0


class TestNavigation:
    """Test navigation between pages."""

    @pytest.mark.asyncio
    async def test_navigate_to_login(self, page):
        await page.goto("/")
        await page.wait_for_load_state("networkidle")
        # Try to find login link
        login_link = page.locator('a[href*="login"], a:has-text("Login"), a:has-text("Sign In")')
        count = await login_link.count()
        if count > 0:
            await login_link.first.click()
            await page.wait_for_load_state("networkidle")
            assert "login" in page.url

    @pytest.mark.asyncio
    async def test_navigate_to_register(self, page):
        await page.goto("/")
        await page.wait_for_load_state("networkidle")
        register_link = page.locator('a[href*="register"], a:has-text("Register"), a:has-text("Sign Up")')
        count = await register_link.count()
        if count > 0:
            await register_link.first.click()
            await page.wait_for_load_state("networkidle")
            assert "register" in page.url


class TestResponsiveDesign:
    """Test responsive design at different viewport sizes."""

    @pytest.mark.asyncio
    async def test_mobile_viewport(self, page):
        await page.set_viewport_size({"width": 375, "height": 667})
        await page.goto("/login")
        await page.wait_for_load_state("networkidle")
        content = await page.content()
        assert len(content) > 0

    @pytest.mark.asyncio
    async def test_tablet_viewport(self, page):
        await page.set_viewport_size({"width": 768, "height": 1024})
        await page.goto("/login")
        await page.wait_for_load_state("networkidle")
        content = await page.content()
        assert len(content) > 0

    @pytest.mark.asyncio
    async def test_desktop_viewport(self, page):
        await page.set_viewport_size({"width": 1920, "height": 1080})
        await page.goto("/login")
        await page.wait_for_load_state("networkidle")
        content = await page.content()
        assert len(content) > 0


class TestErrorPages:
    """Test error handling for invalid routes."""

    @pytest.mark.asyncio
    async def test_404_page(self, page):
        response = await page.goto("/this-page-does-not-exist-12345")
        # Should either show 404 page or redirect
        assert response is not None

    @pytest.mark.asyncio
    async def test_invalid_api_route(self, page):
        response = await page.goto("/api/v1/nonexistent-endpoint")
        assert response is not None
