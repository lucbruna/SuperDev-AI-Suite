"use client";

import { useState, useMemo, useRef, type MouseEvent } from "react";
import { cn } from "@/utils/cn";

interface DataPoint {
  label: string;
  value: number;
}

interface LineChartProps {
  data: DataPoint[];
  width?: number;
  height?: number;
  color?: string;
  showGrid?: boolean;
  showLabels?: boolean;
  className?: string;
}

interface TooltipData {
  x: number;
  y: number;
  label: string;
  value: number;
}

export function LineChart({
  data,
  width = 600,
  height = 300,
  color = "#3b82f6",
  showGrid = true,
  showLabels = true,
  className,
}: LineChartProps) {
  const [tooltip, setTooltip] = useState<TooltipData | null>(null);
  const svgRef = useRef<SVGSVGElement>(null);

  const padding = { top: 20, right: 20, bottom: showLabels ? 40 : 20, left: showLabels ? 50 : 20 };
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;

  const { minValue, maxValue, points, pathD, gridLinesX, gridLinesY } = useMemo(() => {
    if (data.length === 0) {
      return { minValue: 0, maxValue: 100, points: [], pathD: "", gridLinesX: [], gridLinesY: [] };
    }

    const values = data.map((d) => d.value);
    const minVal = Math.min(...values);
    const maxVal = Math.max(...values);
    const range = maxVal - minVal || 1;
    const padding_ratio = range * 0.1;
    const minValue = Math.max(0, minVal - padding_ratio);
    const maxValue = maxVal + padding_ratio;
    const valueRange = maxValue - minValue;

    const pts = data.map((d, i) => ({
      x: padding.left + (i / Math.max(data.length - 1, 1)) * chartWidth,
      y: padding.top + chartHeight - ((d.value - minValue) / valueRange) * chartHeight,
      ...d,
    }));

    const d = pts
      .map((p, i) => `${i === 0 ? "M" : "L"} ${p.x} ${p.y}`)
      .join(" ");

    const gridY = 5;
    const gY = Array.from({ length: gridY + 1 }, (_, i) => {
      const val = minValue + (valueRange * i) / gridY;
      const y = padding.top + chartHeight - (i / gridY) * chartHeight;
      return { y, label: val.toFixed(0) };
    });

    const gridX = data.length > 10 ? Math.ceil(data.length / 5) : 1;
    const gX = data
      .filter((_, i) => i % gridX === 0)
      .map((d, i) => ({
        x: padding.left + (i * gridX / Math.max(data.length - 1, 1)) * chartWidth,
        label: d.label,
      }));

    return { minValue, maxValue, points: pts, pathD: d, gridLinesX: gX, gridLinesY: gY };
  }, [data, chartWidth, chartHeight, padding]);

  const handleMouseMove = (e: MouseEvent<SVGSVGElement>) => {
    if (points.length === 0) return;
    const svgRect = svgRef.current?.getBoundingClientRect();
    if (!svgRect) return;

    const mouseX = e.clientX - svgRect.left;
    const closest = points.reduce((prev, curr) =>
      Math.abs(curr.x - mouseX) < Math.abs(prev.x - mouseX) ? curr : prev,
    );

    setTooltip({
      x: closest.x,
      y: closest.y,
      label: closest.label,
      value: closest.value,
    });
  };

  const handleMouseLeave = () => setTooltip(null);

  if (data.length === 0) {
    return (
      <div
        className={cn("flex items-center justify-center text-sm text-surface-400", className)}
        style={{ width, height }}
      >
        No data available
      </div>
    );
  }

  return (
    <div className={cn("relative", className)} style={{ width, height }}>
      <svg
        ref={svgRef}
        width={width}
        height={height}
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
        className="overflow-visible"
      >
        {showGrid &&
          gridLinesY.map((gl, i) => (
            <g key={`gy-${i}`}>
              <line
                x1={padding.left}
                y1={gl.y}
                x2={width - padding.right}
                y2={gl.y}
                className="stroke-surface-200 dark:stroke-surface-700"
                strokeWidth="1"
              />
              {showLabels && (
                <text
                  x={padding.left - 8}
                  y={gl.y + 4}
                  textAnchor="end"
                  className="fill-surface-400 text-[11px]"
                >
                  {gl.label}
                </text>
              )}
            </g>
          ))}

        {showGrid &&
          gridLinesX.map((gl, i) => (
            <line
              key={`gx-${i}`}
              x1={gl.x}
              y1={padding.top}
              x2={gl.x}
              y2={height - padding.bottom}
              className="stroke-surface-200 dark:stroke-surface-700"
              strokeWidth="1"
            />
          ))}

        {showLabels &&
          gridLinesX.map((gl, i) => (
            <text
              key={`lx-${i}`}
              x={gl.x}
              y={height - 8}
              textAnchor="middle"
              className="fill-surface-400 text-[11px]"
            >
              {gl.label.length > 6 ? gl.label.slice(0, 5) + "…" : gl.label}
            </text>
          ))}

        <path d={pathD} fill="none" stroke={color} strokeWidth="2" strokeLinejoin="round" />

        <path
          d={`${pathD} L ${points[points.length - 1]?.x ?? 0} ${padding.top + chartHeight} L ${points[0]?.x ?? 0} ${padding.top + chartHeight} Z`}
          fill={color}
          fillOpacity="0.08"
        />

        {points.map((p, i) => (
          <circle
            key={i}
            cx={p.x}
            cy={p.y}
            r="4"
            fill="white"
            stroke={color}
            strokeWidth="2"
            className="cursor-pointer"
          />
        ))}

        {tooltip && (
          <>
            <line
              x1={tooltip.x}
              y1={padding.top}
              x2={tooltip.x}
              y2={height - padding.bottom}
              className="stroke-surface-400"
              strokeWidth="1"
              strokeDasharray="4 2"
            />
            <rect
              x={tooltip.x - 45}
              y={Math.max(padding.top - 5, tooltip.y - 40)}
              width="90"
              height="32"
              rx="4"
              className="fill-surface-800 dark:fill-surface-100"
            />
            <text
              x={tooltip.x}
              y={Math.max(padding.top + 5, tooltip.y - 22)}
              textAnchor="middle"
              className="fill-white text-[10px] dark:fill-surface-900"
            >
              {tooltip.label}
            </text>
            <text
              x={tooltip.x}
              y={Math.max(padding.top + 17, tooltip.y - 10)}
              textAnchor="middle"
              className="fill-white text-[11px] font-semibold dark:fill-surface-900"
            >
              {tooltip.value}
            </text>
          </>
        )}
      </svg>
    </div>
  );
}
