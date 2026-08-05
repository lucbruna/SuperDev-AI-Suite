from __future__ import annotations

import ast
import logging
import random
import re
import string
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger("superdev.ai.testgen")


class TestFramework(str, Enum):
    PYTEST = "pytest"
    UNITTEST = "unittest"
    JEST = "jest"
    MOCHA = "mocha"
    JUNIT = "junit"
    GO_TEST = "go_test"
    RUST_TEST = "rust_test"


class TestType(str, Enum):
    UNIT = "unit"
    INTEGRATION = "integration"
    FUNCTIONAL = "functional"
    REGRESSION = "regression"


@dataclass
class TestRequest:
    code: str
    framework: TestFramework = TestFramework.PYTEST
    test_type: TestType = TestType.UNIT
    module_name: str = ""
    class_name: str = ""
    function_name: str = ""
    coverage_target: float = 0.8
    include_edge_cases: bool = True
    include_mocks: bool = True
    max_test_cases: int = 10


@dataclass
class GeneratedTest:
    test_code: str = ""
    framework: TestFramework = TestFramework.PYTEST
    test_type: TestType = TestType.UNIT
    module_name: str = ""
    class_name: str = ""
    function_name: str = ""
    mocks_used: list[str] = field(default_factory=list)
    test_data: dict[str, Any] = field(default_factory=dict)
    coverage_estimate: float = 0.0
    warnings: list[str] = field(default_factory=list)
    file_path: Optional[str] = None


FRAMEWORK_CONFIGS: dict[TestFramework, dict[str, Any]] = {
    TestFramework.PYTEST: {
        "imports": "import pytest\nfrom unittest.mock import MagicMock, patch\n",
        "decorator": "",
        "assert_eq": "assert ",
        "assert_raises": "with pytest.raises({exc}):",
        "mock_prefix": "mock_",
        "fixture_prefix": "@pytest.fixture",
        "file_suffix": "_test.py",
    },
    TestFramework.UNITTEST: {
        "imports": "import unittest\nfrom unittest.mock import MagicMock, patch\n",
        "decorator": "",
        "assert_eq": "self.assertEqual(",
        "assert_raises": "with self.assertRaises({exc}):",
        "mock_prefix": "mock_",
        "fixture_prefix": "def setUp(self):",
        "file_suffix": "_test.py",
    },
    TestFramework.JEST: {
        "imports": "const { mockFunction } = require('../test-utils');\n",
        "decorator": "",
        "assert_eq": "expect({actual}).toBe({expected});",
        "assert_raises": "expect(() => {fn}).toThrow();",
        "mock_prefix": "jest.mock(",
        "fixture_prefix": "beforeEach(() => {\n  jest.clearAllMocks();\n});",
        "file_suffix": ".test.js",
    },
    TestFramework.JUNIT: {
        "imports": "import org.junit.jupiter.api.Test;\nimport static org.junit.jupiter.api.Assertions.*;\nimport org.mockito.Mockito;\n",
        "decorator": "@Test\n",
        "assert_eq": "assertEquals({expected}, {actual});",
        "assert_raises": "assertThrows({exc}.class, () -> {fn});",
        "mock_prefix": "@Mock\n",
        "fixture_prefix": "@BeforeEach\nvoid setUp() {\n}",
        "file_suffix": "Test.java",
    },
}


class TestGenerator:
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url
        self._model = model or "gpt-4o"
        self._llm_client: Optional[Any] = None

    async def _ensure_llm(self) -> Any:
        if self._llm_client is None:
            from ai.reasoning_engine import LLMClient
            self._llm_client = LLMClient(
                api_key=self._api_key,
                base_url=self._base_url,
                model=self._model,
            )
        return self._llm_client

    async def generate_tests(self, request: TestRequest) -> GeneratedTest:
        if request.framework == TestFramework.PYTEST:
            return await self._generate_pytest(request)
        elif request.framework == TestFramework.UNITTEST:
            return await self._generate_unittest(request)
        elif request.framework == TestFramework.JEST:
            return await self._generate_jest(request)
        elif request.framework == TestFramework.JUNIT:
            return await self._generate_junit(request)
        elif request.framework == TestFramework.GO_TEST:
            return self._generate_go_test(request)
        elif request.framework == TestFramework.RUST_TEST:
            return self._generate_rust_test(request)
        else:
            return await self._generate_pytest(request)

    async def _generate_pytest(self, request: TestRequest) -> GeneratedTest:
        result = GeneratedTest(framework=TestFramework.PYTEST, test_type=request.test_type)
        functions, classes = self._parse_functions_and_classes(request.code)

        test_parts = [
            FRAMEWORK_CONFIGS[TestFramework.PYTEST]["imports"],
            "",
        ]

        if request.module_name:
            test_parts.append(f"from {request.module_name} import *")
            test_parts.append("")

        generated_tests: list[str] = []
        mocks_used: list[str] = []

        if classes:
            for cls_name in classes:
                if request.class_name and cls_name != request.class_name:
                    continue
                test_parts.append(f"\nclass Test{cls_name}:\n")
                test_parts.append(f'    """Test suite for {cls_name}."""\n')
                test_parts.append("    @pytest.fixture(autouse=True)\n")
                test_parts.append(f"    def setup_method(self):\n")
                test_parts.append(f"        self.instance = {cls_name}()\n")
                test_parts.append("")

                for func_name, func_info in functions:
                    if func_name.startswith("_"):
                        continue
                    test_func = self._generate_unit_test_function(
                        func_name, func_info, cls_name, TestFramework.PYTEST, request
                    )
                    generated_tests.append(test_func)

        if functions:
            for func_name, func_info in functions:
                if classes and not request.function_name:
                    continue
                if request.function_name and func_name != request.function_name:
                    continue
                if any(f"[{c}]" in func_name for c in classes):
                    continue
                test_func = self._generate_unit_test_function(
                    func_name, func_info, "", TestFramework.PYTEST, request
                )
                generated_tests.append(test_func)

        for test in generated_tests:
            test_parts.append(test)
            test_parts.append("")

        result.test_code = "\n".join(test_parts)

        result.coverage_estimate = self._estimate_coverage(
            request.code, result.test_code
        )

        return result

    async def _generate_unittest(self, request: TestRequest) -> GeneratedTest:
        result = GeneratedTest(framework=TestFramework.UNITTEST, test_type=request.test_type)
        functions, classes = self._parse_functions_and_classes(request.code)

        test_parts = [
            FRAMEWORK_CONFIGS[TestFramework.UNITTEST]["imports"],
            "",
            f"class Test{request.class_name or 'Module'}(unittest.TestCase):",
            "",
            "    def setUp(self):",
            "        pass",
            "",
        ]

        if request.module_name:
            test_parts.insert(1, f"from {request.module_name} import *")

        for func_name, func_info in functions:
            if func_name.startswith("_"):
                continue
            test = self._generate_unit_test_function(
                func_name, func_info, "", TestFramework.UNITTEST, request
            )
            test_parts.append(test)
            test_parts.append("")

        if test_parts:
            test_parts.append("if __name__ == '__main__':")
            test_parts.append("    unittest.main()")

        result.test_code = "\n".join(test_parts)
        result.coverage_estimate = self._estimate_coverage(
            request.code, result.test_code
        )
        return result

    async def _generate_jest(self, request: TestRequest) -> GeneratedTest:
        result = GeneratedTest(framework=TestFramework.JEST, test_type=request.test_type)

        test_parts = [
            FRAMEWORK_CONFIGS[TestFramework.JEST]["imports"],
            "",
            f"const {request.class_name.lower() or 'module'} = require('../src/{request.module_name}');",
            "",
            f"describe('{request.class_name or request.module_name}', () => {{",
        ]

        functions, classes = self._parse_functions_and_classes(request.code)
        for func_name, func_info in functions:
            if func_name.startswith("_"):
                continue
            test_parts.append(f"    describe('{func_name}', () => {{")
            test_parts.append(f"        test('should execute {func_name} correctly', () => {{")
            args = [a.arg for a in func_info.args if a.arg not in ("self", "cls")]
            test_args = ", ".join(f"'{a}'" for a in args) if args else ""
            test_parts.append(f"            const result = {request.class_name.lower() or 'module'}.{func_name}({test_args});")
            test_parts.append("            expect(result).toBeDefined();")
            test_parts.append("        });")
            test_parts.append("    });")

        test_parts.append("});")

        result.test_code = "\n".join(test_parts)
        result.coverage_estimate = self._estimate_coverage(
            request.code, result.test_code
        )
        return result

    async def _generate_junit(self, request: TestRequest) -> GeneratedTest:
        result = GeneratedTest(framework=TestFramework.JUNIT, test_type=request.test_type)

        test_parts = [
            FRAMEWORK_CONFIGS[TestFramework.JUNIT]["imports"],
            "",
            f"public class Test{request.class_name or 'Module'} {{",
            "",
        ]

        test_parts.append(f"    private {request.class_name or 'Module'} {request.class_name.lower() or 'module'} = new {request.class_name or 'Module'}();\n")

        functions, classes = self._parse_functions_and_classes(request.code)
        for func_name, func_info in functions:
            if func_name.startswith("_"):
                continue
            test_parts.append(f"    @Test")
            test_parts.append(f"    public void test{func_name.capitalize()}() {{")
            test_parts.append(f"        // TODO: implement test for {func_name}")
            test_parts.append(f"        assertNotNull({request.class_name.lower() or 'module'}.{func_name}());")
            test_parts.append(f"    }}")

        test_parts.append("}")

        result.test_code = "\n".join(test_parts)
        result.coverage_estimate = self._estimate_coverage(
            request.code, result.test_code
        )
        return result

    def _generate_go_test(self, request: TestRequest) -> GeneratedTest:
        result = GeneratedTest(framework=TestFramework.GO_TEST, test_type=request.test_type)

        package_name = request.module_name.split(".")[-1] if request.module_name else "main"
        test_parts = [
            f"package {package_name}\n",
            'import "testing"\n',
            f"func Test{request.class_name or 'Module'}(t *testing.T) {{",
            f'    // Test for {request.function_name or request.module_name}',
            "}",
        ]

        result.test_code = "\n".join(test_parts)
        result.coverage_estimate = 0.1
        return result

    def _generate_rust_test(self, request: TestRequest) -> GeneratedTest:
        result = GeneratedTest(framework=TestFramework.RUST_TEST, test_type=request.test_type)

        test_function = request.function_name or "feature"
        test_parts = [
            "#[cfg(test)]",
            "mod tests {",
            "    use super::*;\n",
            "    #[test]",
            f"    fn test_{test_function.lower().replace(' ', '_')}() {{",
            "        // TODO: implement test",
            "        assert!(true);",
            "    }",
            "}",
        ]

        result.test_code = "\n".join(test_parts)
        result.coverage_estimate = 0.1
        return result

    def _generate_unit_test_function(
        self,
        func_name: str,
        func_info: ast.FunctionDef,
        class_name: str,
        framework: TestFramework,
        request: TestRequest,
    ) -> str:
        config = FRAMEWORK_CONFIGS.get(framework, FRAMEWORK_CONFIGS[TestFramework.PYTEST])
        parts: list[str] = []

        test_method_name = f"test_{func_name}"
        parts.append(f"def {test_method_name}(self):")
        parts.append(f'    """Test the {func_name} function."""\n')

        args = [a.arg for a in func_info.args if a.arg not in ("self", "cls")]
        if args:
            mock_args = ", ".join(self._generate_test_data(a) for a in args[:3])
            if class_name:
                parts.append(f"    result = self.instance.{func_name}({mock_args})")
            else:
                parts.append(f"    result = {func_name}({mock_args})")
        else:
            if class_name:
                parts.append(f"    result = self.instance.{func_name}()")
            else:
                parts.append(f"    result = {func_name}()")

        if func_info.returns:
            return_type = self._get_return_type_name(func_info.returns)
            if return_type in ("bool", "int", "str", "list", "dict"):
                parts.append(f"    assert result is not None")
                parts.append(f"    assert isinstance(result, {self._get_type_check(return_type)})")
            else:
                parts.append("    assert result is not None")
        else:
            parts.append("    assert result is not None")

        return "\n".join(parts)

    def _generate_test_data(self, arg_name: str) -> str:
        if "name" in arg_name.lower():
            return "'test_name'"
        elif "id" in arg_name.lower():
            return "42"
        elif "count" in arg_name.lower() or "num" in arg_name.lower():
            return "10"
        elif "flag" in arg_name.lower() or "enable" in arg_name.lower():
            return "True"
        elif "data" in arg_name.lower() or "payload" in arg_name.lower():
            return "{'key': 'value'}"
        elif "list" in arg_name.lower() or "items" in arg_name.lower():
            return "[]"
        elif "config" in arg_name.lower():
            return "{'debug': False}"
        else:
            return "'test_value'"

    def _parse_functions_and_classes(
        self, code: str
    ) -> tuple[list[tuple[str, ast.FunctionDef]], list[str]]:
        functions: list[tuple[str, ast.FunctionDef]] = []
        classes: list[str] = []

        try:
            tree = ast.parse(code)
            for node in ast.iter_child_nodes(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                    for item in node.body:
                        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            functions.append((f"[{node.name}].{item.name}", item))
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    functions.append((node.name, node))
        except SyntaxError:
            pass

        return functions, classes

    def _get_return_type_name(self, node: ast.AST) -> str:
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Subscript):
            if isinstance(node.value, ast.Name):
                return node.value.id
        elif isinstance(node, ast.Constant):
            return str(node.value)
        return "Any"

    def _get_type_check(self, type_name: str) -> str:
        mapping = {
            "bool": "bool",
            "int": "int",
            "str": "str",
            "list": "list",
            "dict": "dict",
            "float": "float",
            "tuple": "tuple",
            "set": "set",
            "Optional": "type(None)",
            "Any": "object",
        }
        return mapping.get(type_name, "object")

    def _estimate_coverage(self, source_code: str, test_code: str) -> float:
        source_functions, source_classes = self._parse_functions_and_classes(source_code)
        test_functions, _ = self._parse_functions_and_classes(test_code)

        if not source_functions:
            return 1.0

        covered = 0
        for func_name, _ in source_functions:
            for test_func_name, _ in test_functions:
                if func_name.replace(".", "_") in test_func_name:
                    covered += 1
                    break

        return covered / len(source_functions)

    async def generate_integration_tests(
        self, request: TestRequest
    ) -> GeneratedTest:
        result = GeneratedTest(
            framework=request.framework,
            test_type=TestType.INTEGRATION,
        )

        if request.framework == TestFramework.PYTEST:
            test_parts = [
                "import pytest\n",
                f"class Test{request.class_name or 'Module'}Integration:\n",
                '    """Integration tests."""\n',
                "    @pytest.mark.integration\n",
                f"    async def test_{request.function_name or 'full_workflow'}_integration(self):",
                "        # TODO: implement integration test",
                "        pass",
            ]
            result.test_code = "\n".join(test_parts)

        result.coverage_estimate = 0.5
        return result

    def generate_test_data(
        self,
        type_hint: str,
        count: int = 1,
    ) -> list[Any]:
        generators = {
            "int": lambda: random.randint(-1000, 1000),
            "float": lambda: round(random.uniform(-1000.0, 1000.0), 2),
            "str": lambda: ''.join(random.choices(string.ascii_lowercase, k=8)),
            "bool": lambda: random.choice([True, False]),
            "list": lambda: [random.randint(0, 100) for _ in range(random.randint(1, 5))],
            "dict": lambda: {f"key_{i}": random.randint(0, 100) for i in range(random.randint(1, 4))},
            "None": lambda: None,
        }

        gen = generators.get(type_hint, generators["str"])
        return [gen() for _ in range(count)]

    def suggest_test_maintenance(
        self, source_code: str, existing_tests: str
    ) -> list[str]:
        suggestions: list[str] = []
        source_funcs, source_classes = self._parse_functions_and_classes(source_code)
        test_funcs, _ = self._parse_functions_and_classes(existing_tests)

        source_func_names = {
            f[0].split("].")[-1].replace(".", "_") for f in source_funcs
        }
        test_func_names = {f[0].replace(".", "_") for f in test_funcs}

        for func_name in source_func_names:
            tested = any(func_name in tf for tf in test_func_names)
            if not tested:
                suggestions.append(f"No test found for function: {func_name}")

        test_func_names_clean = {f.split("test_")[-1] for f in test_func_names if "test_" in f}
        for tf in test_func_names_clean:
            if tf not in source_func_names:
                pass

        coverage_ratio = len(test_func_names & source_func_names) / max(len(source_func_names), 1)
        if coverage_ratio < 0.5:
            suggestions.append(
                f"Low test coverage ({coverage_ratio:.0%}). Consider adding tests for uncovered functions."
            )

        return suggestions

    async def close(self) -> None:
        if self._llm_client:
            await self._llm_client.close()
