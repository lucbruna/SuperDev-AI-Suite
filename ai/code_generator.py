from __future__ import annotations

import asyncio
import difflib
import logging
import re
import subprocess  # nosec
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger("superdev.ai.codegen")


class Language(str, Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    GO = "go"
    RUST = "rust"
    JAVA = "java"


class GenerationMethod(str, Enum):
    LLM = "llm"
    TEMPLATE = "template"
    HYBRID = "hybrid"


@dataclass
class GenerationRequest:
    description: str
    language: Language = Language.PYTHON
    method: GenerationMethod = GenerationMethod.LLM
    context: Optional[str] = None
    dependencies: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    include_tests: bool = True
    include_docstrings: bool = True
    style_guide: str = ""
    max_tokens: int = 4096
    temperature: float = 0.3
    additional_instructions: Optional[str] = None
    existing_code: Optional[str] = None


@dataclass
class GeneratedCode:
    code: str
    tests: Optional[str] = None
    language: Language = Language.PYTHON
    file_path: Optional[str] = None
    token_usage: dict[str, int] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    formatted: bool = False
    lint_passed: bool = False
    lint_errors: list[str] = field(default_factory=list)


@dataclass
class CodeReviewFeedback:
    original_code: str = ""
    suggestions: list[str] = field(default_factory=list)
    issues: list[str] = field(default_factory=list)
    rating: int = 5


LANGUAGE_EXTENSIONS: dict[Language, str] = {
    Language.PYTHON: ".py",
    Language.JAVASCRIPT: ".js",
    Language.TYPESCRIPT: ".ts",
    Language.GO: ".go",
    Language.RUST: ".rs",
    Language.JAVA: ".java",
}

LANGUAGE_COMMENTS: dict[Language, tuple[str, str]] = {
    Language.PYTHON: ("#", '"""'),
    Language.JAVASCRIPT: ("//", "/*"),
    Language.TYPESCRIPT: ("//", "/*"),
    Language.GO: ("//", "/*"),
    Language.RUST: ("//", "/*"),
    Language.JAVA: ("//", "/*"),
}

TEMPLATES: dict[Language, dict[str, str]] = {
    Language.PYTHON: {
        "module": '''"""${description}"""

from __future__ import annotations

from typing import Any, Optional


class ${class_name}:
    """${description}"""

    def __init__(self) -> None:
        pass

    def __repr__(self) -> str:
        return f"${class_name}()"
''',
        "function": '''def ${function_name}(${params}) -> ${return_type}:
    """${description}"""
    ${body}
''',
    },
    Language.JAVASCRIPT: {
        "module": '''/**
 * ${description}
 */

class ${class_name} {
    constructor() {
    }

    /**
     * ${description}
     */
}

module.exports = { ${class_name} };
''',
    },
    Language.TYPESCRIPT: {
        "module": '''/**
 * ${description}
 */

export class ${class_name} {
    constructor() {
    }

    /**
     * ${description}
     */
}
''',
    },
    Language.GO: {
        "module": '''package ${package_name}

// ${description}
type ${struct_name} struct {
}

// New${struct_name} creates a new ${struct_name}
func New${struct_name}() *${struct_name} {
    return &${struct_name}{}
}
''',
    },
    Language.RUST: {
        "module": '''/// ${description}
pub struct ${struct_name} {
}

impl ${struct_name} {
    /// Creates a new ${struct_name}
    pub fn new() -> Self {
        Self {}
    }
}
''',
    },
    Language.JAVA: {
        "module": '''package ${package_name};

/**
 * ${description}
 */
public class ${class_name} {
    public ${class_name}() {
    }
}
''',
    },
}

TEST_TEMPLATES: dict[Language, str] = {
    Language.PYTHON: '''"""Tests for ${module_name}."""

import pytest
from ${module_path} import ${class_name}


class Test${class_name}:
    """Test suite for ${class_name}."""

    def test_initialization(self) -> None:
        """Test basic initialization."""
        instance = ${class_name}()
        assert instance is not None

    def test_${test_name}(self) -> None:
        """Test ${description}."""
        pass
''',
    Language.JAVASCRIPT: '''const { ${class_name} } = require("../${module_path}");

describe("${class_name}", () => {
    test("should initialize correctly", () => {
        const instance = new ${class_name}();
        expect(instance).toBeDefined();
    });
});
''',
    Language.TYPESCRIPT: '''import { ${class_name} } from "../${module_path}";

describe("${class_name}", () => {
    test("should initialize correctly", () => {
        const instance = new ${class_name}();
        expect(instance).toBeDefined();
    });
});
''',
}


def _format_llm_messages(request: GenerationRequest) -> list[dict[str, str]]:
    lang_name = request.language.value
    system = (
        f"You are a code generation engine. Generate {lang_name} code based on the description.\n"
        f"Follow {request.style_guide or 'PEP 8' if request.language == Language.PYTHON else 'standard conventions'}.\n"
        f"Return ONLY the code block, no explanation.\n"
        f"Use the ```{lang_name} code block format.\n"
    )
    if request.include_docstrings:
        system += "Include comprehensive docstrings/comments.\n"
    if request.constraints:
        system += "Constraints:\n" + "\n".join(f"- {c}" for c in request.constraints)
    if request.additional_instructions:
        system += f"\n{request.additional_instructions}"

    user_parts = [f"Generate {lang_name} code for: {request.description}"]
    if request.context:
        user_parts.append(f"\nContext:\n{request.context}")
    if request.dependencies:
        user_parts.append(f"\nDependencies: {', '.join(request.dependencies)}")
    if request.existing_code:
        user_parts.append(f"\nExisting code to extend:\n{request.existing_code}")

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": "\n".join(user_parts)},
    ]


def _format_test_messages(request: GenerationRequest, code: str) -> list[dict[str, str]]:
    lang_name = request.language.value
    system = (
        f"You are a test generation engine. Generate {lang_name} tests for the provided code.\n"
        f"Use pytest for Python, Jest for JS/TS, Go test for Go, #[cfg(test)] for Rust, JUnit for Java.\n"
        f"Return ONLY the test code block.\n"
    )

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": f"Generate tests for this {lang_name} code:\n\n{code}"},
    ]


class CodeGenerator:
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        format_enabled: bool = True,
        lint_enabled: bool = True,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url
        self._model = model or "gpt-4o"
        self._format_enabled = format_enabled
        self._lint_enabled = lint_enabled
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

    def _extract_code_block(self, text: str, language: Language) -> str:
        pattern = rf"```{language.value}\n?(.*?)```"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()
        pattern2 = r"```\n?(.*?)```"
        match2 = re.search(pattern2, text, re.DOTALL)
        if match2:
            return match2.group(1).strip()
        return text.strip()

    async def generate(
        self, request: GenerationRequest
    ) -> GeneratedCode:
        result = GeneratedCode(language=request.language)

        if request.method == GenerationMethod.TEMPLATE:
            code = self._generate_from_template(request)
            result.code = code
            result.warnings.append("Template generation may produce generic code")
        elif request.method == GenerationMethod.LLM:
            code, token_usage = await self._generate_via_llm(request)
            result.code = code
            result.token_usage = token_usage
        else:
            code, token_usage = await self._generate_via_llm(request)
            result.code = code
            result.token_usage = token_usage
            template_code = self._generate_from_template(request)
            if template_code:
                result.warnings.append("Hybrid mode used LLM result; template available for reference")

        result.code = self._fix_indentation(result.code, request.language)
        result.file_path = self._suggest_file_path(request)

        if self._format_enabled:
            formatted = await self._format_code(result.code, request.language)
            if formatted:
                result.code = formatted
                result.formatted = True
            else:
                result.warnings.append("Code formatting unavailable or failed")

        if self._lint_enabled:
            lint_ok, errors = await self._lint_code(result.code, request.language)
            result.lint_passed = lint_ok
            result.lint_errors = errors
            if not lint_ok:
                result.warnings.append(f"Lint found {len(errors)} issue(s)")

        if request.include_tests:
            tests = await self._generate_tests(request, result.code)
            result.tests = tests

        return result

    def _generate_from_template(self, request: GenerationRequest) -> str:
        lang_templates = TEMPLATES.get(request.language, {})
        template = lang_templates.get("module")
        if not template:
            return f"# {request.description}\n# No template available for {request.language.value}\n"

        class_name = self._infer_class_name(request.description)
        package_name = "main" if request.language == Language.GO else "com.example"

        replacements = {
            "${description}": request.description,
            "${class_name}": class_name,
            "${package_name}": package_name,
            "${struct_name}": class_name,
            "${module_name}": class_name.lower(),
        }

        result = template
        for key, val in replacements.items():
            result = result.replace(key, val)
        return result

    def _infer_class_name(self, description: str) -> str:
        words = description.split()
        important = [w for w in words if w[0].isupper()] if any(w[0].isupper() for w in words) else words
        if not important:
            return "GeneratedModule"
        name = "".join(w.capitalize() for w in important[:3])
        name = re.sub(r"[^a-zA-Z0-9_]", "", name)
        return name or "GeneratedModule"

    async def _generate_via_llm(
        self, request: GenerationRequest
    ) -> tuple[str, dict[str, int]]:
        llm = await self._ensure_llm()
        messages = _format_llm_messages(request)
        content, usage = await llm.chat(
            messages, temperature=request.temperature, max_tokens=request.max_tokens
        )
        code = self._extract_code_block(content, request.language)
        return code, usage.to_dict()

    async def _generate_tests(
        self, request: GenerationRequest, code: str
    ) -> Optional[str]:
        llm = await self._ensure_llm()
        messages = _format_test_messages(request, code)
        try:
            content, _ = await llm.chat(
                messages, temperature=0.2, max_tokens=2048
            )
            tests = self._extract_code_block(content, request.language)
            return tests
        except Exception as exc:
            logger.warning("Test generation failed: %s", exc)
            template = TEST_TEMPLATES.get(request.language)
            if template:
                class_name = self._infer_class_name(request.description)
                module_path = self._suggest_file_path(request) or class_name.lower()
                module_path = Path(module_path).stem
                test_name = request.description.split()[0].lower() if request.description.split() else "feature"
                return template.replace("${class_name}", class_name).replace(
                    "${module_path}", module_path
                ).replace(
                    "${module_name}", class_name.lower()
                ).replace(
                    "${test_name}", test_name
                ).replace(
                    "${description}", request.description
                )
            return None

    def _fix_indentation(self, code: str, language: Language) -> str:
        lines = code.split("\n")
        if not lines:
            return code
        non_empty = [i for i, l in enumerate(lines) if l.strip()]
        if not non_empty:
            return code
        first_content = min(non_empty)
        indent = len(lines[first_content]) - len(lines[first_content].lstrip())
        if indent > 0:
            lines = [l[indent:] if l.strip() else "" for l in lines]
        return "\n".join(lines)

    def _suggest_file_path(self, request: GenerationRequest) -> str:
        class_name = self._infer_class_name(request.description)
        ext = LANGUAGE_EXTENSIONS.get(request.language, ".txt")
        return f"{class_name.lower()}{ext}"

    async def _format_code(self, code: str, language: Language) -> Optional[str]:
        formatters = {
            Language.PYTHON: ("black", ["-"]),
            Language.JAVASCRIPT: ("npx", ["prettier", "--parser", "babel"]),
            Language.TYPESCRIPT: ("npx", ["prettier", "--parser", "typescript"]),
            Language.GO: ("gofmt", []),
            Language.RUST: ("rustfmt", []),
        }

        formatter_cmd = formatters.get(language)
        if not formatter_cmd:
            return None

        try:
            proc = await asyncio.create_subprocess_exec(
                formatter_cmd[0],
                *formatter_cmd[1],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate(code.encode("utf-8"), timeout=15.0)
            if proc.returncode == 0:
                return stdout.decode("utf-8").strip()
            logger.debug("Formatter failed for %s: %s", language.value, stderr.decode())
            return None
        except (FileNotFoundError, asyncio.TimeoutError, OSError) as exc:
            logger.debug("Formatter unavailable for %s: %s", language.value, exc)
            return None

    async def _lint_code(self, code: str, language: Language) -> tuple[bool, list[str]]:
        linters = {
            Language.PYTHON: ("python", ["-m", "pylint", "--from-stdin", "input.py"]),
        }

        linter_cmd = linters.get(language)
        if not linter_cmd:
            return True, []

        try:
            proc = await asyncio.create_subprocess_exec(
                linter_cmd[0],
                *linter_cmd[1],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            _, stderr = await proc.communicate(code.encode("utf-8"), timeout=15.0)
            output = stderr.decode("utf-8")
            errors = [line.strip() for line in output.split("\n") if line.strip() and ":" in line]
            return proc.returncode == 0, errors[:20]
        except (FileNotFoundError, asyncio.TimeoutError, OSError) as exc:
            logger.debug("Linter unavailable for %s: %s", language.value, exc)
            return True, []

    async def generate_from_description(
        self,
        description: str,
        language: Language = Language.PYTHON,
        **kwargs: Any,
    ) -> GeneratedCode:
        request = GenerationRequest(description=description, language=language, **kwargs)
        return await self.generate(request)

    async def incorporate_feedback(
        self,
        original_code: str,
        feedback: CodeReviewFeedback,
        language: Language = Language.PYTHON,
    ) -> GeneratedCode:
        llm = await self._ensure_llm()
        messages = [
            {
                "role": "system",
                "content": (
                    f"You are a code improvement engine. Given {language.value} code and review feedback, "
                    "produce an improved version. Return ONLY the improved code in a code block."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Original code:\n```{language.value}\n{original_code}\n```\n\n"
                    f"Review feedback (rating: {feedback.rating}/10):\n"
                    f"Issues: {', '.join(feedback.issues)}\n"
                    f"Suggestions: {', '.join(feedback.suggestions)}\n\n"
                    "Please incorporate this feedback and produce improved code."
                ),
            },
        ]
        content, _ = await llm.chat(messages, temperature=0.3, max_tokens=4096)
        return GeneratedCode(
            code=self._extract_code_block(content, language),
            language=language,
            formatted=True,
        )

    def generate_diff(self, original: str, updated: str) -> str:
        original_lines = original.splitlines(keepends=True)
        updated_lines = updated.splitlines(keepends=True)
        diff = difflib.unified_diff(
            original_lines,
            updated_lines,
            fromfile="original",
            tofile="updated",
        )
        return "".join(diff)

    async def close(self) -> None:
        if self._llm_client:
            await self._llm_client.close()
