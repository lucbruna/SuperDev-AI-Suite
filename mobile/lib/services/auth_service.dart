import 'package:flutter/foundation.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../config/api_config.dart';
import '../models/user.dart';
import 'api_client.dart';

class AuthService {
  final ApiClient _apiClient = ApiClient();
  final FlutterSecureStorage _secureStorage = const FlutterSecureStorage();

  Future<Map<String, dynamic>> login(String username, String password) async {
    final response = await _apiClient.post(
      ApiConfig.loginEndpoint,
      body: {
        'username': username,
        'password': password,
      },
    );

    final token = response['access_token'] as String? ??
        response['token'] as String? ??
        '';
    final refreshToken = response['refresh_token'] as String?;

    if (token.isNotEmpty) {
      await saveToken(token);
      if (refreshToken != null) {
        await _secureStorage.write(key: 'refresh_token', value: refreshToken);
      }
    }

    return response;
  }

  Future<Map<String, dynamic>> register(Map<String, dynamic> data) async {
    final response = await _apiClient.post(
      ApiConfig.registerEndpoint,
      body: data,
    );

    final token = response['access_token'] as String? ??
        response['token'] as String? ??
        '';
    if (token.isNotEmpty) {
      await saveToken(token);
      final refreshToken = response['refresh_token'] as String?;
      if (refreshToken != null) {
        await _secureStorage.write(key: 'refresh_token', value: refreshToken);
      }
    }

    return response;
  }

  Future<void> logout() async {
    try {
      await _apiClient.post(ApiConfig.logoutEndpoint);
    } catch (e) {
      debugPrint('Logout API call failed: $e');
    }
    await clearToken();
  }

  Future<String?> getToken() async {
    try {
      return await _secureStorage.read(key: 'auth_token');
    } catch (e) {
      debugPrint('Error reading token: $e');
      return null;
    }
  }

  Future<void> saveToken(String token) async {
    await _secureStorage.write(key: 'auth_token', value: token);
  }

  Future<void> clearToken() async {
    await _secureStorage.delete(key: 'auth_token');
    await _secureStorage.delete(key: 'refresh_token');
  }

  Future<User?> getCurrentUser() async {
    try {
      final response = await _apiClient.get(ApiConfig.userEndpoint);
      final userData = response['data'] as Map<String, dynamic>? ?? response;
      return User.fromJson(userData);
    } catch (e) {
      debugPrint('Error fetching current user: $e');
      return null;
    }
  }

  Future<bool> isLoggedIn() async {
    final token = await getToken();
    return token != null && token.isNotEmpty;
  }
}
