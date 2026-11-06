import { useEffect, useRef, useState } from "react";
import {
  Area,
  CartesianGrid,
  ComposedChart,
  Line,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { ExperimentRow } from "@/api/queries";
import { Card } from "@/components/ui/card";
import { copy } from "@/lib/copy";
import { MethodLegend } from "./method-legend";

type AccuracyChartProps = {
  rows: ExperimentRow[];
};

type Method = ExperimentRow["method"];

type CurvePoint = {
  n_train: number;
  [key: string]: number | [number, number];
};

const METHODS: { method: Method; color: string }[] = [
  { method: "bayes", color: "var(--chart-1)" },
  { method: "mle", color: "var(--chart-2)" },
  { method: "persona", color: "var(--chart-3)" },
  { method: "equal", color: "var(--chart-4)" },
];

const Y_DOMAIN: [number, number] = [0.4, 0.9];
const Y_TICKS = [0.4, 0.5, 0.6, 0.7, 0.8, 0.9];

const percentFormatter = new Intl.NumberFormat("pt-BR", {
  style: "percent",
  maximumFractionDigits: 0,
});

function rangeKey(method: Method): string {
  return `${method}Range`;
}

/**
 * A curva de acurácia por número de pares de treino: uma linha por método e a
 * faixa de ±1 desvio de cada um.
 */
export function AccuracyChart({ rows }: AccuracyChartProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [width, setWidth] = useState(0);

  useEffect(() => {
    const element = containerRef.current;

    if (!element || typeof ResizeObserver === "undefined") {
      return;
    }

    const observer = new ResizeObserver((entries) => {
      const entry = entries[0];

      if (entry) {
        setWidth(entry.contentRect.width);
      }
    });

    observer.observe(element);

    return () => observer.disconnect();
  }, []);

  const chartWidth = width || 640;
  const chartHeight = chartWidth < 500 ? 240 : 320;

  const nValues = [...new Set(rows.map((row) => row.n_train))].sort(
    (a, b) => a - b,
  );
  const byMethodAndPairs = new Map(
    rows.map((row) => [`${row.method}-${row.n_train}`, row]),
  );

  const data: CurvePoint[] = nValues.map((nTrain) => {
    const point: CurvePoint = { n_train: nTrain };

    for (const { method } of METHODS) {
      const row = byMethodAndPairs.get(`${method}-${nTrain}`);
      const value = row?.acc_mean ?? 0;

      point[method] = value;
      point[rangeKey(method)] = row
        ? [row.acc_mean - row.acc_sd, row.acc_mean + row.acc_sd]
        : [value, value];
    }

    return point;
  });

  const chartA11y = {
    role: "img",
    "aria-label": copy.experiment.curve.chartLabel,
  } as const;

  return (
    <Card className="gap-3 rounded-xl border bg-card p-4 text-card-foreground shadow-sm ring-0 md:p-6">
      <div>
        <h2 className="text-lg font-semibold">{copy.experiment.curve.title}</h2>
        <p className="text-sm text-muted-foreground">
          {copy.experiment.curve.lead}
        </p>
      </div>

      <MethodLegend />

      <div ref={containerRef} className="w-full min-w-0">
        <ComposedChart
          {...chartA11y}
          width={chartWidth}
          height={chartHeight}
          data={data}
          margin={{ top: 8, right: 14, bottom: 32, left: 0 }}
        >
          <CartesianGrid
            vertical={false}
            stroke="var(--border)"
            strokeDasharray="0"
          />
          <XAxis
            type="number"
            dataKey="n_train"
            domain={[nValues[0] ?? 3, nValues[nValues.length - 1] ?? 10]}
            ticks={nValues}
            tick={{ fontSize: 12, fill: "var(--muted-foreground)" }}
            tickLine={false}
            axisLine={{ stroke: "var(--border)" }}
            label={{
              value: copy.experiment.curve.xAxis,
              position: "insideBottom",
              offset: -24,
              fill: "var(--muted-foreground)",
              fontSize: 12,
            }}
          />
          <YAxis
            type="number"
            domain={Y_DOMAIN}
            allowDataOverflow
            ticks={Y_TICKS}
            width={42}
            tickFormatter={(value: number) => percentFormatter.format(value)}
            tick={{ fontSize: 12, fill: "var(--muted-foreground)" }}
            tickLine={false}
            axisLine={false}
          />
          <Tooltip
            cursor={{
              stroke: "var(--muted-foreground)",
              strokeDasharray: "3 3",
            }}
            content={({ active, payload }) => {
              const point = payload?.[0]?.payload as CurvePoint | undefined;

              if (!active || !point) {
                return null;
              }

              return (
                <div className="rounded-lg border bg-card p-2 text-xs text-card-foreground shadow-md">
                  <p className="font-medium">
                    {copy.experiment.table.pairs(point.n_train)}
                  </p>
                  {METHODS.map(({ method }) => (
                    <p key={method} className="text-muted-foreground">
                      {copy.experiment.methods[method]}:{" "}
                      <span className="text-card-foreground tabular-nums">
                        {percentFormatter.format(Number(point[method]))}
                      </span>
                    </p>
                  ))}
                </div>
              );
            }}
          />

          {METHODS.map(({ method, color }) => (
            <Area
              key={rangeKey(method)}
              type="linear"
              dataKey={rangeKey(method)}
              stroke="none"
              fill={color}
              fillOpacity={0.1}
              isAnimationActive={false}
            />
          ))}

          {METHODS.map(({ method, color }) => (
            <Line
              key={method}
              type="linear"
              dataKey={method}
              name={copy.experiment.methods[method]}
              stroke={color}
              strokeWidth={2}
              dot={{
                r: 4,
                strokeWidth: 2,
                stroke: "var(--card)",
                fill: color,
              }}
              isAnimationActive={false}
            />
          ))}
        </ComposedChart>
      </div>
    </Card>
  );
}
