import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import '../config/theme.dart';

class SalesChart extends StatelessWidget {
  final List<double> salesData;
  final List<String> labels;
  final String title;

  const SalesChart({
    super.key,
    required this.salesData,
    required this.labels,
    this.title = 'Sales Overview',
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    if (salesData.isEmpty) {
      return Card(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Center(
            child: Text(
              'No sales data available',
              style: theme.textTheme.bodyLarge,
            ),
          ),
        ),
      );
    }

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: theme.textTheme.titleLarge,
            ),
            const SizedBox(height: 24),
            SizedBox(
              height: 200,
              child: BarChart(
                BarChartData(
                  alignment: BarChartAlignment.spaceAround,
                  maxY: salesData
                          .reduce((a, b) => a > b ? a : b)
                          .clamp(1, double.infinity) *
                      1.2,
                  barTouchData: BarTouchData(
                    touchTooltipData: BarTouchTooltipData(
                      tooltipRoundedRadius: 8,
                      getTooltipItem: (group, groupIndex, rod, rodIndex) {
                        return BarTooltipItem(
                          '${labels[groupIndex]}\n',
                          TextStyle(
                            color: theme.colorScheme.onSurface,
                            fontWeight: FontWeight.bold,
                            fontSize: 14,
                          ),
                          children: [
                            TextSpan(
                              text:
                                  '\$${salesData[groupIndex].toStringAsFixed(2)}',
                              style: TextStyle(
                                color: theme.colorScheme.secondary,
                                fontSize: 12,
                              ),
                            ),
                          ],
                        );
                      },
                    ),
                  ),
                  titlesData: FlTitlesData(
                    show: true,
                    bottomTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        getTitlesWidget: (value, meta) {
                          final index = value.toInt();
                          if (index >= 0 && index < labels.length) {
                            return Padding(
                              padding: const EdgeInsets.only(top: 8),
                              child: Text(
                                labels[index],
                                style: const TextStyle(fontSize: 10),
                              ),
                            );
                          }
                          return const SizedBox.shrink();
                        },
                        reservedSize: 28,
                      ),
                    ),
                    leftTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        reservedSize: 40,
                        getTitlesWidget: (value, meta) {
                          return Text(
                            '\$${value.toInt()}',
                            style: const TextStyle(fontSize: 10),
                          );
                        },
                      ),
                    ),
                    topTitles: const AxisTitles(
                      sideTitles: SideTitles(showTitles: false),
                    ),
                    rightTitles: const AxisTitles(
                      sideTitles: SideTitles(showTitles: false),
                    ),
                  ),
                  gridData: FlGridData(
                    show: true,
                    drawVerticalLine: false,
                    horizontalInterval: null,
                    getDrawingHorizontalLine: (value) {
                      return FlLine(
                        color: theme.colorScheme.onSurface.withOpacity(0.1),
                        strokeWidth: 1,
                      );
                    },
                  ),
                  barGroups: salesData.asMap().entries.map((entry) {
                    return BarChartGroupData(
                      x: entry.key,
                      barRods: [
                        BarChartRodData(
                          toY: entry.value.clamp(0.1, double.infinity),
                          color: AppTheme.tealAccent,
                          width: 20,
                          borderRadius: const BorderRadius.only(
                            topLeft: Radius.circular(4),
                            topRight: Radius.circular(4),
                          ),
                        ),
                      ],
                    );
                  }).toList(),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class CashFlowChart extends StatelessWidget {
  final List<double> inflows;
  final List<double> outflows;
  final List<String> labels;

  const CashFlowChart({
    super.key,
    required this.inflows,
    required this.outflows,
    required this.labels,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Cash Flow',
              style: theme.textTheme.titleLarge,
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                _legendItem(AppTheme.successGreen, 'Inflow', context),
                const SizedBox(width: 16),
                _legendItem(AppTheme.errorRed, 'Outflow', context),
              ],
            ),
            const SizedBox(height: 16),
            SizedBox(
              height: 200,
              child: BarChart(
                BarChartData(
                  alignment: BarChartAlignment.spaceAround,
                  maxY: _maxValue * 1.2,
                  barTouchData: BarTouchData(
                    touchTooltipData: BarTouchTooltipData(
                      getTooltipItem: (group, groupIndex, rod, rodIndex) {
                        final isInflow = rodIndex == 0;
                        return BarTooltipItem(
                          '${labels[groupIndex]}\n',
                          TextStyle(
                            color: theme.colorScheme.onSurface,
                            fontWeight: FontWeight.bold,
                          ),
                          children: [
                            TextSpan(
                              text:
                                  '${isInflow ? 'In' : 'Out'}flow: \$${rod.toY.toStringAsFixed(2)}',
                              style: TextStyle(
                                color: isInflow
                                    ? AppTheme.successGreen
                                    : AppTheme.errorRed,
                              ),
                            ),
                          ],
                        );
                      },
                    ),
                  ),
                  titlesData: FlTitlesData(
                    bottomTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        getTitlesWidget: (value, meta) {
                          final index = value.toInt();
                          if (index >= 0 && index < labels.length) {
                            return Padding(
                              padding: const EdgeInsets.only(top: 8),
                              child: Text(
                                labels[index],
                                style: const TextStyle(fontSize: 10),
                              ),
                            );
                          }
                          return const SizedBox.shrink();
                        },
                      ),
                    ),
                    leftTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        reservedSize: 40,
                        getTitlesWidget: (value, meta) {
                          return Text(
                            '\$${value.toInt()}',
                            style: const TextStyle(fontSize: 10),
                          );
                        },
                      ),
                    ),
                    topTitles: const AxisTitles(
                      sideTitles: SideTitles(showTitles: false),
                    ),
                    rightTitles: const AxisTitles(
                      sideTitles: SideTitles(showTitles: false),
                    ),
                  ),
                  gridData: FlGridData(
                    show: true,
                    drawVerticalLine: false,
                    getDrawingHorizontalLine: (value) {
                      return FlLine(
                        color: theme.colorScheme.onSurface.withOpacity(0.1),
                        strokeWidth: 1,
                      );
                    },
                  ),
                  barGroups: List.generate(inflows.length, (index) {
                    return BarChartGroupData(
                      x: index,
                      barRods: [
                        BarChartRodData(
                          toY: inflows[index].clamp(0.1, double.infinity),
                          color: AppTheme.successGreen,
                          width: 10,
                          borderRadius: const BorderRadius.only(
                            topLeft: Radius.circular(4),
                            topRight: Radius.circular(4),
                          ),
                        ),
                        BarChartRodData(
                          toY: outflows[index].clamp(0.1, double.infinity),
                          color: AppTheme.errorRed,
                          width: 10,
                          borderRadius: const BorderRadius.only(
                            topLeft: Radius.circular(4),
                            topRight: Radius.circular(4),
                          ),
                        ),
                      ],
                    );
                  }),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  double get _maxValue {
    final all = [...inflows, ...outflows];
    if (all.isEmpty) return 1;
    return all.reduce((a, b) => a > b ? a : b);
  }

  Widget _legendItem(Color color, String label, BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 12,
          height: 12,
          decoration: BoxDecoration(
            color: color,
            borderRadius: BorderRadius.circular(2),
          ),
        ),
        const SizedBox(width: 4),
        Text(
          label,
          style: Theme.of(context).textTheme.bodyMedium,
        ),
      ],
    );
  }
}

class PipelineChart extends StatelessWidget {
  final List<String> stageNames;
  final List<double> stageValues;
  final List<Color> stageColors;

  const PipelineChart({
    super.key,
    required this.stageNames,
    required this.stageValues,
    this.stageColors = const [
      AppTheme.infoBlue,
      AppTheme.warningAmber,
      AppTheme.tealAccent,
      AppTheme.successGreen,
    ],
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    if (stageValues.isEmpty) {
      return Card(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Center(
            child: Text(
              'No pipeline data',
              style: theme.textTheme.bodyLarge,
            ),
          ),
        ),
      );
    }

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Pipeline',
              style: theme.textTheme.titleLarge,
            ),
            const SizedBox(height: 16),
            SizedBox(
              height: 220,
              child: PieChart(
                PieChartData(
                  sectionsSpace: 2,
                  centerSpaceRadius: 40,
                  sections: List.generate(stageValues.length, (index) {
                    final total = stageValues.fold<double>(
                        0.0, (sum, v) => sum + v);
                    final percentage = total > 0
                        ? (stageValues[index] / total * 100)
                        : 0.0;
                    return PieChartSectionData(
                      color: stageColors[index % stageColors.length],
                      value: stageValues[index].clamp(0.1, double.infinity),
                      title: '${percentage.toStringAsFixed(0)}%',
                      radius: 60,
                      titleStyle: const TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    );
                  }),
                ),
              ),
            ),
            const SizedBox(height: 12),
            ...List.generate(stageNames.length, (index) {
              return Padding(
                padding: const EdgeInsets.symmetric(vertical: 2),
                child: Row(
                  children: [
                    Container(
                      width: 12,
                      height: 12,
                      decoration: BoxDecoration(
                        color: stageColors[index % stageColors.length],
                        borderRadius: BorderRadius.circular(2),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Text(
                      stageNames[index],
                      style: theme.textTheme.bodyMedium,
                    ),
                    const Spacer(),
                    Text(
                      '\$${stageValues[index].toStringAsFixed(0)}',
                      style: theme.textTheme.bodyMedium?.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
              );
            }),
          ],
        ),
      ),
    );
  }
}
