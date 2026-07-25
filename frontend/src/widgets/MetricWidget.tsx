interface MetricWidgetProps {
  title: string;
  value: string | number;
  change?: number;
  icon?: React.ReactNode;
}

export function MetricWidget({ title, value, change, icon }: MetricWidgetProps) {
  return (
    <div className="bg-white p-4 rounded-lg shadow">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-500">{title}</p>
          <p className="text-2xl font-bold">{value}</p>
          {change !== undefined && (
            <p className={`text-xs ${change >= 0 ? "text-green-600" : "text-red-600"}`}>
              {change >= 0 ? "+" : ""}{change}%
            </p>
          )}
        </div>
        {icon && <div className="text-gray-400">{icon}</div>}
      </div>
    </div>
  );
}
