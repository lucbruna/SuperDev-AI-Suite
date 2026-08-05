import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../config/api_config.dart';

class ApiException implements Exception {
  final String message;
  final int? statusCode;
  final Map<String, dynamic>? errors;

  ApiException(this.message, {this.statusCode, this.errors});

  @override
  String toString() => 'ApiException: $message (status: $statusCode)';
}

class ApiClient {
  static final ApiClient _instance = ApiClient._internal();
  factory ApiClient() => _instance;
  ApiClient._internal();

  final FlutterSecureStorage _secureStorage = const FlutterSecureStorage();
  final http.Client _httpClient = http.Client();
  String? _baseUrl;

  String get baseUrl => _baseUrl ?? ApiConfig.baseUrl;

  void setBaseUrl(String url) {
    _baseUrl = url;
  }

  Map<String, String> get _defaultHeaders => {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      };

  Future<Map<String, String>> _getHeaders() async {
    final headers = Map<String, String>.from(_defaultHeaders);
    final token = await _getToken();
    if (token != null && token.isNotEmpty) {
      headers['Authorization'] = 'Bearer $token';
    }
    return headers;
  }

  Future<String?> _getToken() async {
    try {
      return await _secureStorage.read(key: 'auth_token');
    } catch (e) {
      debugPrint('Error reading token: $e');
      return null;
    }
  }

  Future<Map<String, dynamic>> get(
    String endpoint, {
    Map<String, String>? queryParams,
    int retries = ApiConfig.maxRetries,
  }) async {
    return _request(
      'GET',
      endpoint,
      queryParams: queryParams,
      retries: retries,
    );
  }

  Future<Map<String, dynamic>> post(
    String endpoint, {
    Map<String, dynamic>? body,
    int retries = ApiConfig.maxRetries,
  }) async {
    return _request(
      'POST',
      endpoint,
      body: body,
      retries: retries,
    );
  }

  Future<Map<String, dynamic>> put(
    String endpoint, {
    Map<String, dynamic>? body,
    int retries = ApiConfig.maxRetries,
  }) async {
    return _request(
      'PUT',
      endpoint,
      body: body,
      retries: retries,
    );
  }

  Future<Map<String, dynamic>> delete(
    String endpoint, {
    int retries = ApiConfig.maxRetries,
  }) async {
    return _request(
      'DELETE',
      endpoint,
      retries: retries,
    );
  }

  Future<Map<String, dynamic>> _request(
    String method,
    String endpoint, {
    Map<String, dynamic>? body,
    Map<String, String>? queryParams,
    int retries = ApiConfig.maxRetries,
  }) async {
    int attempt = 0;
    while (attempt <= retries) {
      try {
        final uri = _buildUri(endpoint, queryParams);
        final headers = await _getHeaders();

        http.Response response;
        switch (method) {
          case 'GET':
            response = await _httpClient
                .get(uri, headers: headers)
                .timeout(ApiConfig.connectionTimeout);
            break;
          case 'POST':
            response = await _httpClient
                .post(uri, headers: headers, body: jsonEncode(body))
                .timeout(ApiConfig.connectionTimeout);
            break;
          case 'PUT':
            response = await _httpClient
                .put(uri, headers: headers, body: jsonEncode(body))
                .timeout(ApiConfig.connectionTimeout);
            break;
          case 'DELETE':
            response = await _httpClient
                .delete(uri, headers: headers)
                .timeout(ApiConfig.connectionTimeout);
            break;
          default:
            throw ApiException('Unsupported HTTP method: $method');
        }

        if (response.statusCode == 401) {
          final refreshed = await _tryRefreshToken();
          if (refreshed) {
            attempt++;
            continue;
          } else {
            throw ApiException(
              'Authentication failed',
              statusCode: 401,
            );
          }
        }

        if (response.statusCode >= 200 && response.statusCode < 300) {
          if (response.body.isEmpty) return {};
          final decoded = jsonDecode(response.body);
          if (decoded is List) {
            return {'data': decoded};
          }
          return decoded as Map<String, dynamic>;
        }

        final errorBody = _parseError(response);
        throw ApiException(
          errorBody['message'] as String? ?? 'Request failed',
          statusCode: response.statusCode,
          errors: errorBody['errors'] as Map<String, dynamic>?,
        );
      } on SocketException {
        attempt++;
        if (attempt > retries) {
          throw ApiException(
            'Connection failed. Please check your network.',
            statusCode: 0,
          );
        }
        await Future.delayed(ApiConfig.retryDelay);
      } on TimeoutException {
        attempt++;
        if (attempt > retries) {
          throw ApiException(
            'Request timed out. Please try again.',
            statusCode: 0,
          );
        }
        await Future.delayed(ApiConfig.retryDelay);
      } on http.ClientException {
        attempt++;
        if (attempt > retries) {
          throw ApiException(
            'Client error occurred. Please try again.',
            statusCode: 0,
          );
        }
        await Future.delayed(ApiConfig.retryDelay);
      } on FormatException catch (e) {
        throw ApiException('Invalid response format: ${e.message}');
      }
    }
    throw ApiException('Max retries exceeded');
  }

  Uri _buildUri(String endpoint, Map<String, String>? queryParams) {
    final uri = Uri.parse('$baseUrl$endpoint');
    if (queryParams != null && queryParams.isNotEmpty) {
      return uri.replace(queryParameters: queryParams);
    }
    return uri;
  }

  Map<String, dynamic> _parseError(http.Response response) {
    try {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } catch (_) {
      return {'message': response.body};
    }
  }

  Future<bool> _tryRefreshToken() async {
    try {
      final refreshToken = await _secureStorage.read(key: 'refresh_token');
      if (refreshToken == null || refreshToken.isEmpty) return false;

      final response = await _httpClient
          .post(
            Uri.parse('$baseUrl${ApiConfig.refreshTokenEndpoint}'),
            headers: _defaultHeaders,
            body: jsonEncode({'refresh_token': refreshToken}),
          )
          .timeout(ApiConfig.connectionTimeout);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        await _secureStorage.write(
          key: 'auth_token',
          value: data['access_token'] as String? ?? data['token'] as String? ?? '',
        );
        final newRefresh = data['refresh_token'] as String?;
        if (newRefresh != null) {
          await _secureStorage.write(key: 'refresh_token', value: newRefresh);
        }
        return true;
      }
      return false;
    } catch (e) {
      debugPrint('Token refresh failed: $e');
      return false;
    }
  }

  void dispose() {
    _httpClient.close();
  }
}
