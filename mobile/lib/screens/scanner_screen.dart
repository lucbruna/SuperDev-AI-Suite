import 'package:flutter/material.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import 'package:qr_flutter/qr_flutter.dart';
import '../config/theme.dart';
import '../models/scan_result.dart';
import '../services/scanner_service.dart';

class ScannerScreen extends StatefulWidget {
  const ScannerScreen({super.key});

  @override
  State<ScannerScreen> createState() => _ScannerScreenState();
}

class _ScannerScreenState extends State<ScannerScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final ScannerService _scannerService = ScannerService();
  final TextEditingController _manualController = TextEditingController();
  List<ScanResult> _scanHistory = [];
  ScanResult? _lastResult;
  bool _isScanning = true;
  bool _torchOn = false;
  MobileScannerController? _cameraController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _cameraController = MobileScannerController();
    _loadHistory();
  }

  @override
  void dispose() {
    _tabController.dispose();
    _manualController.dispose();
    _cameraController?.dispose();
    super.dispose();
  }

  Future<void> _loadHistory() async {
    final history = await _scannerService.getScanHistory();
    if (mounted) {
      setState(() => _scanHistory = history);
    }
  }

  void _onDetect(BarcodeCapture capture) {
    if (!_isScanning) return;
    final barcode = capture.barcodes.firstOrNull;
    if (barcode != null && barcode.rawValue != null) {
      _isScanning = false;
      _processResult(barcode.rawValue!, barcode.format.name);
    }
  }

  Future<void> _processResult(String barcode, String format) async {
    final result = await _scannerService.processBarcode(barcode, format: format);
    if (!mounted) return;
    setState(() {
      _lastResult = result;
      _scanHistory.insert(0, result);
    });
    _showResultDialog(result);
    Future.delayed(const Duration(seconds: 2), () {
      if (mounted) setState(() => _isScanning = true);
    });
  }

  void _manualSubmit() {
    final text = _manualController.text.trim();
    if (text.isEmpty) return;
    _processResult(text, 'manual');
    _manualController.clear();
  }

  void _showResultDialog(ScanResult result) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: Row(
          children: [
            const Icon(Icons.check_circle, color: AppTheme.successGreen),
            const SizedBox(width: 8),
            const Text('Scan Result'),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _resultRow('Barcode', result.barcode),
            _resultRow('Format', result.format),
            if (result.productName != null)
              _resultRow('Product', result.productName!),
            _resultRow('Scanned at',
                '${result.scannedAt.hour}:${result.scannedAt.minute.toString().padLeft(2, '0')}'),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Close'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(ctx);
            },
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }

  Widget _resultRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 80,
            child: Text(
              label,
              style: TextStyle(
                color: Colors.grey.shade600,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
          Expanded(child: Text(value)),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      appBar: AppBar(
        title: const Text('Scanner'),
        actions: [
          IconButton(
            icon: Icon(_torchOn ? Icons.flash_on : Icons.flash_off),
            onPressed: () {
              setState(() => _torchOn = !_torchOn);
              _cameraController?.toggleTorch();
            },
          ),
        ],
        bottom: TabBar(
          controller: _tabController,
          tabs: [
            Tab(
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.qr_code_scanner, size: 18),
                  const SizedBox(width: 6),
                  Text('Scan', style: theme.textTheme.labelLarge),
                ],
              ),
            ),
            Tab(
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.edit, size: 18),
                  const SizedBox(width: 6),
                  Text('Manual', style: theme.textTheme.labelLarge),
                ],
              ),
            ),
            Tab(
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.history, size: 18),
                  const SizedBox(width: 6),
                  Text('History', style: theme.textTheme.labelLarge),
                ],
              ),
            ),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildScannerView(theme),
          _buildManualView(theme),
          _buildHistoryView(theme),
        ],
      ),
    );
  }

  Widget _buildScannerView(ThemeData theme) {
    return Stack(
      children: [
        MobileScanner(
          controller: _cameraController,
          onDetect: _onDetect,
        ),
        Container(
          decoration: BoxDecoration(
            border: Border.all(color: AppTheme.tealAccent, width: 2),
            borderRadius: BorderRadius.circular(12),
          ),
          margin: const EdgeInsets.all(60),
          child: Center(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(
                  Icons.qr_code_scanner,
                  size: 80,
                  color: Colors.white.withOpacity(0.3),
                ),
                const SizedBox(height: 12),
                Text(
                  'Align barcode within frame',
                  style: TextStyle(
                    color: Colors.white.withOpacity(0.7),
                    fontSize: 14,
                  ),
                ),
              ],
            ),
          ),
        ),
        if (_lastResult != null)
          Positioned(
            bottom: 16,
            left: 16,
            right: 16,
            child: Card(
              color: Colors.black87,
              child: ListTile(
                leading: const Icon(Icons.check_circle,
                    color: AppTheme.successGreen),
                title: Text(
                  _lastResult!.barcode,
                  style: const TextStyle(color: Colors.white),
                ),
                subtitle: Text(
                  _lastResult!.format,
                  style: TextStyle(color: Colors.white.withOpacity(0.7)),
                ),
              ),
            ),
          ),
      ],
    );
  }

  Widget _buildManualView(ThemeData theme) {
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.edit,
            size: 64,
            color: theme.colorScheme.onSurface.withOpacity(0.3),
          ),
          const SizedBox(height: 24),
          Text(
            'Enter barcode manually',
            style: theme.textTheme.titleLarge,
          ),
          const SizedBox(height: 24),
          TextField(
            controller: _manualController,
            decoration: InputDecoration(
              hintText: 'Enter barcode number...',
              prefixIcon: const Icon(Icons.qr_code),
              suffixIcon: IconButton(
                icon: const Icon(Icons.clear),
                onPressed: () => _manualController.clear(),
              ),
            ),
            keyboardType: TextInputType.text,
            textInputAction: TextInputAction.done,
            onSubmitted: (_) => _manualSubmit(),
          ),
          const SizedBox(height: 16),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              onPressed: _manualSubmit,
              icon: const Icon(Icons.search),
              label: const Text('Look Up'),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHistoryView(ThemeData theme) {
    if (_scanHistory.isEmpty) {
      return const EmptyStateWidget(
        message: 'No scan history',
        icon: Icons.history,
      );
    }

    return RefreshIndicator(
      onRefresh: _loadHistory,
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: _scanHistory.length,
        itemBuilder: (context, index) {
          final scan = _scanHistory[index];
          return Card(
            margin: const EdgeInsets.only(bottom: 8),
            child: ListTile(
              leading: Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: AppTheme.tealAccent.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Icon(Icons.qr_code, color: AppTheme.tealAccent),
              ),
              title: Text(
                scan.productName ?? scan.barcode,
                style: theme.textTheme.titleMedium,
              ),
              subtitle: Text(
                '${scan.format} - ${scan.scannedAt.hour}:${scan.scannedAt.minute.toString().padLeft(2, '0')}',
                style: theme.textTheme.bodyMedium,
              ),
              trailing: const Icon(Icons.chevron_right),
              onTap: () => _showResultDialog(scan),
            ),
          );
        },
      ),
    );
  }
}

class EmptyStateWidget extends StatelessWidget {
  final String message;
  final IconData icon;

  const EmptyStateWidget({
    super.key,
    required this.message,
    this.icon = Icons.inbox_outlined,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 64,
              color: theme.colorScheme.onSurface.withOpacity(0.3)),
          const SizedBox(height: 16),
          Text(message,
              style: theme.textTheme.bodyLarge?.copyWith(
                  color: theme.colorScheme.onSurface.withOpacity(0.5))),
        ],
      ),
    );
  }
}
