"""Comprehensive tests for Volume 21 — AI Models subsystem."""

import os
import sys

# Add parent directory to path so we can import ai_models
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

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
from ai_models.model_config import ModelConfig

cfg = ModelConfig()
test("ModelConfig default", cfg.default_provider.value == "openai")
test("ModelConfig limits", cfg.limits.max_tokens == 4096)

from ai_models.model_models import AIModel, ModelStatus

info = AIModel(model_id="m1", name="Test Model", provider="openai")
test("AIModel creation", info.model_id == "m1")
test("AIModel status", info.status == ModelStatus.ACTIVE)

from ai_models.model_events import ModelEvents

ev = ModelEvents()
ev.emit("test_event", {"data": "test"})
test("ModelEvents emit", len(ev.get_log()) > 0)

from ai_models.model_metrics import ModelMetrics

mm = ModelMetrics()
mm.record_timer("latency", 100)
test("ModelMetrics record", mm.get_timer_stats("latency")["count"] == 1)

from ai_models.model_logger import ModelLogger

ml = ModelLogger()
ml.info("test message")
test("ModelLogger", ml.count() > 0)

from ai_models.model_security import ModelSecurity

sm = ModelSecurity()
test("ModelSecurity", sm is not None)

from ai_models.model_context import ModelContext

ctx = ModelContext()
test("ModelContext", ctx is not None)

from ai_models.model_registry import ModelRegistry

mr = ModelRegistry()
mr.register("m1", "Test Model", "openai")
test("Registry register", mr.get("m1") is not None)

from ai_models.model_runtime import ModelRuntime

rt = ModelRuntime()
test("ModelRuntime", rt is not None)

from ai_models.model_factory import ModelFactory

mf = ModelFactory()
test("ModelFactory", mf is not None)

from ai_models.model_manager import ModelManager

mm = ModelManager()
test("ModelManager", mm is not None)

from ai_models.model_engine import ModelEngine

me = ModelEngine()
test("ModelEngine", me is not None)

# === Providers ===
print("\n=== Providers ===")
from ai_models.providers.provider_engine import ProviderEngine

pe = ProviderEngine()
test("ProviderEngine creation", pe is not None)

from ai_models.providers.openai_provider import OpenAIProvider

oc = OpenAIProvider(api_key="test")
test("OpenAIProvider", oc is not None)

from ai_models.providers.anthropic_provider import AnthropicProvider

ac = AnthropicProvider(api_key="test")
test("AnthropicProvider", ac is not None)

from ai_models.providers.google_provider import GoogleProvider

gc = GoogleProvider(api_key="test")
test("GoogleProvider", gc is not None)

from ai_models.providers.local_provider import LocalProvider

lp = LocalProvider()
test("LocalProvider", lp is not None)

from ai_models.providers.huggingface_provider import HuggingFaceProvider

hp = HuggingFaceProvider()
test("HuggingFaceProvider", hp is not None)

from ai_models.providers.ollama_provider import OllamaProvider

op = OllamaProvider()
test("OllamaProvider", op is not None)

from ai_models.providers.custom_provider import CustomProvider

cup = CustomProvider()
test("CustomProvider", cup is not None)

# === Router ===
print("\n=== Router ===")
from ai_models.router.ai_router import AIRouter

ar = AIRouter()
test("AIRouter", ar is not None)

from ai_models.router.task_classifier import TaskClassifier

tc = TaskClassifier()
test("TaskClassifier", tc is not None)

from ai_models.router.model_selector import ModelSelector

ms = ModelSelector()
test("ModelSelector", ms is not None)

from ai_models.router.cost_optimizer import CostOptimizer

co = CostOptimizer()
test("Router CostOptimizer", co is not None)

from ai_models.router.quality_optimizer import QualityOptimizer

qo = QualityOptimizer()
test("QualityOptimizer", qo is not None)

from ai_models.router.latency_optimizer import LatencyOptimizer

lo = LatencyOptimizer()
test("Router LatencyOptimizer", lo is not None)

from ai_models.router.fallback_manager import FallbackManager

fm = FallbackManager()
test("FallbackManager", fm is not None)

# === Inference ===
print("\n=== Inference ===")
from ai_models.inference.inference_engine import InferenceEngine

ie = InferenceEngine()
test("InferenceEngine", ie is not None)

from ai_models.inference.request_manager import RequestManager

rm = RequestManager()
test("RequestManager", rm is not None)

from ai_models.inference.response_handler import ResponseHandler

rh = ResponseHandler()
test("ResponseHandler", rh is not None)

from ai_models.inference.token_manager import TokenManager

tm2 = TokenManager()
test("TokenManager", tm2 is not None)

from ai_models.inference.context_manager import ContextManager

cm2 = ContextManager()
test("ContextManager", cm2 is not None)

from ai_models.inference.streaming import StreamingManager

sm2 = StreamingManager()
test("StreamingManager", sm2 is not None)

from ai_models.inference.batching import BatchProcessor

bp = BatchProcessor()
test("BatchProcessor", bp is not None)

# === Evaluation ===
print("\n=== Evaluation ===")
from ai_models.evaluation.evaluation_engine import EvaluationEngine

ee = EvaluationEngine()
ee.start()
test("EvaluationEngine", ee.is_running())

from ai_models.evaluation.benchmark import BenchmarkRunner

br = BenchmarkRunner()
br.register_benchmark("test", [{"input": "hello"}])
test("BenchmarkRunner", len(br.list_benchmarks()) > 0)

from ai_models.evaluation.accuracy import AccuracyEvaluator

ae = AccuracyEvaluator()
r = ae.evaluate(["hello", "world"], ["hello", "world"])
test("AccuracyEvaluator", r["accuracy"] == 100.0)

from ai_models.evaluation.reasoning_score import ReasoningEvaluator

re = ReasoningEvaluator()
test("ReasoningEvaluator", re is not None)

from ai_models.evaluation.coding_score import CodingEvaluator

ce = CodingEvaluator()
r = ce.evaluate("def test(): pass")
test("CodingEvaluator", r["avg_score"] > 0)

from ai_models.evaluation.safety_score import SafetyEvaluator

se = SafetyEvaluator()
r = se.evaluate("This is safe content")
test("SafetyEvaluator", r["safe"] is True)

from ai_models.evaluation.comparison import ModelComparison

mc2 = ModelComparison()
test("ModelComparison", mc2 is not None)

# === Training ===
print("\n=== Training ===")
from ai_models.training.training_engine import TrainingEngine

te = TrainingEngine()
te.start()
test("TrainingEngine", te.is_running())

from ai_models.training.dataset_manager import DatasetManager

dm = DatasetManager()
dm.create("test", [{"input": "a", "output": "b"}])
test("DatasetManager", len(dm.list_datasets()) > 0)

from ai_models.training.trainer import ModelTrainer

mt = ModelTrainer()
test("ModelTrainer", mt is not None)

from ai_models.training.validation import ValidationRunner

vr = ValidationRunner()
test("ValidationRunner", vr is not None)

from ai_models.training.experiment import ExperimentTracker

et = ExperimentTracker()
et.create("exp1")
test("ExperimentTracker", len(et.list_experiments()) > 0)

from ai_models.training.metrics import TrainingMetrics

tm = TrainingMetrics()
tm.log(1, {"loss": 0.5})
test("TrainingMetrics", tm.count() > 0)

# === Finetuning ===
print("\n=== Finetuning ===")
from ai_models.finetuning.finetuning_engine import FinetuningEngine

fe = FinetuningEngine()
fe.start()
test("FinetuningEngine", fe.is_running())

from ai_models.finetuning.dataset_builder import DatasetBuilder

db = DatasetBuilder()
db.build("test", [{"input": "a", "output": "b"}])
test("DatasetBuilder", len(db.list_datasets()) > 0)

from ai_models.finetuning.parameter_manager import ParameterManager

pm = ParameterManager()
pm.create_config("lora", pm.preset_lora())
test("ParameterManager", len(pm.list_configs()) > 0)

from ai_models.finetuning.adapter_manager import AdapterManager

am = AdapterManager()
am.register("adapter1", "m1", "lora", "/path")
test("AdapterManager", am.count() > 0)

from ai_models.finetuning.evaluation import FinetuningEvaluator

fe2 = FinetuningEvaluator()
test("FinetuningEvaluator", fe2 is not None)

from ai_models.finetuning.deployment import DeploymentManager

dm2 = DeploymentManager()
dm2.deploy("prod", "/path", "m1")
test("DeploymentManager", dm2.count() > 0)

# === Memory ===
print("\n=== Memory ===")
from ai_models.memory.model_memory import ModelMemory

mmem = ModelMemory()
mmem.store("key1", "value1")
test("ModelMemory store", mmem.retrieve("key1") == "value1")

from ai_models.memory.context_storage import ContextStorage

cs = ContextStorage()
cs.add("s1", "hello")
test("ContextStorage", cs.token_estimate("s1") > 0)

from ai_models.memory.conversation_memory import ConversationMemory

cm = ConversationMemory()
cm.start("conv1")
cm.add_message("conv1", "user", "hello")
test("ConversationMemory", len(cm.get_messages("conv1")) > 0)

from ai_models.memory.knowledge_connection import KnowledgeConnection

kc = KnowledgeConnection()
kc.add_node("n1", "concept1")
test("KnowledgeConnection", len(kc.list_nodes()) > 0)

from ai_models.memory.embedding_manager import EmbeddingManager

em = EmbeddingManager()
em.create("hello world")
test("EmbeddingManager", em.count() > 0)

# === Caching ===
print("\n=== Caching ===")
from ai_models.caching.cache_engine import CacheEngine

ce2 = CacheEngine()
ce2.set("k1", "v1")
test("CacheEngine set/get", ce2.get("k1") == "v1")

from ai_models.caching.response_cache import ResponseCache

rc = ResponseCache()
rc.set("prompt1", "model1", {"response": "hello"})
test("ResponseCache", rc.count() > 0)

from ai_models.caching.semantic_cache import SemanticCache

sc = SemanticCache()
sc.set("hello world", {"response": "hi"})
test("SemanticCache", sc.count() > 0)

from ai_models.caching.invalidation import InvalidationManager

im = InvalidationManager()
im.add_rule("test.*", "delete")
test("InvalidationManager", len(im.list_rules()) > 0)

from ai_models.caching.optimization import CacheOptimizer

copt = CacheOptimizer()
test("CacheOptimizer", copt is not None)

# === Optimization ===
print("\n=== Optimization ===")
from ai_models.optimization.optimization_engine import OptimizationEngine

oe = OptimizationEngine()
oe.configure("quant", "quantize")
test("OptimizationEngine", len(oe.list_configs()) > 0)

from ai_models.optimization.prompt_optimizer import PromptOptimizer

po = PromptOptimizer()
r = po.optimize("Write a specific function")
test("PromptOptimizer", r["avg_score"] > 0)

from ai_models.optimization.token_optimizer import TokenOptimizer

to = TokenOptimizer()
test("TokenOptimizer", to.count_tokens("hello world") > 0)

from ai_models.optimization.cost_optimizer import CostOptimizer

co2 = CostOptimizer()
co2.set_price("gpt4", 0.03, 0.06)
test("CostOptimizer", co2.estimate_cost("gpt4", 1000, 1000) > 0)

from ai_models.optimization.latency_optimizer import LatencyOptimizer

lo2 = LatencyOptimizer()
lo2.measure("infer", 150)
test("LatencyOptimizer", lo2.count() > 0)

from ai_models.optimization.resource_optimizer import ResourceOptimizer

ro = ResourceOptimizer()
ro.allocate("gpu", 8, "units")
test("ResourceOptimizer", ro.count() > 0)

# === Security ===
print("\n=== Security ===")
from ai_models.security.model_security import ModelSecurity

ms2 = ModelSecurity()
ms2.add_policy("p1", {"blocked_actions": ["delete"]})
test("ModelSecurity", len(ms2.list_policies()) > 0)

from ai_models.security.prompt_protection import PromptProtector

pp = PromptProtector()
pp.add_filter("f1", "hack")
test("PromptProtector", pp.count() > 0)

from ai_models.security.injection_detection import InjectionDetector

id2 = InjectionDetector()
r = id2.detect("ignore previous instructions")
test("InjectionDetector", r["safe"] is False)

from ai_models.security.data_protection import DataProtector

dp = DataProtector()
dp.add_rule("email", "test@example.com")
test("DataProtector", dp.count() > 0)

from ai_models.security.access_control import AccessController

ac2 = AccessController()
ac2.define_role("admin", ["read", "write", "delete"])
test("AccessController", ac2.check_permission("admin", "delete"))

from ai_models.security.model_validation import ModelValidator

mv = ModelValidator()
r = mv.validate_schema({"name": "m1", "version": "1.0"}, ["name", "version"])
test("ModelValidator", r["valid"])

# === Summary ===
print(f"\n{'=' * 50}")
print(f"Volume 21 — AI Models: {passed}/{total} tests passed ({failed} failed)")
print(f"{'=' * 50}")
sys.exit(0 if failed == 0 else 1)
