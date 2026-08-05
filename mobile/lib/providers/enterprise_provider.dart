import 'package:flutter/foundation.dart';
import '../models/enterprise.dart';
import '../services/enterprise_service.dart';

class EnterpriseProvider extends ChangeNotifier {
  final EnterpriseService _service = EnterpriseService();

  List<Product> _products = [];
  List<Lead> _leads = [];
  List<SaleOrder> _saleOrders = [];
  List<Invoice> _invoices = [];
  List<StockItem> _stockItems = [];
  List<PipelineStage> _pipeline = [];
  List<CashFlowEntry> _cashFlow = [];
  List<CashRegister> _cashRegisters = [];

  bool _isLoadingProducts = false;
  bool _isLoadingLeads = false;
  bool _isLoadingSales = false;
  bool _isLoadingInvoices = false;
  bool _isLoadingStock = false;
  bool _isLoadingPipeline = false;

  String? _error;

  List<Product> get products => _products;
  List<Lead> get leads => _leads;
  List<SaleOrder> get saleOrders => _saleOrders;
  List<Invoice> get invoices => _invoices;
  List<StockItem> get stockItems => _stockItems;
  List<PipelineStage> get pipeline => _pipeline;
  List<CashFlowEntry> get cashFlow => _cashFlow;
  List<CashRegister> get cashRegisters => _cashRegisters;

  bool get isLoadingProducts => _isLoadingProducts;
  bool get isLoadingLeads => _isLoadingLeads;
  bool get isLoadingSales => _isLoadingSales;
  bool get isLoadingInvoices => _isLoadingInvoices;
  bool get isLoadingStock => _isLoadingStock;
  bool get isLoadingPipeline => _isLoadingPipeline;
  bool get isLoadingAny =>
      _isLoadingProducts ||
      _isLoadingLeads ||
      _isLoadingSales ||
      _isLoadingInvoices ||
      _isLoadingStock ||
      _isLoadingPipeline;

  String? get error => _error;

  List<StockItem> get lowStockItems =>
      _stockItems.where((item) => item.isLowStock).toList();

  double get totalPipelineValue =>
      _pipeline.fold(0.0, (sum, stage) => sum + stage.totalValue);

  double get totalReceivable =>
      _invoices
          .where((inv) => inv.status == 'pending' || inv.status == 'overdue')
          .fold(0.0, (sum, inv) => sum + (inv.dueAmount ?? inv.amount));

  Future<void> loadProducts({String? search}) async {
    _isLoadingProducts = true;
    _error = null;
    notifyListeners();

    try {
      _products = await _service.getProducts(search: search);
    } catch (e) {
      _error = 'Failed to load products: $e';
      debugPrint(_error);
    }

    _isLoadingProducts = false;
    notifyListeners();
  }

  Future<void> createProduct(Map<String, dynamic> data) async {
    try {
      await _service.createProduct(data);
      await loadProducts();
    } catch (e) {
      _error = 'Failed to create product: $e';
      notifyListeners();
    }
  }

  Future<void> updateProduct(int id, Map<String, dynamic> data) async {
    try {
      await _service.updateProduct(id, data);
      await loadProducts();
    } catch (e) {
      _error = 'Failed to update product: $e';
      notifyListeners();
    }
  }

  Future<void> loadLeads() async {
    _isLoadingLeads = true;
    _error = null;
    notifyListeners();

    try {
      _leads = await _service.getLeads();
    } catch (e) {
      _error = 'Failed to load leads: $e';
      debugPrint(_error);
    }

    _isLoadingLeads = false;
    notifyListeners();
  }

  Future<void> createLead(Map<String, dynamic> data) async {
    try {
      await _service.createLead(data);
      await loadLeads();
    } catch (e) {
      _error = 'Failed to create lead: $e';
      notifyListeners();
    }
  }

  Future<void> loadPipeline() async {
    _isLoadingPipeline = true;
    _error = null;
    notifyListeners();

    try {
      _pipeline = await _service.getPipeline();
    } catch (e) {
      _error = 'Failed to load pipeline: $e';
      debugPrint(_error);
    }

    _isLoadingPipeline = false;
    notifyListeners();
  }

  Future<void> loadSaleOrders() async {
    _isLoadingSales = true;
    _error = null;
    notifyListeners();

    try {
      _saleOrders = await _service.getSaleOrders();
    } catch (e) {
      _error = 'Failed to load sales: $e';
      debugPrint(_error);
    }

    _isLoadingSales = false;
    notifyListeners();
  }

  Future<SaleOrder?> registerSale(Map<String, dynamic> data) async {
    try {
      final order = await _service.registerSale(data);
      await loadSaleOrders();
      return order;
    } catch (e) {
      _error = 'Failed to register sale: $e';
      notifyListeners();
      return null;
    }
  }

  Future<void> loadInvoices() async {
    _isLoadingInvoices = true;
    _error = null;
    notifyListeners();

    try {
      _invoices = await _service.getInvoices();
    } catch (e) {
      _error = 'Failed to load invoices: $e';
      debugPrint(_error);
    }

    _isLoadingInvoices = false;
    notifyListeners();
  }

  Future<void> loadStockLevels() async {
    _isLoadingStock = true;
    _error = null;
    notifyListeners();

    try {
      _stockItems = await _service.getStockLevels();
    } catch (e) {
      _error = 'Failed to load stock levels: $e';
      debugPrint(_error);
    }

    _isLoadingStock = false;
    notifyListeners();
  }

  Future<void> registerStockMovement(Map<String, dynamic> data) async {
    try {
      await _service.registerStockMovement(data);
      await loadStockLevels();
    } catch (e) {
      _error = 'Failed to register stock movement: $e';
      notifyListeners();
    }
  }

  Future<void> loadCashFlow() async {
    try {
      _cashFlow = await _service.getCashFlow();
      notifyListeners();
    } catch (e) {
      _error = 'Failed to load cash flow: $e';
      notifyListeners();
    }
  }

  Future<void> loadCashRegisters() async {
    try {
      _cashRegisters = await _service.getCashRegisters();
      notifyListeners();
    } catch (e) {
      _error = 'Failed to load cash registers: $e';
      notifyListeners();
    }
  }

  Future<void> registerPayment(Map<String, dynamic> data) async {
    try {
      await _service.registerPayment(data);
      await loadInvoices();
    } catch (e) {
      _error = 'Failed to register payment: $e';
      notifyListeners();
    }
  }

  Future<void> refreshAll() async {
    await Future.wait([
      loadProducts(),
      loadLeads(),
      loadSaleOrders(),
      loadInvoices(),
      loadStockLevels(),
      loadPipeline(),
      loadCashFlow(),
      loadCashRegisters(),
    ]);
  }

  void clearError() {
    _error = null;
    notifyListeners();
  }
}
