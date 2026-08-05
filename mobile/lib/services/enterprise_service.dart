import '../config/api_config.dart';
import '../models/enterprise.dart';
import 'api_client.dart';

class EnterpriseService {
  final ApiClient _apiClient = ApiClient();

  Future<List<Product>> getProducts({String? search}) async {
    final params = <String, String>{};
    if (search != null && search.isNotEmpty) {
      params['search'] = search;
    }
    final response = await _apiClient.get(
      ApiConfig.productsEndpoint,
      queryParams: params.isNotEmpty ? params : null,
    );
    final dataList = response['data'] as List<dynamic>? ??
        (response['results'] as List<dynamic>? ?? [response]);
    return dataList
        .map((e) => Product.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<Product> createProduct(Map<String, dynamic> data) async {
    final response = await _apiClient.post(
      ApiConfig.productsEndpoint,
      body: data,
    );
    final productData = response['data'] as Map<String, dynamic>? ?? response;
    return Product.fromJson(productData);
  }

  Future<Product> updateProduct(int id, Map<String, dynamic> data) async {
    final response = await _apiClient.put(
      '${ApiConfig.productsEndpoint}/$id',
      body: data,
    );
    final productData = response['data'] as Map<String, dynamic>? ?? response;
    return Product.fromJson(productData);
  }

  Future<List<Lead>> getLeads() async {
    final response = await _apiClient.get(ApiConfig.leadsEndpoint);
    final dataList = response['data'] as List<dynamic>? ??
        (response['results'] as List<dynamic>? ?? [response]);
    return dataList
        .map((e) => Lead.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<Lead> createLead(Map<String, dynamic> data) async {
    final response = await _apiClient.post(
      ApiConfig.leadsEndpoint,
      body: data,
    );
    final leadData = response['data'] as Map<String, dynamic>? ?? response;
    return Lead.fromJson(leadData);
  }

  Future<List<PipelineStage>> getPipeline() async {
    final response = await _apiClient.get(ApiConfig.pipelineEndpoint);
    final dataList = response['data'] as List<dynamic>? ??
        (response['stages'] as List<dynamic>? ?? []);
    return dataList
        .map((e) => PipelineStage.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<SaleOrder> registerSale(Map<String, dynamic> data) async {
    final response = await _apiClient.post(
      ApiConfig.saleOrdersEndpoint,
      body: data,
    );
    final orderData = response['data'] as Map<String, dynamic>? ?? response;
    return SaleOrder.fromJson(orderData);
  }

  Future<List<StockItem>> getStockLevels() async {
    final response = await _apiClient.get(ApiConfig.stockEndpoint);
    final dataList = response['data'] as List<dynamic>? ??
        (response['results'] as List<dynamic>? ?? [response]);
    return dataList
        .map((e) => StockItem.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<StockMovement> registerStockMovement(Map<String, dynamic> data) async {
    final response = await _apiClient.post(
      ApiConfig.stockMovementsEndpoint,
      body: data,
    );
    final movementData =
        response['data'] as Map<String, dynamic>? ?? response;
    return StockMovement.fromJson(movementData);
  }

  Future<List<Invoice>> getInvoices() async {
    final response = await _apiClient.get(ApiConfig.invoicesEndpoint);
    final dataList = response['data'] as List<dynamic>? ??
        (response['results'] as List<dynamic>? ?? [response]);
    return dataList
        .map((e) => Invoice.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<Invoice> createInvoice(Map<String, dynamic> data) async {
    final response = await _apiClient.post(
      ApiConfig.invoicesEndpoint,
      body: data,
    );
    final invoiceData = response['data'] as Map<String, dynamic>? ?? response;
    return Invoice.fromJson(invoiceData);
  }

  Future<List<CashRegister>> getCashRegisters() async {
    final response = await _apiClient.get(ApiConfig.cashRegisterEndpoint);
    final dataList = response['data'] as List<dynamic>? ??
        (response['results'] as List<dynamic>? ?? [response]);
    return dataList
        .map((e) => CashRegister.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<List<CashFlowEntry>> getCashFlow() async {
    final response = await _apiClient.get(ApiConfig.cashFlowEndpoint);
    final dataList = response['data'] as List<dynamic>? ??
        (response['results'] as List<dynamic>? ?? [response]);
    return dataList
        .map((e) => CashFlowEntry.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<List<SaleOrder>> getSaleOrders() async {
    final response = await _apiClient.get(ApiConfig.saleOrdersEndpoint);
    final dataList = response['data'] as List<dynamic>? ??
        (response['results'] as List<dynamic>? ?? [response]);
    return dataList
        .map((e) => SaleOrder.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<PaymentRecord> registerPayment(Map<String, dynamic> data) async {
    final response = await _apiClient.post(
      ApiConfig.paymentsEndpoint,
      body: data,
    );
    final paymentData = response['data'] as Map<String, dynamic>? ?? response;
    return PaymentRecord.fromJson(paymentData);
  }

  Future<List<Opportunity>> getOpportunities() async {
    final response = await _apiClient.get(ApiConfig.opportunitiesEndpoint);
    final dataList = response['data'] as List<dynamic>? ??
        (response['results'] as List<dynamic>? ?? [response]);
    return dataList
        .map((e) => Opportunity.fromJson(e as Map<String, dynamic>))
        .toList();
  }
}
