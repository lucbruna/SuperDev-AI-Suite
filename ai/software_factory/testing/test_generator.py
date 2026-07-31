"""Generator for test cases and test code."""
from .models import TestCase, TestCategory


class TestGenerator:
    """Generates test cases from module specifications."""

    def __init__(self):
        self._templates: dict[str, str] = {}

    def generate_for_module(self, module_path: str,
                            category: TestCategory = TestCategory.UNIT) -> list[TestCase]:
        """Generate test cases for a module."""
        tests = []
        # Generate standard test patterns
        tests.append(TestCase(
            name=f"test_{module_path}_instantiation",
            description=f"Test that {module_path} can be instantiated",
            category=category,
            module=module_path,
        ))
        tests.append(TestCase(
            name=f"test_{module_path}_basic_functionality",
            description=f"Test basic functionality of {module_path}",
            category=category,
            module=module_path,
        ))
        tests.append(TestCase(
            name=f"test_{module_path}_edge_cases",
            description=f"Test edge cases for {module_path}",
            category=category,
            module=module_path,
        ))
        return tests

    def generate_unit_test(self, class_name: str, method_name: str) -> TestCase:
        return TestCase(
            name=f"test_{class_name}_{method_name}",
            description=f"Unit test for {class_name}.{method_name}",
            category=TestCategory.UNIT,
        )

    def generate_integration_test(self, component_a: str, component_b: str) -> TestCase:
        return TestCase(
            name=f"test_integration_{component_a}_{component_b}",
            description=f"Integration test between {component_a} and {component_b}",
            category=TestCategory.INTEGRATION,
        )

    def generate_performance_test(self, target: str, threshold_ms: float = 100.0) -> TestCase:
        return TestCase(
            name=f"test_performance_{target}",
            description=f"Performance test for {target} (threshold: {threshold_ms}ms)",
            category=TestCategory.PERFORMANCE,
            timeout=threshold_ms / 1000.0,
        )

    def register_template(self, name: str, template: str) -> None:
        self._templates[name] = template

    def get_template(self, name: str) -> str | None:
        return self._templates.get(name)

    def list_templates(self) -> list[str]:
        return list(self._templates.keys())
