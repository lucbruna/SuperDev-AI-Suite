import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  final String baseUrl;
  final String? apiKey;

  ApiService({required this.baseUrl, this.apiKey});

  Map<String, String> get _headers => {
        'Content-Type': 'application/json',
        if (apiKey != null) 'Authorization': 'Bearer $apiKey',
      };

  Future<Map<String, dynamic>> get(String path) async {
    final response = await http.get(
      Uri.parse('$baseUrl$path'),
      headers: _headers,
    );
    if (response.statusCode >= 400) {
      throw Exception('HTTP ${response.statusCode}');
    }
    return jsonDecode(response.body);
  }

  Future<Map<String, dynamic>> post(String path, Map<String, dynamic> body) async {
    final response = await http.post(
      Uri.parse('$baseUrl$path'),
      headers: _headers,
      body: jsonEncode(body),
    );
    if (response.statusCode >= 400) {
      throw Exception('HTTP ${response.statusCode}');
    }
    return jsonDecode(response.body);
  }
}
