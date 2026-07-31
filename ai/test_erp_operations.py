"""ERP Operations — Comprehensive test suite."""

# Core models
from erp_operations.automation.engine import AutomationEngine
from erp_operations.automation.models import AutomationRule, AutomationStatus, ScheduledTask

# Core engine
from erp_operations.erp_engine import ERPEngine
from erp_operations.erp_models import (
    Delivery,
    Employee,
    Order,
    OrderStatus,
    Product,
    PurchaseOrder,
    Supplier,
    WarehouseLocation,
    WorkflowApproval,
    WorkflowStatus,
    WorkOrder,
)
from erp_operations.hr.engine import HREngine
from erp_operations.hr.models import Department, LeaveRequest, LeaveStatus, LeaveType, PayrollRecord
from erp_operations.hr.models import Employee as HREmployee
from erp_operations.hr.models import EmployeeStatus as HREmpStatus
from erp_operations.inventory.engine import InventoryEngine

# Subsystem models and engines
from erp_operations.inventory.models import InventoryItem, MovementType
from erp_operations.inventory.models import StockMovement as InvMovement
from erp_operations.logistics.engine import LogisticsEngine
from erp_operations.logistics.models import Carrier, CarrierType, DeliveryProof, Route, Shipment, ShipmentStatus
from erp_operations.production.engine import ProductionEngine
from erp_operations.production.models import (
    BOM,
    ProductionLine,
    ProductionOrder,
    ProductionStatus,
    QualityCheck,
    QualityStatus,
)
from erp_operations.purchases.engine import PurchasesEngine
from erp_operations.purchases.models import PurchaseOrder as PurchPO
from erp_operations.purchases.models import PurchaseOrderStatus
from erp_operations.sales.engine import SalesEngine
from erp_operations.sales.models import (
    Commission,
    Quotation,
    QuotationStatus,
    SalesOrder,
    SalesOrderStatus,
    SalesTarget,
)
from erp_operations.suppliers.engine import SuppliersEngine
from erp_operations.suppliers.models import Supplier as SupSupplier
from erp_operations.suppliers.models import SupplierPerformance, SupplierStatus
from erp_operations.warehouse.engine import WarehouseEngine
from erp_operations.warehouse.models import Bin, BinStatus, PickTask, WarehouseZone, WarehouseZoneModel
from erp_operations.workflow.engine import WorkflowEngine
from erp_operations.workflow.models import StepStatus, StepType, WorkflowDefinition, WorkflowInstance, WorkflowStep
from erp_operations.workflow.models import WorkflowStatus as WfStatus

# ========== Core ERPEngine Tests ==========

class TestERPEngine:
    def test_add_product(self):
        engine = ERPEngine()
        p = Product(product_id="P001", name="Widget", sku="W001", price=10.0)
        engine.add_product(p)
        assert engine.get_product("P001") is p

    def test_list_products(self):
        engine = ERPEngine()
        engine.add_product(Product(product_id="P001", name="A", category="cat1"))
        engine.add_product(Product(product_id="P002", name="B", category="cat2"))
        engine.add_product(Product(product_id="P003", name="C", category="cat1"))
        assert len(engine.list_products("cat1")) == 2

    def test_update_stock_in(self):
        engine = ERPEngine()
        p = Product(product_id="P001", stock_quantity=10)
        engine.add_product(p)
        assert engine.update_stock("P001", 5, "in") is True
        assert p.stock_quantity == 15

    def test_update_stock_out(self):
        engine = ERPEngine()
        p = Product(product_id="P001", stock_quantity=10)
        engine.add_product(p)
        assert engine.update_stock("P001", 3, "out") is True
        assert p.stock_quantity == 7

    def test_update_stock_out_insufficient(self):
        engine = ERPEngine()
        p = Product(product_id="P001", stock_quantity=2)
        engine.add_product(p)
        assert engine.update_stock("P001", 5, "out") is False

    def test_create_order(self):
        engine = ERPEngine()
        o = Order(order_id="O001", customer_id="C001", total=100.0)
        engine.add_order(o)
        assert engine.get_order("O001") is o

    def test_update_order_status(self):
        engine = ERPEngine()
        o = Order(order_id="O001", status=OrderStatus.DRAFT)
        engine.add_order(o)
        assert engine.update_order_status("O001", OrderStatus.CONFIRMED) is True
        assert o.status == OrderStatus.CONFIRMED

    def test_create_purchase_order(self):
        engine = ERPEngine()
        po = PurchaseOrder(po_id="PO001", supplier_id="S001", total=500.0)
        engine.add_purchase_order(po)
        assert engine.get_purchase_order("PO001") is po

    def test_approve_purchase(self):
        engine = ERPEngine()
        po = PurchaseOrder(po_id="PO001", status=OrderStatus.DRAFT)
        engine.add_purchase_order(po)
        assert engine.update_order_status is not None

    def test_add_supplier(self):
        engine = ERPEngine()
        s = Supplier(supplier_id="S001", name="Acme")
        engine.add_supplier(s)
        assert engine.get_supplier("S001") is s

    def test_add_employee(self):
        engine = ERPEngine()
        e = Employee(employee_id="E001", name="John", department="Engineering")
        engine.add_employee(e)
        assert engine.get_employee("E001") is e

    def test_create_delivery(self):
        engine = ERPEngine()
        d = Delivery(delivery_id="D001", order_id="O001", origin="A", destination="B")
        engine.add_delivery(d)
        assert engine.get_delivery("D001") is d

    def test_create_work_order(self):
        engine = ERPEngine()
        w = WorkOrder(work_order_id="W001", product_id="P001", quantity=10)
        engine.add_work_order(w)
        assert engine.get_work_order("W001") is w

    def test_add_location(self):
        engine = ERPEngine()
        loc = WarehouseLocation(location_id="L001", name="Zone A", capacity=100)
        engine.add_location(loc)
        assert engine.get_location("L001") is loc

    def test_add_approval(self):
        engine = ERPEngine()
        app = WorkflowApproval(approval_id="A001", workflow_name="order_approval", entity_type="order", entity_id="O001", requested_by="user1")
        engine.add_approval(app)
        assert len(engine.get_approvals()) == 1

    def test_get_approvals_filtered(self):
        engine = ERPEngine()
        app = WorkflowApproval(approval_id="A001", workflow_name="order_approval", status=WorkflowStatus.PENDING)
        engine.add_approval(app)
        assert len(engine.get_approvals(WorkflowStatus.PENDING)) == 1
        assert len(engine.get_approvals(WorkflowStatus.APPROVED)) == 0


# ========== Inventory Subsystem Tests ==========

class TestInventorySubsystem:
    def test_add_item(self):
        engine = InventoryEngine()
        item = InventoryItem(item_id="I001", name="Bolt", quantity=100, min_quantity=10, max_quantity=500)
        engine.add_item(item)
        assert engine.get_item("I001") is item

    def test_stock_movement_in(self):
        engine = InventoryEngine()
        item = InventoryItem(item_id="I001", quantity=50)
        engine.add_item(item)
        mov = InvMovement(movement_id="M001", item_id="I001", movement_type=MovementType.IN, quantity=30)
        engine.record_movement(mov)
        assert item.quantity == 80

    def test_stock_movement_out(self):
        engine = InventoryEngine()
        item = InventoryItem(item_id="I001", quantity=50)
        engine.add_item(item)
        mov = InvMovement(movement_id="M001", item_id="I001", movement_type=MovementType.OUT, quantity=20)
        engine.record_movement(mov)
        assert item.quantity == 30

    def test_low_stock_detection(self):
        engine = InventoryEngine()
        item = InventoryItem(item_id="I001", quantity=5, min_quantity=10)
        engine.add_item(item)
        low = engine.get_low_stock_items()
        assert len(low) == 1

    def test_replenishment_alert(self):
        engine = InventoryEngine()
        item = InventoryItem(item_id="I001", quantity=3, min_quantity=10, max_quantity=100)
        engine.add_item(item)
        alerts = engine.check_replenishment()
        assert len(alerts) == 1
        assert alerts[0].suggested_order == 97

    def test_stats(self):
        engine = InventoryEngine()
        engine.add_item(InventoryItem(item_id="I001", quantity=10, cost=5.0))
        engine.add_item(InventoryItem(item_id="I002", quantity=20, cost=3.0))
        stats = engine.get_stats()
        assert stats["total_items"] == 2
        assert stats["total_value"] == 110.0


# ========== Sales Subsystem Tests ==========

class TestSalesSubsystem:
    def test_create_order(self):
        engine = SalesEngine()
        order = SalesOrder(order_id="SO001", customer_id="C001", total=250.0)
        engine.create_order(order)
        assert engine.get_order("SO001") is order

    def test_update_status(self):
        engine = SalesEngine()
        order = SalesOrder(order_id="SO001", status=SalesOrderStatus.DRAFT)
        engine.create_order(order)
        assert engine.update_order_status("SO001", SalesOrderStatus.CONFIRMED) is True

    def test_create_quotation(self):
        engine = SalesEngine()
        q = Quotation(quotation_id="Q001", customer_id="C001", total=500.0)
        engine.create_quotation(q)
        assert engine.get_quotation("Q001") is q

    def test_accept_quotation(self):
        engine = SalesEngine()
        q = Quotation(quotation_id="Q001", status=QuotationStatus.SENT)
        engine.create_quotation(q)
        assert engine.accept_quotation("Q001") is True
        assert q.status == QuotationStatus.ACCEPTED

    def test_target(self):
        engine = SalesEngine()
        t = SalesTarget(target_id="T001", sales_rep="rep1", target_amount=10000, achieved=3000)
        engine.set_target(t)
        assert engine.get_target("T001") is t
        assert t.achievement_pct == 30.0

    def test_commission(self):
        engine = SalesEngine()
        c = Commission(commission_id="CM001", sales_rep="rep1", order_id="SO001", rate=0.1, earned=25.0)
        engine.add_commission(c)
        assert len(engine.get_commissions("rep1")) == 1

    def test_stats(self):
        engine = SalesEngine()
        engine.create_order(SalesOrder(order_id="SO001", total=100))
        engine.create_order(SalesOrder(order_id="SO002", total=200))
        stats = engine.get_stats()
        assert stats["total_orders"] == 2
        assert stats["total_revenue"] == 300


# ========== Purchases Subsystem Tests ==========

class TestPurchasesSubsystem:
    def test_create_order(self):
        engine = PurchasesEngine()
        po = PurchPO(po_id="PO001", supplier_id="S001", total=1000.0)
        engine.create_order(po)
        assert engine.get_order("PO001") is po

    def test_approve_order(self):
        engine = PurchasesEngine()
        po = PurchPO(po_id="PO001")
        engine.create_order(po)
        assert engine.approve_order("PO001", "manager1") is True
        assert po.status == PurchaseOrderStatus.APPROVED

    def test_compare_prices(self):
        engine = PurchasesEngine()
        comp = engine.compare_prices("P001", {"S001": 10.0, "S002": 8.0, "S003": 12.0})
        assert comp.best_supplier == "S002"
        assert comp.best_price == 8.0
        assert comp.savings == 4.0

    def test_orders_by_supplier(self):
        engine = PurchasesEngine()
        engine.create_order(PurchPO(po_id="PO001", supplier_id="S001"))
        engine.create_order(PurchPO(po_id="PO002", supplier_id="S001"))
        engine.create_order(PurchPO(po_id="PO003", supplier_id="S002"))
        assert len(engine.get_orders_by_supplier("S001")) == 2


# ========== Suppliers Subsystem Tests ==========

class TestSuppliersSubsystem:
    def test_add_supplier(self):
        engine = SuppliersEngine()
        s = SupSupplier(supplier_id="S001", name="Acme", rating=4.5)
        engine.add_supplier(s)
        assert engine.get_supplier("S001") is s

    def test_rate_supplier(self):
        engine = SuppliersEngine()
        s = SupSupplier(supplier_id="S001")
        engine.add_supplier(s)
        assert engine.rate_supplier("S001", 4.2) is True
        assert s.rating == 4.2

    def test_rate_supplier_clamp(self):
        engine = SuppliersEngine()
        s = SupSupplier(supplier_id="S001")
        engine.add_supplier(s)
        engine.rate_supplier("S001", 6.0)
        assert s.rating == 5.0

    def test_top_suppliers(self):
        engine = SuppliersEngine()
        engine.add_supplier(SupSupplier(supplier_id="S001", name="A", rating=4.0, status=SupplierStatus.ACTIVE))
        engine.add_supplier(SupSupplier(supplier_id="S002", name="B", rating=4.8, status=SupplierStatus.ACTIVE))
        engine.add_supplier(SupSupplier(supplier_id="S003", name="C", rating=3.5, status=SupplierStatus.ACTIVE))
        top = engine.get_top_suppliers(2)
        assert len(top) == 2
        assert top[0].rating >= top[1].rating

    def test_performance(self):
        engine = SuppliersEngine()
        perf = SupplierPerformance(performance_id="P001", supplier_id="S001", on_time_delivery=95, quality_score=90, price_competitiveness=85)
        result = engine.add_performance(perf)
        assert result.overall_score == 90.0

    def test_stats(self):
        engine = SuppliersEngine()
        engine.add_supplier(SupSupplier(supplier_id="S001", rating=4.0, status=SupplierStatus.ACTIVE))
        stats = engine.get_stats()
        assert stats["total_suppliers"] == 1
        assert stats["avg_rating"] == 4.0


# ========== Production Subsystem Tests ==========

class TestProductionSubsystem:
    def test_create_order(self):
        engine = ProductionEngine()
        order = ProductionOrder(order_id="PR001", product_id="P001", quantity=100)
        engine.create_order(order)
        assert engine.get_order("PR001") is order

    def test_update_status(self):
        engine = ProductionEngine()
        order = ProductionOrder(order_id="PR001", status=ProductionStatus.PLANNED)
        engine.create_order(order)
        assert engine.update_order_status("PR001", ProductionStatus.IN_PROGRESS) is True

    def test_add_line(self):
        engine = ProductionEngine()
        line = ProductionLine(line_id="L001", name="Line A", capacity=500, efficiency=85.0)
        engine.add_line(line)
        assert line.utilization == 0.0

    def test_assign_to_line(self):
        engine = ProductionEngine()
        order = ProductionOrder(order_id="PR001")
        line = ProductionLine(line_id="L001", capacity=10)
        engine.create_order(order)
        engine.add_line(line)
        assert engine.assign_order_to_line("PR001", "L001") is True
        assert order.assigned_line == "L001"

    def test_quality_check(self):
        engine = ProductionEngine()
        check = QualityCheck(check_id="QC001", order_id="PR001", status=QualityStatus.PASSED, score=98.0)
        engine.add_quality_check(check)
        checks = engine.get_quality_checks("PR001")
        assert len(checks) == 1

    def test_bom(self):
        engine = ProductionEngine()
        bom = BOM(bom_id="BOM001", product_id="P001", components=[{"id": "C1", "qty": 2}], total_cost=50.0)
        engine.add_bom(bom)
        assert engine.get_bom("BOM001") is bom

    def test_stats(self):
        engine = ProductionEngine()
        engine.create_order(ProductionOrder(order_id="PR001", status=ProductionStatus.IN_PROGRESS))
        engine.create_order(ProductionOrder(order_id="PR002", status=ProductionStatus.COMPLETED))
        stats = engine.get_stats()
        assert stats["total_orders"] == 2
        assert stats["in_progress"] == 1
        assert stats["completed"] == 1


# ========== Logistics Subsystem Tests ==========

class TestLogisticsSubsystem:
    def test_create_shipment(self):
        engine = LogisticsEngine()
        s = Shipment(shipment_id="SH001", order_id="O001", carrier="FedEx")
        engine.create_shipment(s)
        assert engine.get_shipment("SH001") is s

    def test_update_status(self):
        engine = LogisticsEngine()
        s = Shipment(shipment_id="SH001", status=ShipmentStatus.PENDING)
        engine.create_shipment(s)
        assert engine.update_shipment_status("SH001", ShipmentStatus.IN_TRANSIT) is True
        assert s.status == ShipmentStatus.IN_TRANSIT

    def test_delivered_status_sets_date(self):
        engine = LogisticsEngine()
        s = Shipment(shipment_id="SH001", status=ShipmentStatus.IN_TRANSIT)
        engine.create_shipment(s)
        engine.update_shipment_status("SH001", ShipmentStatus.DELIVERED)
        assert s.actual_delivery is not None

    def test_find_routes(self):
        engine = LogisticsEngine()
        engine.add_route(Route(route_id="R001", name="A to B", origin="NYC", destination="LA"))
        engine.add_route(Route(route_id="R002", name="C to D", origin="Chicago", destination="Miami"))
        routes = engine.find_routes("NYC", "LA")
        assert len(routes) == 1

    def test_best_carrier(self):
        engine = LogisticsEngine()
        engine.add_carrier(Carrier(carrier_id="C001", name="Fast", cost_per_km=0.5, max_weight=100, active=True))
        engine.add_carrier(Carrier(carrier_id="C002", name="Cheap", cost_per_km=0.2, max_weight=100, active=True))
        best = engine.get_best_carrier(50)
        assert best.carrier_id == "C002"

    def test_best_carrier_by_type(self):
        engine = LogisticsEngine()
        engine.add_carrier(Carrier(carrier_id="C001", name="Air", cost_per_km=1.0, max_weight=100, active=True, carrier_type=CarrierType.AIR))
        engine.add_carrier(Carrier(carrier_id="C002", name="Road", cost_per_km=0.3, max_weight=100, active=True, carrier_type=CarrierType.ROAD))
        best = engine.get_best_carrier(50, CarrierType.AIR)
        assert best.carrier_id == "C001"

    def test_delivery_proof(self):
        engine = LogisticsEngine()
        proof = DeliveryProof(proof_id="DP001", shipment_id="SH001", recipient="John")
        engine.add_delivery_proof(proof)
        assert engine.get_proof("SH001") is proof

    def test_stats(self):
        engine = LogisticsEngine()
        engine.create_shipment(Shipment(shipment_id="SH001", status=ShipmentStatus.DELIVERED))
        engine.create_shipment(Shipment(shipment_id="SH002", status=ShipmentStatus.IN_TRANSIT))
        stats = engine.get_stats()
        assert stats["total_shipments"] == 2
        assert stats["delivered"] == 1


# ========== Warehouse Subsystem Tests ==========

class TestWarehouseSubsystem:
    def test_add_zone(self):
        engine = WarehouseEngine()
        zone = WarehouseZoneModel(zone_id="Z001", name="Storage A", zone_type=WarehouseZone.STORAGE, capacity=500)
        engine.add_zone(zone)
        assert engine.get_zone("Z001") is zone

    def test_add_bin(self):
        engine = WarehouseEngine()
        b = Bin(bin_id="B001", zone_id="Z001", aisle="A1", rack="R1", level=1, position=1, max_capacity=100)
        engine.add_bin(b)
        assert engine.get_bin("B001") is b

    def test_find_empty_bins(self):
        engine = WarehouseEngine()
        engine.add_bin(Bin(bin_id="B001", zone_id="Z001", status=BinStatus.EMPTY))
        engine.add_bin(Bin(bin_id="B002", zone_id="Z001", status=BinStatus.FULL))
        empty = engine.find_empty_bins("Z001")
        assert len(empty) == 1

    def test_assign_product_to_bin(self):
        engine = WarehouseEngine()
        b = Bin(bin_id="B001", zone_id="Z001", max_capacity=100)
        engine.add_bin(b)
        assert engine.assign_product_to_bin("B001", "P001", 50) is True
        assert b.quantity == 50
        assert b.status == BinStatus.PARTIAL

    def test_zone_utilization(self):
        engine = WarehouseEngine()
        zone = WarehouseZoneModel(zone_id="Z001", capacity=100, current_usage=25)
        engine.add_zone(zone)
        assert engine.get_zone_utilization("Z001") == 25.0

    def test_pick_tasks(self):
        engine = WarehouseEngine()
        engine.create_pick_task(PickTask(task_id="PT001", order_id="O001", status="pending"))
        engine.create_pick_task(PickTask(task_id="PT002", order_id="O001", status="completed"))
        pending = engine.get_pending_picks()
        assert len(pending) == 1

    def test_stats(self):
        engine = WarehouseEngine()
        engine.add_zone(WarehouseZoneModel(zone_id="Z001"))
        engine.add_bin(Bin(bin_id="B001", status=BinStatus.EMPTY))
        engine.add_bin(Bin(bin_id="B002", status=BinStatus.FULL))
        stats = engine.get_stats()
        assert stats["total_bins"] == 2
        assert stats["empty_bins"] == 1
        assert stats["full_bins"] == 1


# ========== HR Subsystem Tests ==========

class TestHRSubsystem:
    def test_add_employee(self):
        engine = HREngine()
        e = HREmployee(employee_id="E001", name="John", department="Engineering", salary=80000)
        engine.add_employee(e)
        assert engine.get_employee("E001") is e

    def test_update_status(self):
        engine = HREngine()
        e = HREmployee(employee_id="E001", status=HREmpStatus.ACTIVE)
        engine.add_employee(e)
        assert engine.update_employee_status("E001", HREmpStatus.ON_LEAVE) is True
        assert e.status == HREmpStatus.ON_LEAVE

    def test_leave_request(self):
        engine = HREngine()
        req = LeaveRequest(request_id="LR001", employee_id="E001", leave_type=LeaveType.ANNUAL, days=5)
        engine.submit_leave_request(req)
        assert engine.approve_leave("LR001", "mgr1") is True
        assert req.status == LeaveStatus.APPROVED

    def test_leave_balance(self):
        engine = HREngine()
        engine.submit_leave_request(LeaveRequest(request_id="LR001", employee_id="E001", leave_type=LeaveType.ANNUAL, days=5, status=LeaveStatus.APPROVED))
        balance = engine.get_leave_balance("E001", LeaveType.ANNUAL)
        assert balance == 15

    def test_payroll(self):
        engine = HREngine()
        record = PayrollRecord(record_id="PR001", employee_id="E001", base_salary=5000, bonus=500, deductions=800)
        result = engine.process_payroll(record)
        assert result.net_pay == 4700
        assert result.status == "processed"

    def test_department(self):
        engine = HREngine()
        dept = Department(department_id="D001", name="Engineering", headcount=10, budget=500000)
        engine.add_department(dept)
        assert engine.get_department("D001") is dept

    def test_employees_by_department(self):
        engine = HREngine()
        engine.add_employee(HREmployee(employee_id="E001", department="Eng"))
        engine.add_employee(HREmployee(employee_id="E002", department="Eng"))
        engine.add_employee(HREmployee(employee_id="E003", department="Sales"))
        assert len(engine.get_employees_by_department("Eng")) == 2

    def test_stats(self):
        engine = HREngine()
        engine.add_employee(HREmployee(employee_id="E001", status=HREmpStatus.ACTIVE))
        stats = engine.get_stats()
        assert stats["total_employees"] == 1
        assert stats["active"] == 1


# ========== Workflow Subsystem Tests ==========

class TestWorkflowSubsystem:
    def test_create_definition(self):
        engine = WorkflowEngine()
        defn = WorkflowDefinition(workflow_id="WF001", name="Approval Process")
        engine.create_definition(defn)
        assert engine.get_definition("WF001") is defn

    def test_activate_definition(self):
        engine = WorkflowEngine()
        defn = WorkflowDefinition(workflow_id="WF001", status=WfStatus.DRAFT)
        engine.create_definition(defn)
        assert engine.activate_definition("WF001") is True
        assert defn.status == WfStatus.ACTIVE

    def test_add_step(self):
        engine = WorkflowEngine()
        step = WorkflowStep(step_id="S001", workflow_id="WF001", name="Manager Approval", step_type=StepType.APPROVAL, order=1)
        engine.add_step(step)
        steps = engine.get_workflow_steps("WF001")
        assert len(steps) == 1

    def test_start_instance(self):
        engine = WorkflowEngine()
        inst = WorkflowInstance(instance_id="I001", workflow_id="WF001", initiated_by="user1")
        engine.start_instance(inst)
        assert engine.get_instance("I001") is inst

    def test_complete_step(self):
        engine = WorkflowEngine()
        step = WorkflowStep(step_id="S001", workflow_id="WF001")
        engine.add_step(step)
        assert engine.complete_step("S001") is True
        assert step.status == StepStatus.COMPLETED

    def test_approve_step(self):
        engine = WorkflowEngine()
        step = WorkflowStep(step_id="S001", workflow_id="WF001")
        engine.add_step(step)
        record = engine.approve_step("S001", "mgr1", "approved", "Looks good")
        assert record.decision == "approved"
        assert step.status == StepStatus.COMPLETED

    def test_get_approvals(self):
        engine = WorkflowEngine()
        step = WorkflowStep(step_id="S001", workflow_id="WF001")
        engine.add_step(step)
        engine.approve_step("S001", "mgr1", "approved")
        approvals = engine.get_approvals()
        assert len(approvals) == 1

    def test_stats(self):
        engine = WorkflowEngine()
        engine.create_definition(WorkflowDefinition(workflow_id="WF001"))
        engine.start_instance(WorkflowInstance(instance_id="I001", status=WfStatus.ACTIVE))
        stats = engine.get_stats()
        assert stats["definitions"] == 1
        assert stats["instances"] == 1
        assert stats["active"] == 1


# ========== Automation Subsystem Tests ==========

class TestAutomationSubsystem:
    def test_create_rule(self):
        engine = AutomationEngine()
        rule = AutomationRule(rule_id="AR001", name="Email on order", status=AutomationStatus.ACTIVE)
        engine.create_rule(rule)
        assert engine.get_rule("AR001") is rule

    def test_activate_deactivate(self):
        engine = AutomationEngine()
        rule = AutomationRule(rule_id="AR001", status=AutomationStatus.INACTIVE)
        engine.create_rule(rule)
        assert engine.activate_rule("AR001") is True
        assert rule.status == AutomationStatus.ACTIVE
        assert engine.deactivate_rule("AR001") is True
        assert rule.status == AutomationStatus.INACTIVE

    def test_execute_rule(self):
        engine = AutomationEngine()
        rule = AutomationRule(rule_id="AR001", actions=[{"type": "email"}])
        engine.create_rule(rule)
        exec_result = engine.execute_rule("AR001", {"order_id": "O001"})
        assert exec_result.status == "success"
        assert rule.run_count == 1

    def test_get_executions(self):
        engine = AutomationEngine()
        engine.create_rule(AutomationRule(rule_id="AR001"))
        engine.execute_rule("AR001")
        engine.execute_rule("AR001")
        execs = engine.get_executions("AR001")
        assert len(execs) == 2

    def test_schedule_task(self):
        engine = AutomationEngine()
        task = ScheduledTask(task_id="ST001", rule_id="AR001", cron="0 9 * * *")
        engine.schedule_task(task)
        assert len(engine.get_scheduled_tasks()) == 1

    def test_get_active_rules(self):
        engine = AutomationEngine()
        engine.create_rule(AutomationRule(rule_id="AR001", status=AutomationStatus.ACTIVE))
        engine.create_rule(AutomationRule(rule_id="AR002", status=AutomationStatus.INACTIVE))
        active = engine.get_active_rules()
        assert len(active) == 1

    def test_metrics(self):
        engine = AutomationEngine()
        engine.create_rule(AutomationRule(rule_id="AR001", status=AutomationStatus.ACTIVE))
        engine.execute_rule("AR001")
        metrics = engine.get_metrics()
        assert metrics.total_executions == 1
        assert metrics.success_rate == 100.0
        assert metrics.active_rules == 1


# ========== Integration Tests ==========

class TestERPIntegration:
    def test_full_order_lifecycle(self):
        engine = ERPEngine()
        product = Product(product_id="P001", name="Widget", price=25.0, stock_quantity=100)
        engine.add_product(product)
        order = Order(order_id="O001", customer_id="C001", items=[{"product_id": "P001", "qty": 2}], total=50.0)
        engine.add_order(order)
        engine.update_order_status("O001", OrderStatus.CONFIRMED)
        engine.update_stock("P001", 2, "out")
        assert product.stock_quantity == 98
        assert order.status == OrderStatus.CONFIRMED

    def test_supplier_purchase_flow(self):
        engine = ERPEngine()
        supplier = Supplier(supplier_id="S001", name="Acme")
        engine.add_supplier(supplier)
        po = PurchaseOrder(po_id="PO001", supplier_id="S001", total=1000.0)
        engine.add_purchase_order(po)
        assert engine.get_purchase_order("PO001") is po

    def test_hr_and_workflow(self):
        engine = ERPEngine()
        employee = Employee(employee_id="E001", name="Alice", department="HR")
        engine.add_employee(employee)
        app = WorkflowApproval(approval_id="A001", workflow_name="leave", entity_type="leave", entity_id="LR001", requested_by="E001")
        engine.add_approval(app)
        assert len(engine.get_approvals()) == 1

    def test_cross_subsystem_inventory_to_sales(self):
        inv = InventoryEngine()
        sales = SalesEngine()
        inv.add_item(InventoryItem(item_id="I001", name="Widget", quantity=50))
        order = SalesOrder(order_id="SO001", customer_id="C001", total=100.0)
        sales.create_order(order)
        inv.record_movement(InvMovement(movement_id="M001", item_id="I001", movement_type=MovementType.OUT, quantity=5))
        assert inv.get_item("I001").quantity == 45
        assert sales.get_order("SO001") is order
