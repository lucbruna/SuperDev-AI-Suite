"""Comprehensive tests for software_factory subsystem — Volume 32."""
import os
import sys

# Ensure software_factory is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# ---------- CORE FACTORY TESTS ----------

class TestFactoryEngine:
    def test_import(self):
        from software_factory.factory_engine import SoftwareFactoryEngine
        assert SoftwareFactoryEngine is not None

    def test_create_project(self):
        from software_factory.factory_engine import ProjectStatus, SoftwareFactoryEngine
        engine = SoftwareFactoryEngine()
        proj = engine.create_project("TestApp", "A test application", "alice")
        assert proj.name == "TestApp"
        assert proj.owner == "alice"
        assert proj.status == ProjectStatus.PLANNING

    def test_advance_phase(self):
        from software_factory.factory_engine import FactoryPhase, SoftwareFactoryEngine
        engine = SoftwareFactoryEngine()
        proj = engine.create_project("PhaseTest")
        assert proj.phase == FactoryPhase.IDEATION
        engine.advance_phase(proj.project_id)
        assert proj.phase == FactoryPhase.REQUIREMENTS

    def test_set_status(self):
        from software_factory.factory_engine import ProjectStatus, SoftwareFactoryEngine
        engine = SoftwareFactoryEngine()
        proj = engine.create_project("StatusTest")
        engine.set_status(proj.project_id, ProjectStatus.DEPLOYED)
        assert proj.status == ProjectStatus.DEPLOYED

    def test_list_projects(self):
        from software_factory.factory_engine import SoftwareFactoryEngine
        engine = SoftwareFactoryEngine()
        engine.create_project("A")
        engine.create_project("B")
        assert len(engine.list_projects()) == 2

    def test_count(self):
        from software_factory.factory_engine import SoftwareFactoryEngine
        engine = SoftwareFactoryEngine()
        assert engine.count() == 0
        engine.create_project("X")
        assert engine.count() == 1


class TestFactoryManager:
    def test_add_artifact(self):
        from software_factory.factory_manager import FactoryManager
        mgr = FactoryManager()
        art = mgr.add_artifact("proj1", "main.py", "code", content="print('hi')")
        assert art.name == "main.py"
        assert art.project_id == "proj1"

    def test_list_artifacts(self):
        from software_factory.factory_manager import FactoryManager
        mgr = FactoryManager()
        mgr.add_artifact("p1", "a.py")
        mgr.add_artifact("p1", "b.py")
        mgr.add_artifact("p2", "c.py")
        assert len(mgr.artifacts["p1"]) == 2


class TestFactoryRuntime:
    def test_submit_task(self):
        from software_factory.factory_runtime import FactoryRuntime, TaskState
        rt = FactoryRuntime()
        task = rt.submit_task("proj1", "Build module", {"src": "main.py"})
        assert task.name == "Build module"
        assert task.state == TaskState.PENDING

    def test_execute_task(self):
        from software_factory.factory_runtime import FactoryRuntime, TaskState
        rt = FactoryRuntime()
        task = rt.submit_task("proj1", "Test")
        result = rt.execute_task(task.task_id)
        assert result is True
        assert task.state == TaskState.COMPLETED


class TestFactoryRegistry:
    def test_register_component(self):
        from software_factory.factory_registry import FactoryRegistry
        reg = FactoryRegistry()
        comp = reg.register("c1", "CodeGen", component_type="generator")
        assert comp.name == "CodeGen"
        assert comp.component_type == "generator"

    def test_get_component(self):
        from software_factory.factory_registry import FactoryRegistry
        reg = FactoryRegistry()
        reg.register("c1", "TestComp")
        assert reg.get("c1") is not None
        assert reg.get("nonexistent") is None


class TestFactoryContext:
    def test_set_get(self):
        from software_factory.factory_context import FactoryContext
        ctx = FactoryContext()
        ctx.set("key1", "value1")
        assert ctx.get("key1") == "value1"

    def test_project_context(self):
        from software_factory.factory_context import FactoryContext
        ctx = FactoryContext()
        ctx.set("db", "postgres", project_id="p1")
        assert ctx.get("db", project_id="p1") == "postgres"


class TestFactoryEvents:
    def test_publish_event(self):
        from software_factory.factory_events import FactoryEventBus, FactoryEventType
        bus = FactoryEventBus()
        event = bus.publish(FactoryEventType.PROJECT_CREATED, "p1", {"name": "App"})
        assert event.event_type == FactoryEventType.PROJECT_CREATED

    def test_subscribe(self):
        from software_factory.factory_events import FactoryEventBus, FactoryEventType
        bus = FactoryEventBus()
        received = []
        bus.subscribe(FactoryEventType.TEST_PASSED, lambda e: received.append(e))
        bus.publish(FactoryEventType.TEST_PASSED, "p1")
        assert len(received) == 1


class TestFactoryMetrics:
    def test_record_metric(self):
        from software_factory.factory_metrics import FactoryMetrics
        m = FactoryMetrics()
        m.record("build_time", 12.5, unit="seconds")
        summary = m.get_summary("build_time")
        assert summary.count == 1
        assert summary.latest == 12.5


class TestFactoryLogger:
    def test_log_entry(self):
        from software_factory.factory_logger import FactoryLogger, LogLevel
        logger = FactoryLogger()
        logger.log(LogLevel.INFO, "Build started", source="build")
        assert len(logger.entries) == 1
        assert logger.entries[0].message == "Build started"

    def test_filter_by_level(self):
        from software_factory.factory_logger import FactoryLogger, LogLevel
        logger = FactoryLogger()
        logger.log(LogLevel.INFO, "info1")
        logger.log(LogLevel.ERROR, "err1")
        logger.log(LogLevel.WARNING, "warn1")
        errors = logger.get_entries(level=LogLevel.ERROR)
        assert len(errors) == 1


class TestFactorySecurity:
    def test_report_issue(self):
        from software_factory.factory_security import FactorySecurity, SecurityCheck, SecuritySeverity
        sec = FactorySecurity()
        issue = sec.report_issue(SecurityCheck.XSS, SecuritySeverity.HIGH, "XSS in template")
        assert issue.severity == SecuritySeverity.HIGH

    def test_resolve_issue(self):
        from software_factory.factory_security import FactorySecurity, SecurityCheck, SecuritySeverity
        sec = FactorySecurity()
        issue = sec.report_issue(SecurityCheck.SQL_INJECTION, SecuritySeverity.MEDIUM, "SQLi")
        sec.resolve_issue(issue.issue_id)
        assert issue.resolved is True

    def test_get_score(self):
        from software_factory.factory_security import FactorySecurity
        sec = FactorySecurity()
        sec.scan_project("p1", ["a.py", "b.py"])
        score = sec.get_score("p1")
        assert score <= 100.0


class TestFactoryModels:
    def test_tech_stack(self):
        from software_factory.factory_models import DatabaseType, Language, TechStack
        ts = TechStack(language=Language.PYTHON, database=DatabaseType.SQLITE)
        assert ts.language == Language.PYTHON

    def test_code_file(self):
        from software_factory.factory_models import CodeFile, Language
        cf = CodeFile(file_id="f1", path="src/main.py", language=Language.PYTHON, content="hello")
        assert cf.path == "src/main.py"


class TestFactoryConfig:
    def test_set_get(self):
        from software_factory.factory_config import FactoryConfig
        cfg = FactoryConfig()
        cfg.set("max_workers", 8)
        assert cfg.get("max_workers") == 8

    def test_default(self):
        from software_factory.factory_config import FactoryConfig
        cfg = FactoryConfig()
        assert cfg.get("missing", "fallback") == "fallback"


class TestFactoryProtocols:
    def test_register_protocol(self):
        from software_factory.factory_protocols import FactoryProtocols, ProtocolType
        fp = FactoryProtocols()
        cfg = fp.register("api", ProtocolType.REST, base_url="http://localhost")
        assert cfg.name == "api"
        assert fp.count() == 1


# ---------- REQUIREMENTS SUBSYSTEM TESTS ----------

class TestRequirementsModels:
    def test_requirement_creation(self):
        from software_factory.requirements.models import Requirement, RequirementType
        req = Requirement(title="Login feature", description="Users can log in", requirement_type=RequirementType.FUNCTIONAL)
        assert req.title == "Login feature"
        assert req.requirement_type == RequirementType.FUNCTIONAL

    def test_requirement_set(self):
        from software_factory.requirements.models import Requirement, RequirementSet
        rs = RequirementSet(name="Sprint 1")
        rs.add_requirement(Requirement(title="A"))
        rs.add_requirement(Requirement(title="B"))
        assert rs.total_count() == 2


class TestRequirementsParser:
    def test_parse(self):
        from software_factory.requirements.requirements_parser import RequirementsParser
        parser = RequirementsParser()
        req = parser.parse({"title": "Test", "type": "security", "priority": "high"})
        assert req.title == "Test"
        assert req.requirement_type.value == "security"

    def test_parse_text(self):
        from software_factory.requirements.requirements_parser import RequirementsParser
        parser = RequirementsParser()
        req = parser.parse_text("Login Page\nAs a user I want to login")
        assert req.title == "Login Page"


class TestRequirementsValidator:
    def test_valid(self):
        from software_factory.requirements.models import Requirement
        from software_factory.requirements.requirements_validator import RequirementsValidator
        val = RequirementsValidator()
        result = val.validate(Requirement(title="Valid Req", description="Desc"))
        assert result.is_valid is True

    def test_missing_title(self):
        from software_factory.requirements.models import Requirement
        from software_factory.requirements.requirements_validator import RequirementsValidator
        val = RequirementsValidator()
        result = val.validate(Requirement(title="", description="Desc"))
        assert result.is_valid is False


class TestRequirementsManager:
    def test_create_and_add(self):
        from software_factory.requirements.models import Requirement
        from software_factory.requirements.requirements_manager import RequirementsManager
        mgr = RequirementsManager()
        rs = mgr.create_set("Sprint 1")
        mgr.add_requirement(rs.set_id, Requirement(title="R1"))
        assert rs.total_count() == 1

    def test_approve(self):
        from software_factory.requirements.models import Requirement
        from software_factory.requirements.requirements_manager import RequirementsManager
        mgr = RequirementsManager()
        req = Requirement(title="ApproveMe")
        mgr.approve_requirement(req)
        assert req.is_approved()


class TestRequirementsAnalyzer:
    def test_analyze_set(self):
        from software_factory.requirements.models import Requirement, RequirementSet
        from software_factory.requirements.requirements_analyzer import RequirementsAnalyzer
        analyzer = RequirementsAnalyzer()
        rs = RequirementSet(name="Test", requirements=[
            Requirement(title="A", description="Desc A"),
            Requirement(title="B", description="Desc B"),
        ])
        result = analyzer.analyze_set(rs)
        assert result["total"] == 2

    def test_quality_score(self):
        from software_factory.requirements.models import Requirement, RequirementSet
        from software_factory.requirements.requirements_analyzer import RequirementsAnalyzer
        analyzer = RequirementsAnalyzer()
        rs = RequirementSet(name="Q", requirements=[Requirement(title="X", description="Y")])
        score = analyzer.compute_quality_score(rs)
        assert 0.0 <= score <= 1.0


class TestRequirementsMapper:
    def test_add_artifact(self):
        from software_factory.requirements.requirements_mapper import RequirementsMapper
        mapper = RequirementsMapper()
        mapper.add_artifact("r1", "src/auth.py")
        mapping = mapper.get_mapping("r1")
        assert "src/auth.py" in mapping.mapped_artifacts


class TestRequirementsReporter:
    def test_status_report(self):
        from software_factory.requirements.models import Requirement, RequirementSet
        from software_factory.requirements.requirements_reporter import RequirementsReporter
        reporter = RequirementsReporter()
        rs = RequirementSet(name="R", requirements=[Requirement(title="T")])
        report = reporter.generate_status_report(rs)
        assert report["summary"]["total"] == 1


class TestRequirementsEngine:
    def test_process(self):
        from software_factory.requirements.requirements_engine import RequirementsEngine
        engine = RequirementsEngine()
        req_set = engine.process_requirements([
            {"title": "R1", "type": "functional"},
            {"title": "R2", "type": "security"},
        ])
        assert req_set.total_count() == 2


# ---------- ARCHITECTURE SUBSYSTEM TESTS ----------

class TestArchitectureModels:
    def test_component(self):
        from software_factory.architecture.models import ArchitectureComponent, ComponentType
        comp = ArchitectureComponent(name="AuthService", component_type=ComponentType.SERVICE, technology="FastAPI")
        assert comp.name == "AuthService"
        assert comp.component_type == ComponentType.SERVICE

    def test_connector(self):
        from software_factory.architecture.models import Connector, ConnectorType
        conn = Connector(source_id="a", target_id="b", connector_type=ConnectorType.HTTP)
        assert conn.connector_type == ConnectorType.HTTP

    def test_pattern(self):
        from software_factory.architecture.models import ArchitecturePattern, PatternType
        pat = ArchitecturePattern(name="Micro", pattern_type=PatternType.MICROSERVICES)
        assert pat.pattern_type == PatternType.MICROSERVICES


class TestArchitectureDesigner:
    def test_create_component(self):
        from software_factory.architecture.architecture_designer import ArchitectureDesigner
        from software_factory.architecture.models import ComponentType
        designer = ArchitectureDesigner()
        comp = designer.create_component("API", ComponentType.API, technology="FastAPI")
        assert comp.name == "API"

    def test_apply_pattern(self):
        from software_factory.architecture.architecture_designer import ArchitectureDesigner
        from software_factory.architecture.models import PatternType
        designer = ArchitectureDesigner()
        result = designer.apply_pattern(PatternType.MICROSERVICES)
        assert len(result["components"]) > 0


class TestArchitectureAnalyzer:
    def test_analyze(self):
        from software_factory.architecture.architecture_analyzer import ArchitectureAnalyzer
        from software_factory.architecture.models import ArchitectureComponent, ComponentType, Connector
        analyzer = ArchitectureAnalyzer()
        comps = [ArchitectureComponent(name="A", component_type=ComponentType.SERVICE)]
        conns = [Connector(source_id="x", target_id="y")]
        result = analyzer.analyze(comps, conns)
        assert result["total_components"] == 1


class TestArchitectureValidator:
    def test_validate_valid(self):
        from software_factory.architecture.architecture_validator import ArchitectureValidator
        from software_factory.architecture.models import ArchitectureComponent
        validator = ArchitectureValidator()
        comp = ArchitectureComponent(component_id="c1", name="A", interfaces=["api"])
        result = validator.validate([comp], [])
        assert result["is_valid"] is True


class TestArchitectureRenderer:
    def test_render_text(self):
        from software_factory.architecture.architecture_renderer import ArchitectureRenderer
        from software_factory.architecture.models import ArchitectureComponent, ComponentType
        renderer = ArchitectureRenderer()
        comps = [ArchitectureComponent(name="Web", component_type=ComponentType.UI)]
        text = renderer.render_text(comps, [])
        assert "Web" in text

    def test_render_mermaid(self):
        from software_factory.architecture.architecture_renderer import ArchitectureRenderer
        from software_factory.architecture.models import ArchitectureComponent, ComponentType, Connector, ConnectorType
        renderer = ArchitectureRenderer()
        c1 = ArchitectureComponent(component_id="c1", name="API", component_type=ComponentType.API)
        c2 = ArchitectureComponent(component_id="c2", name="DB", component_type=ComponentType.DATABASE)
        conn = Connector(source_id="c1", target_id="c2", connector_type=ConnectorType.SYNCHRONOUS)
        mermaid = renderer.render_mermaid([c1, c2], [conn])
        assert "graph TD" in mermaid


class TestArchitectureEngine:
    def test_add_and_analyze(self):
        from software_factory.architecture.architecture_engine import ArchitectureEngine
        from software_factory.architecture.models import ArchitectureComponent, ComponentType
        engine = ArchitectureEngine()
        comp = ArchitectureComponent(name="Svc", component_type=ComponentType.SERVICE)
        engine.add_component(comp)
        stats = engine.get_stats()
        assert stats["components"] == 1


# ---------- GENERATION SUBSYSTEM TESTS ----------

class TestGenerationModels:
    def test_template(self):
        from software_factory.generation.models import Template
        t = Template(name="py_class", content="class {{name}}:\\n    pass")
        rendered = t.render({"name": "MyClass"})
        assert "MyClass" in rendered


class TestCodeGenerator:
    def test_generate_class(self):
        from software_factory.generation.code_generator import CodeGenerator
        from software_factory.generation.models import TemplateLanguage
        gen = CodeGenerator()
        code = gen.generate_class("User", [{"name": "name", "default": "None"}], ["get_name"], TemplateLanguage.PYTHON)
        assert "class User:" in code
        assert "get_name" in code

    def test_generate_function(self):
        from software_factory.generation.code_generator import CodeGenerator
        gen = CodeGenerator()
        code = gen.generate_function("add", ["a", "b"], "return a + b")
        assert "def add(a, b):" in code


class TestTemplateEngine:
    def test_register_and_render(self):
        from software_factory.generation.models import Template
        from software_factory.generation.template_engine import TemplateEngine
        engine = TemplateEngine()
        t = Template(name="hello", content="Hello {{name}}!")
        engine.register(t)
        result = engine.render(t.template_id, {"name": "World"})
        assert "Hello World!" in result


class TestScaffolder:
    def test_scaffold_library(self):
        from software_factory.generation.scaffolder import Scaffolder
        scaffolder = Scaffolder()
        files = scaffolder.scaffold({"project_type": "library", "project_name": "mylib"})
        assert len(files) > 0
        assert any("setup.py" in f.path for f in files)


class TestCodeTransformer:
    def test_rename_variable(self):
        from software_factory.generation.code_transformer import CodeTransformer
        transformer = CodeTransformer()
        result = transformer.rename_variable("old_name = 1", "old_name", "new_name")
        assert "new_name" in result


class TestGenerationEngine:
    def test_generate_from_template(self):
        from software_factory.generation.generation_engine import GenerationEngine
        from software_factory.generation.models import Template
        engine = GenerationEngine()
        t = Template(name="test", content="value={{x}}")
        gf = engine.generate_from_template(t, {"x": "42"}, "out.txt")
        assert "42" in gf.content


# ---------- DATABASE SUBSYSTEM TESTS ----------

class TestDatabaseModels:
    def test_column(self):
        from software_factory.database.models import Column, ColumnType
        col = Column(name="id", column_type=ColumnType.INTEGER, primary_key=True)
        assert col.primary_key is True

    def test_table(self):
        from software_factory.database.models import Column, ColumnType, Table
        table = Table(name="users")
        table.add_column(Column(name="id", column_type=ColumnType.INTEGER, primary_key=True))
        table.add_column(Column(name="name", column_type=ColumnType.VARCHAR))
        assert len(table.columns) == 2
        assert table.has_column("name")

    def test_schema(self):
        from software_factory.database.models import DatabaseSchema, Table
        schema = DatabaseSchema(name="app_db")
        schema.add_table(Table(name="users"))
        assert schema.table_names() == ["users"]

    def test_version_parse(self):
        from software_factory.versioning.models import Version
        v = Version.parse("1.2.3")
        assert v.major == 1
        assert v.minor == 2
        assert v.patch == 3
        assert str(v) == "1.2.3"


class TestSchemaDesigner:
    def test_create_schema(self):
        from software_factory.database.schema_designer import SchemaDesigner
        designer = SchemaDesigner()
        schema = designer.create_schema("mydb")
        designer.create_table(schema, "users", [
            {"name": "id", "type": "integer", "primary_key": True},
            {"name": "email", "type": "varchar"},
        ])
        assert len(schema.tables) == 1

    def test_generate_ddl(self):
        from software_factory.database.schema_designer import SchemaDesigner
        designer = SchemaDesigner()
        schema = designer.create_schema("test")
        designer.create_table(schema, "items", [{"name": "id", "type": "integer", "primary_key": True}])
        ddl = designer.generate_ddl(schema)
        assert "CREATE TABLE items" in ddl


class TestMigrationManager:
    def test_create_and_execute(self):
        from software_factory.database.migration_manager import MigrationManager
        mgr = MigrationManager()
        migration = mgr.create_migration("v1", [{"operation": "create_table", "table": "users"}])
        assert mgr.execute_migration(migration) is True
        assert len(mgr.get_executed()) == 1


class TestQueryBuilder:
    def test_select(self):
        from software_factory.database.query_builder import QueryBuilder
        qb = QueryBuilder()
        query = qb.select(["id", "name"], "users").where("id = ?", 1).build()
        assert "SELECT id, name FROM users" in query
        assert "WHERE id = ?" in query

    def test_insert(self):
        from software_factory.database.query_builder import QueryBuilder
        qb = QueryBuilder()
        query = qb.insert("users", ["name", "email"], ["Alice", "a@b.com"]).build()
        assert "INSERT INTO users" in query

    def test_params(self):
        from software_factory.database.query_builder import QueryBuilder
        qb = QueryBuilder()
        qb.select(["*"], "t").where("x = ?", 42)
        assert qb.get_params() == [42]


class TestDatabaseAnalyzer:
    def test_analyze_schema(self):
        from software_factory.database.database_analyzer import DatabaseAnalyzer
        from software_factory.database.models import Column, ColumnType, DatabaseSchema, Table
        analyzer = DatabaseAnalyzer()
        schema = DatabaseSchema(name="test")
        table = Table(name="users")
        table.add_column(Column(name="id", column_type=ColumnType.INTEGER, primary_key=True))
        table.add_column(Column(name="name", column_type=ColumnType.VARCHAR))
        schema.add_table(table)
        result = analyzer.analyze_schema(schema)
        assert result["total_tables"] == 1
        assert result["total_columns"] == 2


class TestDatabaseEngine:
    def test_create_migration(self):
        from software_factory.database.database_engine import DatabaseEngine
        engine = DatabaseEngine()
        migration = engine.create_migration("v1", [{"operation": "create", "table": "t"}])
        assert migration.name == "v1"
        assert len(engine.get_migrations()) == 1


# ---------- TESTING SUBSYSTEM TESTS ----------

class TestTestingModels:
    def test_test_case(self):
        from software_factory.testing.models import TestCase, TestCategory
        tc = TestCase(name="test_add", category=TestCategory.UNIT, module="math")
        assert tc.name == "test_add"

    def test_test_suite(self):
        from software_factory.testing.models import TestCase, TestSuite
        suite = TestSuite(name="MathTests")
        suite.add_test(TestCase(name="t1"))
        suite.add_test(TestCase(name="t2"))
        assert len(suite.tests) == 2

    def test_coverage_report(self):
        from software_factory.testing.models import CoverageReport
        cr = CoverageReport(total_lines=100, covered_lines=80)
        assert cr.line_coverage == 0.8


class TestTestGenerator:
    def test_generate_for_module(self):
        from software_factory.testing.models import TestCategory
        from software_factory.testing.test_generator import TestGenerator
        gen = TestGenerator()
        tests = gen.generate_for_module("auth.login", TestCategory.UNIT)
        assert len(tests) >= 1

    def test_generate_unit_test(self):
        from software_factory.testing.test_generator import TestGenerator
        gen = TestGenerator()
        tc = gen.generate_unit_test("UserService", "authenticate")
        assert "UserService" in tc.name


class TestTestRunner:
    def test_run_suite(self):
        from software_factory.testing.models import TestCase, TestStatus, TestSuite
        from software_factory.testing.test_runner import TestRunner
        runner = TestRunner()
        suite = TestSuite(name="Simple", tests=[TestCase(name="t1"), TestCase(name="t2")])
        results = runner.run_suite(suite)
        assert len(results) == 2
        assert all(r.status == TestStatus.PASSED for r in results)


class TestTestReporter:
    def test_generate_report(self):
        from software_factory.testing.models import TestResult, TestStatus
        from software_factory.testing.test_reporter import TestReporter
        reporter = TestReporter()
        results = [
            TestResult(test_name="t1", status=TestStatus.PASSED, duration=0.1),
            TestResult(test_name="t2", status=TestStatus.FAILED, message="oops"),
        ]
        report = reporter.generate_report(results)
        assert report["passed"] == 1
        assert report["failed"] == 1


class TestCoverageAnalyzer:
    def test_add_and_summary(self):
        from software_factory.testing.coverage_analyzer import CoverageAnalyzer
        analyzer = CoverageAnalyzer()
        report = analyzer.create_report()
        analyzer.add_file_coverage(report, "a.py", 100, 90, 10, 9)
        summary = analyzer.get_summary(report)
        assert summary["total_lines"] == 100
        assert summary["line_coverage"] == 0.9


class TestTestingEngine:
    def test_generate_and_run(self):
        from software_factory.testing.testing_engine import TestingEngine
        engine = TestingEngine()
        suite = engine.generate_tests("auth.module", "unit")
        assert len(suite.tests) > 1
        results = engine.run_suite(suite.suite_id)
        assert len(results) > 0


# ---------- DOCUMENTATION SUBSYSTEM TESTS ----------

class TestDocumentationModels:
    def test_doc_page(self):
        from software_factory.documentation.models import DocPage, DocSection, DocType
        page = DocPage(title="API Guide", doc_type=DocType.API)
        page.add_section(DocSection(title="Intro", content="Welcome"))
        md = page.to_markdown()
        assert "API Guide" in md

    def test_api_endpoint(self):
        from software_factory.documentation.models import ApiEndpoint, ApiParameter
        ep = ApiEndpoint(path="/users", method="GET", summary="List users")
        ep.parameters.append(ApiParameter(name="limit", type="integer"))
        assert len(ep.parameters) == 1


class TestDocGenerator:
    def test_generate_page(self):
        from software_factory.documentation.doc_generator import DocGenerator
        gen = DocGenerator()
        page = gen.generate_page("MyDoc", [{"title": "S1", "content": "Content1"}])
        assert page.title == "MyDoc"
        assert len(page.sections) == 1


class TestApiDocGenerator:
    def test_generate(self):
        from software_factory.documentation.api_doc_generator import ApiDocGenerator
        gen = ApiDocGenerator()
        docs = gen.generate([{"path": "/items", "method": "GET", "summary": "Get items"}])
        assert "/items" in docs


class TestReadmeGenerator:
    def test_generate(self):
        from software_factory.documentation.readme_generator import ReadmeGenerator
        gen = ReadmeGenerator()
        readme = gen.generate({"name": "MyProject", "description": "A great project"})
        assert "MyProject" in readme
        assert "A great project" in readme


class TestChangelogGenerator:
    def test_generate(self):
        from software_factory.documentation.changelog_generator import ChangelogGenerator
        from software_factory.documentation.models import ChangelogEntry
        gen = ChangelogGenerator()
        entry = ChangelogEntry(version="1.0.0", changes=["Initial release"])
        changelog = gen.generate([entry])
        assert "1.0.0" in changelog
        assert "Initial release" in changelog


class TestDocumentationEngine:
    def test_generate_readme(self):
        from software_factory.documentation.documentation_engine import DocumentationEngine
        engine = DocumentationEngine()
        readme = engine.generate_readme({"name": "App", "description": "Test app"})
        assert "App" in readme


# ---------- DEPLOYMENT SUBSYSTEM TESTS ----------

class TestDeploymentModels:
    def test_deployment(self):
        from software_factory.deployment.models import Deployment, DeploymentStatus
        d = Deployment(name="v1-deploy", version="1.0.0", environment="production")
        assert d.status == DeploymentStatus.PENDING

    def test_environment(self):
        from software_factory.deployment.models import Environment, EnvironmentType
        env = Environment(name="staging", environment_type=EnvironmentType.STAGING)
        assert env.environment_type == EnvironmentType.STAGING


class TestDeployer:
    def test_deploy(self):
        from software_factory.deployment.deployer import Deployer
        from software_factory.deployment.models import Deployment
        deployer = Deployer()
        d = Deployment(name="test", version="1.0", steps=["step1"])
        assert deployer.deploy(d) is True

    def test_dry_run(self):
        from software_factory.deployment.deployer import Deployer
        from software_factory.deployment.models import Deployment
        deployer = Deployer()
        d = Deployment(name="test", version="1.0", steps=["s1", "s2"])
        result = deployer.dry_run(d)
        assert result["would_succeed"] is True


class TestReleaseManager:
    def test_create_release(self):
        from software_factory.deployment.release_manager import ReleaseManager
        mgr = ReleaseManager()
        release = mgr.create_release("1.0.0", "First Release", "Initial launch")
        assert release.version == "1.0.0"

    def test_mark_deployed(self):
        from software_factory.deployment.release_manager import ReleaseManager
        mgr = ReleaseManager()
        release = mgr.create_release("1.0.0", "R1")
        mgr.mark_deployed(release.release_id, "production")
        assert "production" in release.deployed_environments


class TestEnvironmentManager:
    def test_create_env(self):
        from software_factory.deployment.environment_manager import EnvironmentManager
        from software_factory.deployment.models import EnvironmentType
        mgr = EnvironmentManager()
        env = mgr.create_environment("prod", EnvironmentType.PRODUCTION, "https://prod.app.com")
        assert env.active is True
        assert mgr.count() == 1


class TestRollbackHandler:
    def test_create_plan_and_rollback(self):
        from software_factory.deployment.models import Deployment
        from software_factory.deployment.rollback_handler import RollbackHandler
        handler = RollbackHandler()
        plan = handler.create_plan("d1", ["restore_db", "restart"])
        d = Deployment(deployment_id="d1")
        assert handler.execute_rollback(d, plan) is True
        assert d.status.value == "rolled_back"


class TestDeploymentEngine:
    def test_create_and_execute(self):
        from software_factory.deployment.deployment_engine import DeploymentEngine
        engine = DeploymentEngine()
        d = engine.create_deployment("Deploy v1", "1.0.0", "staging")
        assert engine.execute_deployment(d.deployment_id) is True


# ---------- QUALITY SUBSYSTEM TESTS ----------

class TestQualityModels:
    def test_quality_issue(self):
        from software_factory.quality.models import IssueSeverity, QualityIssue
        issue = QualityIssue(file_path="a.py", line_number=10, severity=IssueSeverity.WARNING, message="Too long")
        assert issue.severity == IssueSeverity.WARNING

    def test_quality_report(self):
        from software_factory.quality.models import IssueSeverity, QualityIssue, QualityReport
        report = QualityReport(score=85.0, issues=[
            QualityIssue(severity=IssueSeverity.WARNING),
            QualityIssue(severity=IssueSeverity.INFO),
        ])
        assert report.issue_count == 2


class TestLinter:
    def test_lint(self):
        from software_factory.quality.linter import Linter
        linter = Linter()
        issues = linter.lint("eval('bad')\\nprint('hello')")
        assert len(issues) >= 1


class TestFormatter:
    def test_check_line_length(self):
        from software_factory.quality.formatter import Formatter
        fmt = Formatter()
        violations = fmt.check_line_length("short line", 5)
        assert len(violations) == 1
        violations = fmt.check_line_length("ok", 100)
        assert len(violations) == 0


class TestComplexityAnalyzer:
    def test_analyze(self):
        from software_factory.quality.complexity_analyzer import ComplexityAnalyzer
        analyzer = ComplexityAnalyzer()
        metrics = analyzer.analyze("def foo():\\n    pass\\ndef bar():\\n    pass")
        assert len(metrics) > 0

    def test_cyclomatic(self):
        from software_factory.quality.complexity_analyzer import ComplexityAnalyzer
        analyzer = ComplexityAnalyzer()
        c = analyzer.cyclomatic_complexity("if x:\\n    if y:\\n        pass")
        assert c >= 2


class TestQualityEngine:
    def test_analyze_file(self):
        from software_factory.quality.quality_engine import QualityEngine
        engine = QualityEngine()
        report = engine.analyze_file("test.py", "def foo():\\n    pass")
        assert report.score > 0


# ---------- VERSIONING SUBSYSTEM TESTS ----------

class TestVersioningModels:
    def test_version_parse(self):
        from software_factory.versioning.models import Version
        v = Version.parse("2.1.0")
        assert v.major == 2
        assert v.minor == 1
        assert v.patch == 0

    def test_version_bump(self):
        from software_factory.versioning.models import Version
        v = Version(1, 2, 3)
        assert str(v.bump_major()) == "2.0.0"
        assert str(v.bump_minor()) == "1.3.0"
        assert str(v.bump_patch()) == "1.2.4"

    def test_version_compare(self):
        from software_factory.versioning.models import Version
        assert Version(1, 0, 0) < Version(2, 0, 0)
        assert Version(1, 2, 0) < Version(1, 3, 0)
        assert Version(1, 2, 3) == Version(1, 2, 3)

    def test_dependency_graph(self):
        from software_factory.versioning.models import DependencyGraph
        graph = DependencyGraph()
        graph.add_node("A")
        graph.add_node("B")
        graph.add_edge("A", "B")
        assert "B" in graph.get_dependencies("A")

    def test_version_constraint(self):
        from software_factory.versioning.models import VersionConstraint
        vc = VersionConstraint(name="lib", min_version="1.0.0", max_version="2.0.0")
        assert vc.satisfies("1.5.0") is True
        assert vc.satisfies("2.1.0") is False


class TestTagManager:
    def test_create_tag(self):
        from software_factory.versioning.tag_manager import TagManager
        mgr = TagManager()
        tag = mgr.create_tag("v1.0.0", "1.0.0", "First release")
        assert tag.name == "v1.0.0"
        assert mgr.count() == 1


class TestBranchManager:
    def test_create_branch(self):
        from software_factory.versioning.branch_manager import BranchManager
        mgr = BranchManager()
        branch = mgr.create_branch("feature/auth", "main")
        assert branch.source_branch == "main"

    def test_protect(self):
        from software_factory.versioning.branch_manager import BranchManager
        mgr = BranchManager()
        mgr.create_branch("main")
        mgr.protect_branch("main")
        assert mgr.get_branch("main").is_protected is True


class TestDependencyResolver:
    def test_resolve(self):
        from software_factory.versioning.dependency_resolver import DependencyResolver
        resolver = DependencyResolver()
        graph = resolver.create_graph("deps")
        graph.add_node("A")
        graph.add_node("B")
        graph.add_edge("A", "B")
        order = resolver.resolve("deps")
        assert "B" in order
        assert "A" in order


class TestVersioningEngine:
    def test_create_and_bump(self):
        from software_factory.versioning.versioning_engine import VersioningEngine
        engine = VersioningEngine()
        v = engine.create_version(1, 0, 0)
        new_v = engine.bump_version(v, "minor")
        assert new_v.minor == 1
