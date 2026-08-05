class ApiConfig {
  static const String baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://localhost:8000/api',
  );

  static const Duration connectionTimeout = Duration(seconds: 30);
  static const Duration receiveTimeout = Duration(seconds: 30);

  static const String loginEndpoint = '/auth/login';
  static const String registerEndpoint = '/auth/register';
  static const String refreshTokenEndpoint = '/auth/refresh';
  static const String logoutEndpoint = '/auth/logout';
  static const String userEndpoint = '/auth/me';

  static const String productsEndpoint = '/enterprise/products';
  static const String saleOrdersEndpoint = '/enterprise/sale-orders';
  static const String leadsEndpoint = '/enterprise/leads';
  static const String opportunitiesEndpoint = '/enterprise/opportunities';
  static const String pipelineEndpoint = '/enterprise/pipeline';
  static const String invoicesEndpoint = '/enterprise/invoices';
  static const String stockEndpoint = '/enterprise/stock';
  static const String stockMovementsEndpoint = '/enterprise/stock-movements';
  static const String cashRegisterEndpoint = '/enterprise/cash-register';
  static const String cashFlowEndpoint = '/enterprise/cash-flow';
  static const String paymentsEndpoint = '/enterprise/payments';

  static const String scanEndpoint = '/scanner/process';
  static const String scanHistoryEndpoint = '/scanner/history';

  static const String aiChatEndpoint = '/ai/chat';
  static const String aiCodeEndpoint = '/ai/code';

  static const int maxRetries = 3;
  static const Duration retryDelay = Duration(seconds: 2);
}
