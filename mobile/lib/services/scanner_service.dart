import 'package:flutter/foundation.dart';
import '../config/api_config.dart';
import '../models/scan_result.dart';
import 'api_client.dart';

class ScannerService {
  final ApiClient _apiClient = ApiClient();

  Future<ScanResult> processBarcode(String barcode, {String? format}) async {
    try {
      final response = await _apiClient.post(
        ApiConfig.scanEndpoint,
        body: {
          'barcode': barcode,
          'format': format ?? 'unknown',
        },
      );
      final data = response['data'] as Map<String, dynamic>? ?? response;
      return ScanResult.fromJson(data);
    } catch (e) {
      debugPrint('Error processing barcode: $e');
      return ScanResult(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        barcode: barcode,
        format: format ?? 'manual',
      );
    }
  }

  Future<List<ScanResult>> getScanHistory() async {
    try {
      final response = await _apiClient.get(ApiConfig.scanHistoryEndpoint);
      final dataList = response['data'] as List<dynamic>? ??
          (response['results'] as List<dynamic>? ?? []);
      return dataList
          .map((e) => ScanResult.fromJson(e as Map<String, dynamic>))
          .toList();
    } catch (e) {
      debugPrint('Error fetching scan history: $e');
      return [];
    }
  }
}
