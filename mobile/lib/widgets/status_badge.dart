import 'package:flutter/material.dart';
import '../config/theme.dart';

class StatusBadge extends StatelessWidget {
  final String status;
  final double fontSize;
  final EdgeInsets padding;

  const StatusBadge({
    super.key,
    required this.status,
    this.fontSize = 12,
    this.padding = const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
  });

  @override
  Widget build(BuildContext context) {
    final config = _getConfig();
    return Container(
      padding: padding,
      decoration: BoxDecoration(
        color: config.color.withOpacity(0.15),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: config.color.withOpacity(0.5),
          width: 1,
        ),
      ),
      child: Text(
        status.toUpperCase(),
        style: TextStyle(
          color: config.color,
          fontSize: fontSize,
          fontWeight: FontWeight.w600,
          letterSpacing: 0.5,
        ),
      ),
    );
  }

  _StatusConfig _getConfig() {
    switch (status.toLowerCase()) {
      case 'active':
      case 'completed':
      case 'paid':
      case 'confirmed':
      case 'won':
      case 'open':
      case 'in_stock':
        return _StatusConfig(AppTheme.successGreen);
      case 'pending':
      case 'draft':
      case 'new':
      case 'processing':
      case 'prospecting':
        return _StatusConfig(AppTheme.warningAmber);
      case 'overdue':
      case 'cancelled':
      case 'inactive':
      case 'lost':
      case 'out_of_stock':
      case 'low_stock':
        return _StatusConfig(AppTheme.errorRed);
      case 'negotiation':
      case 'proposal':
      case 'shipped':
      case 'partially_paid':
        return _StatusConfig(AppTheme.infoBlue);
      default:
        return _StatusConfig(Colors.grey);
    }
  }
}

class _StatusConfig {
  final Color color;
  _StatusConfig(this.color);
}
