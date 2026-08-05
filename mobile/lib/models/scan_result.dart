class ScanResult {
  final String id;
  final String barcode;
  final String format;
  final String? productName;
  final DateTime scannedAt;
  final Map<String, dynamic>? rawData;

  ScanResult({
    required this.id,
    required this.barcode,
    required this.format,
    this.productName,
    DateTime? scannedAt,
    this.rawData,
  }) : scannedAt = scannedAt ?? DateTime.now();

  factory ScanResult.fromJson(Map<String, dynamic> json) {
    return ScanResult(
      id: json['id'] as String? ?? '',
      barcode: json['barcode'] as String? ?? '',
      format: json['format'] as String? ?? 'unknown',
      productName: json['product_name'] as String? ?? json['productName'] as String?,
      scannedAt: json['scanned_at'] != null
          ? DateTime.parse(json['scanned_at'] as String)
          : DateTime.now(),
      rawData: json['raw_data'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'barcode': barcode,
      'format': format,
      'product_name': productName,
      'scanned_at': scannedAt.toIso8601String(),
      'raw_data': rawData,
    };
  }
}
