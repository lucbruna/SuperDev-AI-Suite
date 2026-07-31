"""Comprehensive tests for Volume 23 — Digital Twin & Simulation Engine."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

passed = 0
failed = 0
total = 0

def test(name, condition):
    global passed, failed, total
    total += 1
    if condition:
        passed += 1
        print(f"  PASS: {name}")
    else:
        failed += 1
        print(f"  FAIL: {name}")

# === Core Infrastructure ===
print("\n=== Core Infrastructure ===")
from digital_twin.twin_config import TwinConfig, TwinType

cfg = TwinConfig()
test("TwinConfig default", cfg.twin_type == TwinType.ENTERPRISE)
test("TwinConfig limits", cfg.limits.max_entities == 10000)

from digital_twin.twin_models import DigitalEntity, EntityState, SimulationConfig

entity = DigitalEntity(name="Test Entity", entity_type="enterprise")
test("DigitalEntity", entity.name == "Test Entity")
test("DigitalEntity state", entity.state == EntityState.ACTIVE)
sim = SimulationConfig(name="Test Sim", time_steps=50)
test("SimulationConfig", sim.time_steps == 50)

from digital_twin.twin_events import TwinEvents

ev = TwinEvents()
ev.emit("test", {"data": 1})
test("TwinEvents", len(ev.get_log()) > 0)

from digital_twin.twin_metrics import TwinMetrics

tm = TwinMetrics()
tm.record_timer("test", 100)
test("TwinMetrics", tm.get_timer_stats("test")["count"] == 1)

from digital_twin.twin_logger import TwinLogger

tl = TwinLogger()
tl.info("test message")
test("TwinLogger", tl.count() > 0)

from digital_twin.twin_security import TwinSecurity

ts = TwinSecurity()
ts.add_policy("p1", {"blocked": ["delete"]})
test("TwinSecurity", len(ts.list_policies()) > 0)

from digital_twin.twin_context import TwinContext

tc = TwinContext()
tc.set("key", "value")
test("TwinContext", tc.get("key") == "value")

from digital_twin.twin_registry import TwinRegistry

tr = TwinRegistry()
tr.register("t1", "Test Twin", "enterprise")
test("TwinRegistry", tr.count() > 0)

from digital_twin.twin_runtime import TwinRuntime

rt = TwinRuntime()
rt.start()
test("TwinRuntime", rt.is_running())

from digital_twin.twin_factory import TwinFactory

tf = TwinFactory()
tf.register_template("enterprise", {"type": "enterprise"})
test("TwinFactory", tf.count() > 0)

from digital_twin.twin_manager import TwinManager

tmgr = TwinManager()
tmgr.create("t1", "Test Twin")
test("TwinManager", tmgr.count() > 0)

from digital_twin.twin_engine import TwinEngine

te = TwinEngine()
te.start()
test("TwinEngine", te.is_running())

# === Models ===
print("\n=== Models ===")
from digital_twin.models.model_engine import ModelEngine

me = ModelEngine()
me.start()
me.create("m1", "Entity Model", "entity")
test("ModelEngine", me.count() > 0)

from digital_twin.models.entity_model import EntityModel

em = EntityModel()
em.create("Product", "product", {"price": 100})
test("EntityModel", em.count() > 0)

from digital_twin.models.process_model import ProcessModel

pm = ProcessModel()
pm.create("Sales Process", [{"name": "receive_order"}, {"name": "process"}, {"name": "ship"}])
test("ProcessModel", pm.count() > 0)

from digital_twin.models.system_model import SystemModel

sm = SystemModel()
sm.create("Supply Chain", [{"id": "wh1", "name": "Warehouse"}, {"id": "store1", "name": "Store"}])
test("SystemModel", sm.count() > 0)

from digital_twin.models.environment_model import EnvironmentModel

envm = EnvironmentModel()
envm.create("Market Environment", {"competitors": 5})
test("EnvironmentModel", envm.count() > 0)

from digital_twin.models.relationship_model import RelationshipModel

rm = RelationshipModel()
rm.create("Product", "Category", "belongs_to")
test("RelationshipModel", rm.count() > 0)

from digital_twin.models.behavior_model import BehaviorModel

bm = BehaviorModel()
bm.create("Price Behavior", [{"condition": "demand_high", "action": "increase_price"}])
test("BehaviorModel", bm.count() > 0)

# === Simulation ===
print("\n=== Simulation ===")
from digital_twin.simulation.simulation_engine import SimulationEngine

se = SimulationEngine()
se.start()
se.create("sim1", "Market Simulation")
test("SimulationEngine", se.count() > 0)

from digital_twin.simulation.simulator import Simulator

simulator = Simulator()
simulator.register("growth", lambda s: {"value": s.get("value", 100) * 1.1})
result = simulator.step()
test("Simulator", "growth" in result)

from digital_twin.simulation.event_simulator import EventSimulator

esv = EventSimulator()
esv.schedule("price_change", 10, {"delta": 0.05})
test("EventSimulator", esv.pending_count() > 0)

from digital_twin.simulation.process_simulator import ProcessSimulator

psv = ProcessSimulator()
psv.define("p1", "Order Process", [{"name": "receive"}, {"name": "process"}, {"name": "ship"}])
test("ProcessSimulator", psv.count() > 0)

from digital_twin.simulation.resource_simulator import ResourceSimulator

rsv = ResourceSimulator()
rsv.add("inventory", 1000, "units")
test("ResourceSimulator", rsv.count() > 0)

from digital_twin.simulation.time_engine import TimeEngine

time_e = TimeEngine()
time_e.advance()
test("TimeEngine", time_e.get_current() == 1.0)

from digital_twin.simulation.scenario_runner import ScenarioRunner

sr = ScenarioRunner()
sr.add_scenario("s1", "Price Increase", {"delta": 0.1})
test("ScenarioRunner", sr.count() > 0)

# === Scenarios ===
print("\n=== Scenarios ===")
from digital_twin.scenarios.scenario_engine import ScenarioEngine

sce = ScenarioEngine()
sce.start()
sce.create("sc1", "Market Expansion", "Expand to new region")
test("ScenarioEngine", sce.count() > 0)

from digital_twin.scenarios.scenario_builder import ScenarioBuilder

scb = ScenarioBuilder()
scb.create_template("expansion", {"investment": 100000, "region": "EU"})
test("ScenarioBuilder", scb.count() > 0)

from digital_twin.scenarios.scenario_manager import ScenarioManager

scm = ScenarioManager()
scm.add("sm1", "Cost Reduction")
test("ScenarioManager", scm.count() > 0)

from digital_twin.scenarios.comparison import ScenarioComparison

scc = ScenarioComparison()
scc.compare({"a": {"score": 0.8}, "b": {"score": 0.6}})
test("ScenarioComparison", scc.count() > 0)

from digital_twin.scenarios.history import ScenarioHistory

sch = ScenarioHistory()
sch.record("sc1", "created")
test("ScenarioHistory", sch.count() > 0)

from digital_twin.scenarios.templates import ScenarioTemplates

sct = ScenarioTemplates()
test("ScenarioTemplates", sct.count() > 0)

# === Prediction ===
print("\n=== Prediction ===")
from digital_twin.prediction.prediction_engine import PredictionEngine

pe = PredictionEngine()
pe.start()
pe.register_model("pm1", "Demand Model", "regression")
test("PredictionEngine", len(pe.list_models()) > 0)

from digital_twin.prediction.forecasting import Forecaster

fc = Forecaster()
fc.forecast([100, 110, 120, 130], horizon=5)
test("Forecaster", fc.count() > 0)

from digital_twin.prediction.risk_prediction import RiskPredictor

rp = RiskPredictor()
rp.assess({"scenario": "expansion"})
test("RiskPredictor", rp.count() > 0)

from digital_twin.prediction.demand_prediction import DemandPredictor

dp = DemandPredictor()
dp.predict("Product A", [100, 110, 120])
test("DemandPredictor", dp.count() > 0)

from digital_twin.prediction.failure_prediction import FailurePredictor

fp = FailurePredictor()
fp.predict("Engine", {"temperature": 85, "vibration": 6})
test("FailurePredictor", fp.count() > 0)

from digital_twin.prediction.outcome_prediction import OutcomePredictor

op = OutcomePredictor()
op.predict("Expansion", {"revenue": 100000, "cost": 50000})
test("OutcomePredictor", op.count() > 0)

# === Optimization ===
print("\n=== Optimization ===")
from digital_twin.optimization.optimization_engine import OptimizationEngine

oe = OptimizationEngine()
oe.start()
oe.define_problem("op1", "maximize_revenue", {"price": 100, "volume": 1000})
test("OptimizationEngine", len(oe.list_problems()) > 0)

from digital_twin.optimization.constraint_solver import ConstraintSolver

cs = ConstraintSolver()
cs.add_constraint("budget", "range", {"variable": "cost", "min": 0, "max": 50000})
test("ConstraintSolver", cs.count() > 0)

from digital_twin.optimization.cost_optimizer import CostOptimizer

co = CostOptimizer()
co.add_cost("marketing", 10000)
co.add_cost("operations", 20000)
test("CostOptimizer", co.count() > 0)

from digital_twin.optimization.performance_optimizer import PerformanceOptimizer

po = PerformanceOptimizer()
po.record("latency", 150)
po.record("latency", 120)
test("PerformanceOptimizer", po.count() > 0)

from digital_twin.optimization.resource_optimizer import ResourceOptimizer

ro = ResourceOptimizer()
ro.add_resource("compute", 100, 0.5)
test("ResourceOptimizer", ro.count() > 0)

from digital_twin.optimization.recommendation import RecommendationEngine

re = RecommendationEngine()
re.generate({"context": "cost_reduction"})
test("RecommendationEngine", re.count() > 0)

# === Synchronization ===
print("\n=== Synchronization ===")
from digital_twin.synchronization.sync_engine import SyncEngine

syse = SyncEngine()
syse.start()
syse.register_source("db1", "Production DB", "database")
test("SyncEngine", syse.count() > 0)

from digital_twin.synchronization.realtime_sync import RealtimeSync

rts = RealtimeSync()
rts.start()
test("RealtimeSync", rts.is_running())

from digital_twin.synchronization.data_mapper import DataMapper

dm = DataMapper()
dm.add_mapping("name_map", "full_name", "display_name")
test("DataMapper", dm.count() > 0)

from digital_twin.synchronization.update_manager import UpdateManager

um = UpdateManager()
um.queue_update("e1", "price", 100, 110)
test("UpdateManager", um.pending_count() > 0)

from digital_twin.synchronization.consistency import ConsistencyChecker

cc = ConsistencyChecker()
r = cc.check({"price": 100}, {"price": 100})
test("ConsistencyChecker", r["consistent"])

# === Visualization ===
print("\n=== Visualization ===")
from digital_twin.visualization.visualization_engine import VisualizationEngine

ve = VisualizationEngine()
ve.create_view("v1", "Sales Dashboard", "dashboard")
test("VisualizationEngine", ve.count() > 0)

from digital_twin.visualization.dashboard import Dashboard

db = Dashboard()
db.add_widget("w1", "chart", "Revenue Chart")
test("Dashboard", db.count() > 0)

from digital_twin.visualization.map_view import MapView

mv = MapView()
mv.add_marker("m1", 40.7128, -74.0060, "New York")
test("MapView", mv.count() > 0)

from digital_twin.visualization.timeline import Timeline

tl2 = Timeline()
tl2.add_event("e1", 1000, "Sale", "Product sold", "sales")
test("Timeline", tl2.count() > 0)

# === Analytics ===
print("\n=== Analytics ===")
from digital_twin.analytics.twin_analytics import TwinAnalytics

ta = TwinAnalytics()
ta.analyze({"twin_id": "t1"})
test("TwinAnalytics", ta.count() > 0)

from digital_twin.analytics.impact_analysis import ImpactAnalyzer

ia = ImpactAnalyzer()
ia.analyze({"change": "price_increase"}, ["sales", "margin"])
test("ImpactAnalyzer", ia.count() > 0)

from digital_twin.analytics.comparison import AnalyticsComparison

ac = AnalyticsComparison()
ac.compare({"model_a": {"score": 0.9}, "model_b": {"score": 0.7}})
test("AnalyticsComparison", ac.count() > 0)

from digital_twin.analytics.metrics import AnalyticsMetrics

am = AnalyticsMetrics()
am.record("latency", 150)
test("AnalyticsMetrics", am.count() > 0)

from digital_twin.analytics.reports import ReportGenerator

rg = ReportGenerator()
rg.generate("Monthly Report", {"sales": 50000})
test("ReportGenerator", rg.count() > 0)

# === Validation ===
print("\n=== Validation ===")
from digital_twin.validation.validation_engine import ValidationEngine

ve2 = ValidationEngine()
ve2.start()
ve2.register_validator("schema_v", "schema")
test("ValidationEngine", ve2.count() == 0)

from digital_twin.validation.accuracy import AccuracyValidator

av = AccuracyValidator()
av.validate([1, 2, 3], [1, 2, 4])
test("AccuracyValidator", av.count() > 0)

from digital_twin.validation.consistency import ConsistencyValidator

cv = ConsistencyValidator()
cv.add_rule("req_name", "field_exists", {"field": "name"})
test("ConsistencyValidator", len(cv.list_rules()) > 0)

from digital_twin.validation.calibration import CalibrationValidator

calv = CalibrationValidator()
calv.validate([0.8, 0.9, 0.7], [0.8, 0.85, 0.75])
test("CalibrationValidator", calv.count() > 0)

from digital_twin.validation.verification import VerificationEngine

ver = VerificationEngine()
ver.verify("check1", {"a": 1, "b": 2}, {"a": 1, "b": 2})
test("VerificationEngine", ver.count() > 0)

# === Summary ===
print(f"\n{'='*50}")
print(f"Volume 23 — Digital Twin: {passed}/{total} tests passed ({failed} failed)")
print(f"{'='*50}")
sys.exit(0 if failed == 0 else 1)
