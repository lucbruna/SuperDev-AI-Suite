"""Comprehensive tests for Volume 25 — Frontend Experience & User Interface Engine."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

passed = 0
failed = 0
total = 0


def test(name, condition):
    global passed, failed, total
    total += 1
    if condition:
        passed += 1
        print("  PASS: " + name)
    else:
        failed += 1
        print("  FAIL: " + name)


# === Core App ===
print("\n=== Core App ===")
from frontend.app.config import FrontendConfig, Language, TenantConfig, Theme

cfg = FrontendConfig()
test("FrontendConfig default", cfg.theme == Theme.DARK)
test("FrontendConfig language", cfg.language == Language.PT)
test("FrontendConfig to_dict", "app_name" in cfg.to_dict())

tc = TenantConfig(tenant_id="t1", name="Tenant A")
test("TenantConfig", tc.name == "Tenant A")
test("TenantConfig has_feature", tc.has_feature("any_feature"))

from frontend.app.app_core import APIService, App, AuthService, create_app

app = App()
app.initialize()
test("App initialize", app.initialized)
test("App state", app.state.value == "ready")
test("App is_authenticated", not app.is_authenticated())

app2 = create_app({"theme": "dark"})
test("create_app", app2.initialized)

auth = AuthService()
test("AuthService", auth is not None)

api = APIService()
test("APIService", api is not None)

from frontend.app.router import Route, create_router

router = create_router()
router.add_route(Route(path="/", component="Home"))
router.add_route(Route(path="/login", component="Login"))
router.add_route(Route(path="/users/:id", component="User"))
test("Router add_route", len(router.routes) == 3)
test("Router navigate", router.navigate("/"))
test("Router current", router.get_current_route() is not None)
router.navigate("/login")
test("Router back", router.back())

from frontend.app.providers import AppProvider, ThemeProvider

provider = AppProvider()
provider.initialize({"theme": "dark"})
test("AppProvider", provider is not None)

tp = ThemeProvider()
test("ThemeProvider theme", tp.get_theme().name == "dark")
tp.toggle_theme()
test("ThemeProvider toggle", tp.get_theme().name == "light")

from frontend.app.permissions import Permission, PermissionManager, Role

pm = PermissionManager()
pm.set_user_role("user1", Role.DEVELOPER)
test("PermissionManager", pm.has_permission("user1", Permission.VIEW_PROJECTS))
test("PermissionManager deny", not pm.has_permission("user1", Permission.MANAGE_USERS))

from frontend.app.initialization import AppInitializer, InitPhase

init = AppInitializer()
test("AppInitializer", init.phase == InitPhase.PENDING)
init.add_step("test", InitPhase.CONFIG, lambda cfg: None)
test("AppInitializer add_step", len(init.steps) == 1)

# === UI Components ===
print("\n=== UI Components ===")
from frontend.components.ui.button import Button, ButtonProps, ButtonSize, ButtonVariant

btn = Button(ButtonProps(variant=ButtonVariant.PRIMARY, size=ButtonSize.LG))
btn.click()
test("Button", btn.clicked)
test("Button class", "btn" in btn.get_class_name())
test("Button disabled", Button(ButtonProps(disabled=True)).is_disabled())

from frontend.components.ui.input import Input, InputProps, InputType

inp = Input(InputProps(type=InputType.EMAIL, required=True))
inp.value = ""
test("Input empty", not inp.is_valid())
inp.value = "test@example.com"
test("Input valid", inp.is_valid())

from frontend.components.ui.modal import Modal, ModalProps

modal = Modal(ModalProps(title="Test"))
modal.open()
test("Modal open", modal._isOpen)
modal.close()
test("Modal close", not modal._isOpen)

from frontend.components.ui.table import Table, TableColumn, TableProps

table = Table(TableProps(columns=[TableColumn(key="name", label="Name")], data=[{"name": "Test"}]))
test("Table data", len(table.paginated_data) == 1)

from frontend.components.ui.card import Card, CardProps

card = Card(CardProps(title="Test Card"))
test("Card", card.props.title == "Test Card")

from frontend.components.ui.dropdown import Dropdown, DropdownItem, DropdownProps

dd = Dropdown(DropdownProps(items=[DropdownItem(label="Option 1", value="1")]))
dd.select(dd.props.items[0])
test("Dropdown select", dd._selectedValue == "1")

from frontend.components.ui.tabs import Tab, Tabs, TabsProps

tabs = Tabs(TabsProps(tabs=[Tab(key="tab1", label="Tab 1"), Tab(key="tab2", label="Tab 2")]))
tabs.set_active("tab2")
test("Tabs", tabs._activeKey == "tab2")

from frontend.components.ui.form import Form, FormField, FormProps

form = Form(FormProps(fields=[FormField(name="email", label="Email", required=True)]))
form.set_value("email", "test@test.com")
test("Form set_value", form.get_value("email") == "test@test.com")

from frontend.components.ui.notification import Notification, NotificationProps, NotificationType

notif = Notification(NotificationProps(type=NotificationType.SUCCESS, message="Done"))
test("Notification", notif.props.type == NotificationType.SUCCESS)

# === Editor Components ===
print("\n=== Editor Components ===")
from frontend.components.editor.code_editor import CodeEditor, EditorConfig

editor = CodeEditor(EditorConfig())
editor.set_content("line1\nline2\nline3")
test("CodeEditor set_content", editor.get_content() == "line1\nline2\nline3")
test("CodeEditor line", editor.get_line(0) == "line1")
editor.insert_text("x")
test("CodeEditor insert", "x" in editor.get_content())
editor.undo()
test("CodeEditor undo", "x" not in editor.get_content())

from frontend.components.editor.syntax_highlighter import SyntaxHighlighter

sh = SyntaxHighlighter()
tokens = sh.highlight("def hello():\\n    pass", "python")
test("SyntaxHighlighter", len(tokens) > 0)

from frontend.components.editor.file_tree import FileTree, NodeType

ft = FileTree()
node = ft.add_directory("project")
ft.add_file("main.py", "project")
test("FileTree", node is not None)

from frontend.components.editor.terminal import Terminal

term = Terminal()
result = term.execute("echo hello")
test("Terminal execute", result.exit_code == 0)
test("Terminal lines", len(term.lines) > 0)

from frontend.components.editor.suggestion_panel import Suggestion, SuggestionPanel, SuggestionType

sp = SuggestionPanel()
sp.add_suggestion(Suggestion(id="s1", type=SuggestionType.COMPLETION, title="Complete"))
test("SuggestionPanel", len(sp.suggestions) == 1)

from frontend.components.editor.ai_assistant import AIAssistant

ai = AIAssistant()
ai.send_message("Hello")
test("AIAssistant", len(ai.messages) == 1)

from frontend.components.editor.diff_viewer import DiffViewer

dv = DiffViewer()
dv.set_diff("line1\\nline2", "line1\\nchanged")
test("DiffViewer", len(dv.files) == 1)

# === AI Components ===
print("\n=== AI Components ===")
from frontend.components.ai.ai_chat import AIChat, ChatConfig

chat = AIChat(ChatConfig(model="gpt-4"))
chat.send("Hello")
test("AIChat", len(chat.messages) == 1)

from frontend.components.ai.agent_panel import AgentInfo, AgentPanel, AgentType

ap = AgentPanel()
ap.add_agent(AgentInfo(id="a1", name="Coder", type=AgentType.CODER))
test("AgentPanel", len(ap.agents) == 1)

from frontend.components.ai.agent_status import AgentStatus

ast = AgentStatus()
ast.update("a1", name="Agent 1", status="running")
test("AgentStatus", ast.get("a1") is not None)

from frontend.components.ai.conversation import ConversationManager

cm = ConversationManager()
conv = cm.create("Test Conv")
test("ConversationManager", conv.title == "Test Conv")

from frontend.components.ai.prompt_builder import PromptBuilder, PromptTemplate

pb = PromptBuilder()
pb.add_template(PromptTemplate(name="test", template="Hello {name}"))
result = pb.build("test", {"name": "World"})
test("PromptBuilder", "World" in result)

from frontend.components.ai.memory_viewer import MemoryEntry, MemoryType, MemoryViewer

mv = MemoryViewer()
mv.add_memory(MemoryEntry(id="m1", content="test", memory_type=MemoryType.SHORT_TERM))
test("MemoryViewer", len(mv.memories) == 1)

from frontend.components.ai.reasoning_view import ReasoningStep, ReasoningView, Thought

rv = ReasoningView()
rv.add_thought(Thought(step=ReasoningStep.ANALYZE, content="Analyzing..."))
test("ReasoningView", len(rv.thoughts) == 1)

# === Dashboard Components ===
print("\n=== Dashboard Components ===")
from frontend.components.dashboard.dashboard_home import DashboardHome, MetricCard

dh = DashboardHome()
dh.add_metric(MetricCard(title="Agents", value="125"))
test("DashboardHome", len(dh.metrics) == 1)

from frontend.components.dashboard.metrics_panel import Metric, MetricsPanel, MetricType

mp = MetricsPanel()
mp.add_metric(Metric(name="CPU", value=50, metric_type=MetricType.PERCENTAGE))
test("MetricsPanel", len(mp.metrics) == 1)

from frontend.components.dashboard.performance import PerformanceDashboard

pd = PerformanceDashboard()
test("PerformanceDashboard", pd.get_health() == "healthy")

from frontend.components.dashboard.costs import CostDashboard, CostItem

cd = CostDashboard()
cd.add_item(CostItem(service="AWS", amount=1000))
test("CostDashboard", cd.get_total() == 1000)

from frontend.components.dashboard.agents_dashboard import AgentDashboardInfo, AgentDashboardStatus, AgentsDashboard

ad = AgentsDashboard()
ad.add_agent(AgentDashboardInfo(id="a1", name="Agent 1", status=AgentDashboardStatus.ACTIVE))
test("AgentsDashboard", ad.get_active_count() == 1)

from frontend.components.dashboard.infrastructure_dashboard import InfrastructureDashboard, ServerInfo

id_dash = InfrastructureDashboard()
id_dash.add_server(ServerInfo(name="server-1", cpu=50))
test("InfrastructureDashboard", len(id_dash.servers) == 1)

from frontend.components.dashboard.security_dashboard import SecurityDashboard, SecurityEvent, ThreatLevel

sd = SecurityDashboard()
sd.add_event(SecurityEvent(id="e1", title="Threat", threat_level=ThreatLevel.HIGH))
test("SecurityDashboard", len(sd.get_active_threats()) == 1)

# === Services ===
print("\n=== Services ===")
from frontend.services.api_client import APIClient, APIConfig

client = APIClient(APIConfig(base_url="http://test.com"))
response = client.get("/api/test")
test("APIClient", response.ok)

from frontend.services.auth_service import AuthService as AS

auth_svc = AS()
auth_svc.login("test@test.com", "pass")
test("AuthService", auth_svc.is_authenticated())

from frontend.services.project_service import ProjectService

ps = ProjectService()
proj = ps.create("My Project")
test("ProjectService", proj.name == "My Project")

from frontend.services.agent_service import AgentService

ags = AgentService()
agent = ags.create("Coder Agent")
test("AgentService", agent.name == "Coder Agent")

from frontend.services.websocket_service import WebSocketService, WSStatus

ws = WebSocketService()
ws.connect("ws://test.com")
test("WebSocketService", ws.status == WSStatus.CONNECTED)

# === Stores ===
print("\n=== Stores ===")
from frontend.stores.user_store import UserStore

us = UserStore()
us.set_user({"id": "1", "name": "Test User"})
test("UserStore", us.state.is_authenticated)

from frontend.stores.project_store import ProjectStore

ps2 = ProjectStore()
ps2.set_projects([{"id": "1", "name": "Project 1"}])
test("ProjectStore", len(ps2.state.projects) == 1)

from frontend.stores.agent_store import AgentStore

aus2 = AgentStore()
aus2.set_agents([{"id": "1", "name": "Agent 1"}])
test("AgentStore", len(aus2.state.agents) == 1)

from frontend.stores.settings_store import SettingsStore

ss = SettingsStore()
ss.set_theme("light")
test("SettingsStore", ss.state.theme == "light")

# === Realtime ===
print("\n=== Realtime ===")
from frontend.realtime.websocket import WebSocketManager

wsm = WebSocketManager()
wsm.connect("ws://test.com")
test("WebSocketManager", wsm.state.value == "open")

from frontend.realtime.event_manager import EventManager

em = EventManager()
em.emit("test", {"data": 1})
test("EventManager", len(em.events) == 1)

from frontend.realtime.live_updates import LiveUpdate, LiveUpdatesManager, UpdateType

lum = LiveUpdatesManager()
lum.subscribe("projects", lambda u: None)
lum.push(LiveUpdate(resource="projects", update_type=UpdateType.UPDATE, data={}))
test("LiveUpdatesManager", len(lum.buffer) == 1)

# === Security ===
print("\n=== Security ===")
from frontend.security.auth_guard import AuthGuard, GuardResult

ag = AuthGuard()
test("AuthGuard denied", ag.check("/dashboard") == GuardResult.REDIRECT)
ag.login({"id": "1"})
test("AuthGuard allowed", ag.check("/dashboard") == GuardResult.ALLOW)

from frontend.security.permission_check import PermissionCheck

pc = PermissionCheck()
pc.set_permissions({"view_dashboard", "edit_code"})
test("PermissionCheck has", pc.has("view_dashboard"))
test("PermissionCheck deny", not pc.has("admin"))

from frontend.security.session import SessionManager

sm = SessionManager()
session = sm.create("user1", "token123")
test("SessionManager", sm.is_valid())

from frontend.security.audit import AuditLog

al = AuditLog()
al.log("login", "user1", "auth")
test("AuditLog", len(al.entries) == 1)

# === Pages ===
print("\n=== Pages ===")
from frontend.pages.login import LoginPage

lp = LoginPage()
lp.set_email("test@test.com")
lp.set_password("pass")
test("LoginPage", lp.form.email == "test@test.com")

from frontend.pages.register import RegisterPage

rp = RegisterPage()
rp.set_field("name", "Test")
test("RegisterPage", rp.form.name == "Test")

from frontend.pages.dashboard import DashboardPage

dp = DashboardPage()
test("DashboardPage", len(dp.widgets) == 0)

from frontend.pages.projects import ProjectsPage

pp = ProjectsPage()
test("ProjectsPage", pp.view_mode == "grid")

from frontend.pages.workspace import WorkspacePage

wp = WorkspacePage()
test("WorkspacePage", wp.show_terminal)

from frontend.pages.settings import SettingsPage

sp2 = SettingsPage()
sp2.update_setting("theme", "dark")
test("SettingsPage", sp2.unsaved)

# === Layouts ===
print("\n=== Layouts ===")
from frontend.layouts.main_layout import MainLayout

ml = MainLayout()
ml.toggle_sidebar()
test("MainLayout", ml.sidebar_collapsed)

from frontend.layouts.admin_layout import AdminLayout

al2 = AdminLayout()
test("AdminLayout", len(al2.menu_items) == 0)

from frontend.layouts.developer_layout import DeveloperLayout

dl = DeveloperLayout()
dl.toggle_panel("terminal")
test("DeveloperLayout", not dl.panels["terminal"])

# === Hooks ===
print("\n=== Hooks ===")
from frontend.hooks.use_auth import UseAuth

ua = UseAuth()
test("UseAuth", ua.state.user is None)

from frontend.hooks.use_api import UseApi

uapi = UseApi()
test("UseApi", uapi.state.data is None)

from frontend.hooks.use_websocket import UseWebSocket

uws = UseWebSocket()
uws.connect("ws://test")
test("UseWebSocket", uws.connected)

# === Utils ===
print("\n=== Utils ===")
from frontend.utils.formatters import format_currency, format_number, format_percentage, truncate

test("format_number", format_number(1500) == "1.50K")
test("format_currency", "$" in format_currency(100))
test("format_percentage", "%" in format_percentage(50.5))
test("truncate", len(truncate("hello world", 5)) <= 5)

from frontend.utils.validators import is_email, is_strong_password, is_url

test("is_email valid", is_email("test@test.com"))
test("is_email invalid", not is_email("invalid"))
test("is_url", is_url("http://test.com"))
test("is_strong_password", is_strong_password("Strong1Pass"))

from frontend.utils.helpers import deep_merge, generate_id, hash_string, slugify

test("generate_id", len(generate_id()) > 0)
test("hash_string", len(hash_string("test")) == 64)
test("deep_merge", deep_merge({"a": 1}, {"b": 2}) == {"a": 1, "b": 2})
test("slugify", slugify("Hello World") == "hello-world")

# === Workflow Component ===
print("\n=== Workflow Component ===")
from frontend.components.workflow.workflow_canvas import NodeType, WorkflowCanvas, WorkflowEdge, WorkflowNode

wc = WorkflowCanvas()
wc.add_node(WorkflowNode(id="n1", node_type=NodeType.START, label="Start"))
wc.add_node(WorkflowNode(id="n2", node_type=NodeType.ACTION, label="Action"))
wc.add_edge(WorkflowEdge(source="n1", target="n2"))
test("WorkflowCanvas nodes", len(wc.nodes) == 2)
test("WorkflowCanvas edges", len(wc.edges) == 1)
wc.zoom_in()
test("WorkflowCanvas zoom", wc.zoom > 1.0)

# === Summary ===
print("\n" + "=" * 60)
print("Volume 25 — Frontend: " + str(passed) + "/" + str(total) + " tests passed (" + str(failed) + " failed)")
print("=" * 60)
sys.exit(0 if failed == 0 else 1)
