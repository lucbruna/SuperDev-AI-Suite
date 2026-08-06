"""Unit tests for the AI Code Knowledge Graph parser package (phase 2).

Covers the normalized entity model, the stdlib Python AST extractor and every
language parser (python, javascript, typescript, json, yaml, xml, markdown,
docker, git, plugin, workflow, database).
"""
from __future__ import annotations

import pytest

from modules.ai_code_knowledge_graph.ast.entities import make_entity
from modules.ai_code_knowledge_graph.parsers import parse_text
from modules.ai_code_knowledge_graph.parsers import (
    database_parser,
    docker_parser,
    git_parser,
    javascript_parser,
    json_parser,
    markdown_parser,
    plugin_parser,
    python_parser,
    typescript_parser,
    workflow_parser,
    xml_parser,
    yaml_parser,
)


def _kinds(result) -> list[str]:
    return [entity["kind"] for entity in result["entities"]]


def _names(result, kind: str) -> list[str]:
    return [entity["name"] for entity in result["entities"] if entity["kind"] == kind]


# ------------------------------------------------------------ entity helpers
class TestEntityModel:
    def test_make_entity_drops_none(self) -> None:
        entity = make_entity("function", "main", 1, 5, params=["a"], module=None)
        assert entity["kind"] == "function"
        assert entity["name"] == "main"
        assert entity["start_line"] == 1
        assert entity["end_line"] == 5
        assert entity["params"] == ["a"]
        assert "module" not in entity


# ------------------------------------------------------------ python parser
class TestPythonParser:
    SAMPLE = (
        "import os\n"
        "from lib import helper as h\n"
        "\n"
        "@decorator\n"
        "class Service(Base):\n"
        "    def __init__(self):\n"
        "        pass\n"
        "    @staticmethod\n"
        "    def run(self):\n"
        "        pass\n"
        "\n"
        "async def fetch():\n"
        "    return h()\n"
    )

    def test_imports(self) -> None:
        result = python_parser.parse(self.SAMPLE, "app.py")
        imports = [e for e in result["entities"] if e["kind"] == "import"]
        assert ("os", None) in [(e["name"], e.get("source")) for e in imports]
        helper = next(e for e in imports if e["name"] == "helper")
        assert helper["source"] == "lib"
        assert helper["alias"] == "h"

    def test_class_with_methods(self) -> None:
        result = python_parser.parse(self.SAMPLE, "app.py")
        classes = [e for e in result["entities"] if e["kind"] == "class"]
        assert len(classes) == 1
        service = classes[0]
        assert service["name"] == "Service"
        assert service["bases"] == ["Base"]
        assert service["decorators"] == ["decorator"]
        method_names = [m["name"] for m in service["methods"]]
        assert "__init__" in method_names
        assert "run" in method_names
        run = next(m for m in service["methods"] if m["name"] == "run")
        assert run["static"] is True

    def test_functions(self) -> None:
        result = python_parser.parse(self.SAMPLE, "app.py")
        functions = [e for e in result["entities"] if e["kind"] == "function"]
        assert [f["name"] for f in functions] == ["fetch"]
        assert functions[0]["async_"] is True

    def test_file_entity_first(self) -> None:
        result = python_parser.parse("x = 1\n", "app.py")
        assert result["entities"][0]["kind"] == "file"
        assert result["entities"][0]["name"] == "app.py"
        assert result["error"] is None

    def test_syntax_error(self) -> None:
        result = python_parser.parse("def broken(:\n", "bad.py")
        assert result["error"] is not None
        assert result["entities"] == []


# ------------------------------------------------------------- js/ts parsers
class TestJavaScriptParser:
    SAMPLE = (
        "import { foo } from 'lib'\n"
        "const util = require('./util')\n"
        "\n"
        "export class Button extends Base {\n"
        "  render() { return null }\n"
        "}\n"
        "export function helper() {}\n"
        "const arrow = (a) => a\n"
    )

    def test_imports_and_functions(self) -> None:
        result = javascript_parser.parse(self.SAMPLE, "app.js")
        assert "lib" in _names(result, "import")
        util = next(e for e in result["entities"] if e["kind"] == "import" and e["name"] == "util")
        assert util["source"] == "./util"
        classes = [e for e in result["entities"] if e["kind"] == "class"]
        assert classes[0]["name"] == "Button"
        assert classes[0]["bases"] == ["Base"]
        assert classes[0]["exported"] is True
        functions = [e for e in result["entities"] if e["kind"] == "function"]
        function_names = {f["name"] for f in functions}
        assert {"helper", "arrow"} <= function_names


class TestTypeScriptParser:
    SAMPLE = (
        "import type { User } from './user'\n"
        "interface Props { id: number }\n"
        "type State = { count: number }\n"
        "export enum Status { Active }\n"
        "export function render(p: Props) {}\n"
    )

    def test_ts_declarations(self) -> None:
        result = typescript_parser.parse(self.SAMPLE, "app.ts")
        assert "Props" in _names(result, "interface")
        assert "State" in _names(result, "type")
        assert "Status" in _names(result, "enum")
        assert "render" in _names(result, "function")


# --------------------------------------------------------- config parsers
class TestJsonParser:
    def test_valid_document(self) -> None:
        result = json_parser.parse('{"name": "demo", "nested": {"enabled": true}}', "c.json")
        assert result["error"] is None
        assert _names(result, "config") == ["name", "nested", "nested.enabled"]

    def test_invalid_document(self) -> None:
        result = json_parser.parse("{oops", "c.json")
        assert result["error"] is not None
        assert "line" in result["error"]


class TestYamlParser:
    def test_top_level_keys(self) -> None:
        result = yaml_parser.parse("name: demo\nenabled: true\n", "c.yaml")
        assert "name" in _names(result, "config")
        assert result["error"] is None


class TestXmlParser:
    def test_elements(self) -> None:
        result = xml_parser.parse("<root><item id=\"1\">x</item></root>", "c.xml")
        assert _names(result, "config") == ["root", "root/item"]
        assert result["error"] is None

    def test_invalid_xml(self) -> None:
        result = xml_parser.parse("<root><broken></root>", "c.xml")
        assert result["error"] is not None


# ------------------------------------------------------------ markdown parser
class TestMarkdownParser:
    SAMPLE = (
        "---\ntitle: Demo\n---\n"
        "# Heading One\n\nSome text with a [link](https://example.com).\n\n"
        "```python\nprint('hi')\n```\n\n## Sub\n"
    )

    def test_sections_links_blocks(self) -> None:
        result = markdown_parser.parse(self.SAMPLE, "doc.md")
        sections = [e for e in result["entities"] if e["kind"] == "section"]
        assert ("Heading One", 1) in [(s["name"], s["level"]) for s in sections]
        assert any(e["kind"] == "link" and e["target"] == "https://example.com" for e in result["entities"])
        blocks = [e for e in result["entities"] if e["kind"] == "code_block"]
        assert blocks and blocks[0]["language"] == "python"
        assert any(e["kind"] == "config" and e["name"] == "title" for e in result["entities"])


# ------------------------------------------------------------ docker parser
class TestDockerParser:
    SAMPLE = "FROM python:3.12 AS base\nWORKDIR /app\nRUN pip install -r requirements.txt\nENV DEBUG=1\n"

    def test_instructions_and_deps(self) -> None:
        result = docker_parser.parse(self.SAMPLE, "Dockerfile")
        deps = [e for e in result["entities"] if e["kind"] == "dependency"]
        assert deps[0]["name"] == "python:3.12"
        instructions = [e["name"] for e in result["entities"] if e["kind"] == "instruction"]
        assert {"FROM", "WORKDIR", "RUN", "ENV"} <= set(instructions)
        assert any(e["kind"] == "config" and e["name"] == "DEBUG" for e in result["entities"])


# -------------------------------------------------------------- git parser
class TestGitParser:
    def test_gitmodules(self) -> None:
        text = "[submodule \"libs/core\"]\n\tpath = libs/core\n\turl = https://github.com/x/core.git\n"
        result = git_parser.parse(text, ".gitmodules")
        assert any(e["name"] == "libs/core" and e["value"] == "submodule" for e in result["entities"])
        assert any(e["name"] == "path" and e["value"] == "libs/core" for e in result["entities"])


# ------------------------------------------------------------ plugin parser
class TestPluginParser:
    def test_plugin_json(self) -> None:
        text = '{"name": "demo-plugin", "version": "1.0.0", "entry": "src/index.js", "dependencies": ["@x/util"]}'
        result = plugin_parser.parse(text, "plugins/demo/plugin.json")
        plugins = [e for e in result["entities"] if e["kind"] == "plugin"]
        assert plugins[0]["name"] == "demo-plugin"
        assert plugins[0]["version"] == "1.0.0"
        assert plugins[0]["dependencies"] == ["@x/util"]
        assert result["error"] is None


# ---------------------------------------------------------- workflow parser
class TestWorkflowParser:
    def test_workflow(self) -> None:
        text = "name: CI\non: [push, pull_request]\njobs:\n  build:\n    steps:\n      - run: echo hi\n"
        result = workflow_parser.parse(text, "workflows/ci.yml")
        workflows = [e for e in result["entities"] if e["kind"] == "workflow"]
        assert workflows[0]["name"] == "CI"
        assert workflows[0]["triggers"] == ["push", "pull_request"]
        assert workflows[0]["jobs"] == ["build"]
        assert workflows[0]["steps"] == 1


# --------------------------------------------------------- database parser
class TestDatabaseParser:
    def test_sql_tables(self) -> None:
        text = (
            "CREATE TABLE users (\n"
            "  id INTEGER PRIMARY KEY,\n"
            "  email TEXT NOT NULL\n"
            ");\n"
            "CREATE INDEX idx_users_email ON users (email);\n"
            "CREATE VIEW active_users AS SELECT * FROM users;\n"
        )
        result = database_parser.parse(text, "db/schema.sql")
        tables = [e for e in result["entities"] if e["kind"] == "table"]
        assert tables[0]["name"] == "users"
        assert set(tables[0]["columns"]) >= {"id", "email"}
        assert "idx_users_email" in _names(result, "index")
        assert "active_users" in _names(result, "view")

    def test_prisma_models(self) -> None:
        text = "model User {\n  id Int @id\n  email String\n}\nenum Role {\n  ADMIN\n  USER\n}\n"
        result = database_parser.parse(text, "schema.prisma")
        tables = [e for e in result["entities"] if e["kind"] == "table"]
        assert tables[0]["name"] == "User"
        assert set(tables[0]["columns"]) >= {"id", "email"}
        assert "Role" in _names(result, "enum")


# ------------------------------------------------------------- dispatcher
class TestParseTextDispatcher:
    def test_dispatch(self) -> None:
        result = parse_text("python", "def main():\n    pass\n", "app.py")
        assert result["language"] == "python"
        assert "main" in _names(result, "function")

    def test_unknown_language(self) -> None:
        result = parse_text("cobol", "hello", "x.cob")
        assert result["error"] is not None

    def test_parsers_registered(self) -> None:
        from modules.ai_code_knowledge_graph.core.knowledge_registry import default_registry

        registry = default_registry()
        assert {"python", "javascript", "typescript", "json", "yaml", "xml", "markdown"} <= set(
            registry.names("parser")
        )
        assert {"docker", "git", "plugin", "workflow", "database"} <= set(registry.names("parser"))
