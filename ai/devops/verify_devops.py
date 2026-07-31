"""Comprehensive tests for Volume 24 — Cloud Infrastructure & DevOps Engine."""

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
        print(f"  PASS: {name}")
    else:
        failed += 1
        print(f"  FAIL: {name}")


# === Core Infrastructure ===
print("\n=== Core Infrastructure ===")
from devops.devops_config import CloudProvider, DeployStrategy, DevOpsConfig

cfg = DevOpsConfig()
test("DevOpsConfig default", cfg.cloud_provider == CloudProvider.AWS)
test("DevOpsConfig strategy", cfg.deploy_strategy == DeployStrategy.ROLLING)

from devops.devops_models import Server

server = Server(name="web-01", cpu=8, memory_gb=32)
test("Server", server.name == "web-01")
test("Server cpu", server.cpu == 8)

from devops.devops_events import DevOpsEvents

ev = DevOpsEvents()
ev.emit("test", {"data": 1})
test("DevOpsEvents", len(ev.get_log()) > 0)

from devops.devops_metrics import DevOpsMetrics

dm = DevOpsMetrics()
dm.record_timer("deploy", 1500)
test("DevOpsMetrics", dm.get_timer_stats("deploy")["count"] == 1)

from devops.devops_logger import DevOpsLogger

dl = DevOpsLogger()
dl.info("test message")
test("DevOpsLogger", dl.count() > 0)

from devops.devops_security import DevOpsSecurity

ds = DevOpsSecurity()
ds.add_policy("p1", {"blocked": ["delete"]})
test("DevOpsSecurity", len(ds.list_policies()) > 0)

from devops.devops_context import DevOpsContext

dc = DevOpsContext()
dc.set("key", "value")
test("DevOpsContext", dc.get("key") == "value")

from devops.devops_registry import DevOpsRegistry

dr = DevOpsRegistry()
dr.register("r1", "Server 1", "server")
test("DevOpsRegistry", dr.count() > 0)

from devops.devops_runtime import DevOpsRuntime

drt = DevOpsRuntime()
drt.start()
test("DevOpsRuntime", drt.is_running())

from devops.devops_factory import DevOpsFactory

df = DevOpsFactory()
df.register_template("web", {"type": "web_server"})
test("DevOpsFactory", df.count() > 0)

from devops.devops_manager import DevOpsManager

dmgr = DevOpsManager()
dmgr.create("m1", "Resource 1")
test("DevOpsManager", dmgr.count() > 0)

from devops.devops_engine import DevOpsEngine

de = DevOpsEngine()
de.start()
test("DevOpsEngine", de.is_running())

# === Infrastructure ===
print("\n=== Infrastructure ===")
from devops.infrastructure.infrastructure_engine import InfrastructureEngine

ie = InfrastructureEngine()
ie.start()
ie.provision("server-1", "server")
test("InfrastructureEngine", ie.count() > 0)

from devops.infrastructure.resource_manager import ResourceManager

rm = ResourceManager()
rm.add("cpu", "compute", {"cores": 16})
test("ResourceManager", rm.count() > 0)

from devops.infrastructure.server_manager import ServerManager

sm = ServerManager()
sm.create("web-01", cpu=8, memory_gb=32)
test("ServerManager", sm.count() > 0)

from devops.infrastructure.network_manager import NetworkManager

nm = NetworkManager()
nm.create_network("prod-net", "10.0.0.0/16")
test("NetworkManager", nm.count() > 0)

from devops.infrastructure.storage_manager import StorageManager

stm = StorageManager()
stm.create_volume("data-vol", 500, "ssd")
test("StorageManager", stm.count() > 0)

from devops.infrastructure.provisioning import ProvisioningEngine

pe = ProvisioningEngine()
pe.create_template("web-server", {"cpu": 4, "memory": 16})
test("ProvisioningEngine", pe.count() == 0)

from devops.infrastructure.inventory import InventoryManager

im = InventoryManager()
im.add("i1", "Server 1", "server")
test("InventoryManager", im.count() > 0)

# === Containers ===
print("\n=== Containers ===")
from devops.containers.container_engine import ContainerEngine

ce = ContainerEngine()
ce.start()
ce.create("api-1", "superdev/api:latest")
test("ContainerEngine", ce.count() > 0)

from devops.containers.image_manager import ImageManager

imgm = ImageManager()
imgm.pull("superdev/api", "v1.0")
test("ImageManager", imgm.count() > 0)

from devops.containers.registry import ContainerRegistry

cr = ContainerRegistry()
cr.create_repository("superdev/api")
cr.push("superdev/api", "v1.0", "img-123")
test("ContainerRegistry", cr.count() > 0)

from devops.containers.builder import ImageBuilder

ib = ImageBuilder()
ib.build("Dockerfile", tags=["v1.0"])
test("ImageBuilder", ib.count() > 0)

from devops.containers.scanner import ImageScanner

isc = ImageScanner()
isc.scan("superdev/api:v1.0")
test("ImageScanner", isc.count() > 0)

from devops.containers.lifecycle import ContainerLifecycle

cl = ContainerLifecycle()
cl.track("c1", "created")
test("ContainerLifecycle", cl.count() > 0)

from devops.containers.runtime import ContainerRuntime

crt = ContainerRuntime()
crt.run("api-1", "superdev/api:latest")
test("ContainerRuntime", crt.count() > 0)

# === Kubernetes ===
print("\n=== Kubernetes ===")
from devops.kubernetes.kubernetes_engine import KubernetesEngine

ke = KubernetesEngine()
ke.start()
ke.create_cluster("prod-cluster", nodes=5)
test("KubernetesEngine", ke.count() > 0)

from devops.kubernetes.cluster_manager import ClusterManager

km = ClusterManager()
km.create("main-cluster")
test("ClusterManager", km.count() > 0)

from devops.kubernetes.node_manager import NodeManager

nodem = NodeManager()
nodem.add_node("node-1", "main-cluster", cpu=8, memory_gb=32)
test("NodeManager", nodem.count() > 0)

from devops.kubernetes.pod_manager import PodManager

pm = PodManager()
pm.create("api-pod", "default", "superdev/api:latest")
test("PodManager", pm.count() > 0)

from devops.kubernetes.service_manager import ServiceManager

svcm = ServiceManager()
svcm.create("api-svc", "default", "ClusterIP", [80, 443])
test("ServiceManager", svcm.count() > 0)

from devops.kubernetes.deployment_manager import DeploymentManager

kdm = DeploymentManager()
kdm.create("api-deploy", "default", "superdev/api:latest", replicas=3)
test("DeploymentManager", kdm.count() > 0)

from devops.kubernetes.ingress_manager import IngressManager

kim = IngressManager()
kim.create("api-ingress", "default", "api.example.com")
test("IngressManager", kim.count() > 0)

# === CI/CD ===
print("\n=== CI/CD ===")
from devops.cicd.cicd_engine import CICDEngine

cicd = CICDEngine()
cicd.start()
cicd.create_pipeline("main-pipeline", ["build", "test", "deploy"])
test("CICDEngine", cicd.count() > 0)

from devops.cicd.pipeline_builder import PipelineBuilder

pb = PipelineBuilder()
pb.create_template("standard", [{"stage": "build"}, {"stage": "test"}])
test("PipelineBuilder", pb.count() > 0)

from devops.cicd.build import BuildStage

bs = BuildStage()
bs.build("superdev-api", branch="main")
test("BuildStage", bs.count() > 0)

from devops.cicd.test_stage import TestStage

ts = TestStage()
ts.run_tests("superdev-api", "unit")
test("TestStage", ts.count() > 0)

from devops.cicd.security_stage import SecurityStage

ss = SecurityStage()
ss.scan("superdev-api", "sast")
test("SecurityStage", ss.count() > 0)

from devops.cicd.release import ReleaseManager

relm = ReleaseManager()
relm.create_release("v1.0.0", "superdev-api")
test("ReleaseManager", relm.count() > 0)

from devops.cicd.approval import ApprovalManager

am = ApprovalManager()
am.request("main-pipeline", "admin", "production")
test("ApprovalManager", am.count() > 0)

# === Deployment ===
print("\n=== Deployment ===")
from devops.deployment.deployment_engine import DeploymentEngine

depl = DeploymentEngine()
depl.start()
depl.deploy("api", "v1.0", "rolling")
test("DeploymentEngine", depl.count() > 0)

from devops.deployment.release_manager import ReleaseManager as RM2

rm2 = RM2()
rm2.create("v1.0", "api", ["api.tar.gz"])
test("ReleaseManager v2", rm2.count() > 0)

from devops.deployment.version_control import VersionControl

vc = VersionControl()
vc.tag("v1.0", "abc123", "Initial release")
test("VersionControl", vc.count() > 0)

from devops.deployment.rollback import RollbackManager

rbm = RollbackManager()
rbm.record("api", "v1.0", "v0.9", "bug fix")
test("RollbackManager", rbm.count() > 0)

from devops.deployment.blue_green import BlueGreenDeployer

bg = BlueGreenDeployer()
bg.setup("api", "v1.0", "v2.0")
test("BlueGreenDeployer", bg.count() > 0)

from devops.deployment.canary import CanaryDeployer

can = CanaryDeployer()
can.start("api", "v1.0", "v2.0", traffic_pct=10)
test("CanaryDeployer", can.count() > 0)

# === Scaling ===
print("\n=== Scaling ===")
from devops.scaling.scaling_engine import ScalingEngine

se = ScalingEngine()
se.start()
se.create_policy("api-scale", min_replicas=2, max_replicas=10, target_cpu=70)
test("ScalingEngine", se.count() > 0)

from devops.scaling.auto_scaler import AutoScaler

aus = AutoScaler()
aus.configure("api", min=2, max=10)
test("AutoScaler", aus.count() > 0)

from devops.scaling.resource_prediction import ResourcePredictor

rp = ResourcePredictor()
rp.predict("cpu", [50, 55, 60, 65, 70], horizon=24)
test("ResourcePredictor", rp.count() > 0)

from devops.scaling.load_balancer import LoadBalancer

lb = LoadBalancer()
lb.add_target("web-pool", "server-1")
lb.add_target("web-pool", "server-2")
test("LoadBalancer", lb.count() > 0)

from devops.scaling.capacity_planner import CapacityPlanner

cp = CapacityPlanner()
cp.create_plan("growth", {"cpu": 100, "memory": 200}, {"cpu": 200, "memory": 400})
test("CapacityPlanner", cp.count() > 0)

# === Backup ===
print("\n=== Backup ===")
from devops.backup.backup_engine import BackupEngine

be = BackupEngine()
be.start()
be.create_backup("daily-backup", "/data", "s3://backups")
test("BackupEngine", be.count() > 0)

from devops.backup.scheduler import BackupScheduler

bs2 = BackupScheduler()
bs2.create_schedule("daily", "/data", "daily", retention_days=30)
test("BackupScheduler", bs2.count() > 0)

from devops.backup.snapshot import SnapshotManager

sm2 = SnapshotManager()
sm2.create("pre-deploy", "/data", "Before deploy")
test("SnapshotManager", sm2.count() > 0)

from devops.backup.database_backup import DatabaseBackup

db = DatabaseBackup()
db.backup("main-db", "full")
test("DatabaseBackup", db.count() > 0)

from devops.backup.file_backup import FileBackup

fb = FileBackup()
fb.backup("/app/data", "s3://backups")
test("FileBackup", fb.count() > 0)

from devops.backup.restore import RestoreManager

rm3 = RestoreManager()
rm3.restore("backup-123", "/data")
test("RestoreManager", rm3.count() > 0)

# === Disaster Recovery ===
print("\n=== Disaster Recovery ===")
from devops.disaster_recovery.recovery_engine import RecoveryEngine

re = RecoveryEngine()
re.start()
re.create_plan("main-recovery", "Main recovery plan")
test("RecoveryEngine", re.count() > 0)

from devops.disaster_recovery.failover import FailoverManager

fm = FailoverManager()
fm.configure("api", "primary-db", "secondary-db")
test("FailoverManager", fm.count() > 0)

from devops.disaster_recovery.replication import ReplicationManager

rm4 = ReplicationManager()
rm4.setup("primary-db", "secondary-db", "sync")
test("ReplicationManager", rm4.count() > 0)

from devops.disaster_recovery.recovery_plan import RecoveryPlanManager

rpm = RecoveryPlanManager()
rpm.create("dr-plan", ["api", "database"], rto_minutes=30)
test("RecoveryPlanManager", rpm.count() > 0)

from devops.disaster_recovery.emergency_mode import EmergencyMode

em = EmergencyMode()
em.activate("major outage")
test("EmergencyMode", em.is_active())

# === Cloud ===
print("\n=== Cloud ===")
from devops.cloud.cloud_engine import CloudEngine

ce2 = CloudEngine()
ce2.start()
ce2.register_provider("aws-main", "aws")
test("CloudEngine", len(ce2.list_providers()) > 0)

from devops.cloud.aws import AWSProvider

aws = AWSProvider()
aws.create_instance("web-1", "t3.medium")
test("AWSProvider", aws.count() > 0)

from devops.cloud.azure import AzureProvider

azure = AzureProvider()
azure.create_vm("api-vm", "Standard_D2s_v3")
test("AzureProvider", azure.count() > 0)

from devops.cloud.google_cloud import GoogleCloudProvider

gcp = GoogleCloudProvider()
gcp.create_instance("worker-1", "e2-medium")
test("GoogleCloudProvider", gcp.count() > 0)

from devops.cloud.private_cloud import PrivateCloudProvider

priv = PrivateCloudProvider()
priv.create_vm("internal-1", cpu=16, memory_gb=64)
test("PrivateCloudProvider", priv.count() > 0)

from devops.cloud.hybrid_cloud import HybridCloudManager

hc = HybridCloudManager()
hc.register_provider("aws", aws)
test("HybridCloudManager", hc.count() == 0)

# === Configuration ===
print("\n=== Configuration ===")
from devops.configuration.config_engine import ConfigEngine

ce3 = ConfigEngine()
ce3.start()
ce3.set("db.host", "localhost")
test("ConfigEngine", ce3.get("db.host") == "localhost")

from devops.configuration.environment import EnvironmentManager

envm = EnvironmentManager()
envm.create("production", {"ENV": "prod"})
test("EnvironmentManager", envm.count() > 0)

from devops.configuration.variables import VariableManager

vm = VariableManager()
vm.set("API_KEY", "secret123", secret=True)
test("VariableManager", vm.count() > 0)

from devops.configuration.templates import ConfigTemplates

ct = ConfigTemplates()
ct.create("web-config", {"port": 80, "host": "0.0.0.0"})
test("ConfigTemplates", ct.count() > 0)

from devops.configuration.validation import ConfigValidator

cv = ConfigValidator()
cv.add_rule("port-required", "port", "required")
test("ConfigValidator", cv.count() > 0)

# === Secrets ===
print("\n=== Secrets ===")
from devops.secrets.secret_engine import SecretEngine

se2 = SecretEngine()
se2.start()
se2.set("db-password", "supersecret")
test("SecretEngine", se2.count() > 0)

from devops.secrets.vault import VaultManager

vault = VaultManager()
vault.create_vault("main-vault")
vault.store("main-vault", "api-key", "key123")
test("VaultManager", vault.count() > 0)

from devops.secrets.rotation import SecretRotation

sr = SecretRotation()
sr.schedule("db-password", interval_days=30)
test("SecretRotation", sr.count() > 0)

from devops.secrets.access import SecretAccess

sa = SecretAccess()
sa.add_policy("db-access", "db-password", ["admin", "dba"])
test("SecretAccess", sa.count() > 0)

from devops.secrets.encryption import EncryptionManager

enc = EncryptionManager()
enc.generate_key("master-key")
test("EncryptionManager", enc.count() > 0)

# === Monitoring ===
print("\n=== Monitoring ===")
from devops.monitoring.infra_monitor import InfraMonitor

im2 = InfraMonitor()
im2.record("server-1", "cpu", 75.0)
test("InfraMonitor", im2.count() > 0)

from devops.monitoring.resource_monitor import ResourceMonitor

resm = ResourceMonitor()
resm.register("server-1", "server")
resm.update_metrics("server-1", 80.0, 70.0, 50.0)
test("ResourceMonitor", resm.count() > 0)

from devops.monitoring.uptime import UptimeMonitor

um = UptimeMonitor()
um.register("api", "https://api.example.com")
test("UptimeMonitor", um.count() > 0)

from devops.monitoring.alerts import AlertManager

alm = AlertManager()
alm.create_rule("high-cpu", "cpu > 90", "critical")
test("AlertManager", alm.count() == 0)

from devops.monitoring.capacity import CapacityMonitor

cm = CapacityMonitor()
cm.set_capacity("cpu", 100, "cores")
test("CapacityMonitor", cm.count() > 0)

# === Summary ===
print(f"\n{'=' * 50}")
print(f"Volume 24 — DevOps: {passed}/{total} tests passed ({failed} failed)")
print(f"{'=' * 50}")
sys.exit(0 if failed == 0 else 1)
