import { useEffect, useRef, useState } from "react";
import {
  CartesianGrid,
  ComposedChart,
  ErrorBar,
  ReferenceLine,
  Scatter,
  Tooltip,
  XAxis,
  YAxis,
  type ScatterShapeProps,
} from "recharts";

import type { WeightOut } from "@/api/queries";
import { Card } from "@/components/ui/card";
import { copy } from "@/lib/copy";
import { WeightsTable } from "./weights-table";

type WeightsChartProps = {
  weights: WeightOut[];
  priorOnly: boolean;
};

type WeightPoint = {
  row: number;
  label: string;
  series: "posterior" | "prior";
  mean: number;
  lo: number;
  hi: number;
  rawMean: number;
  rawLo: number;
  rawHi: number;
};

const AXIS_MIN = -3;
const AXIS_MAX = 3;
const AXIS_TICKS = [-3, -2, -1, 0, 1, 2, 3];
const ROW_GAP = 0.18;
const PRIOR_Z = 1.645;

const decimalFormatter = new Intl.NumberFormat("pt-BR", {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

function clamp(value: number): number {
  return Math.max(AXIS_MIN, Math.min(AXIS_MAX, value));
}

function toPoint(
  weight: WeightOut,
  index: number,
  series: WeightPoint["series"],
  mean: number,
  lo: number,
  hi: number,
): WeightPoint {
  return {
    row: series === "posterior" ? index - ROW_GAP : index + ROW_GAP,
    label: weight.label,
    series,
    mean: clamp(mean),
    lo: clamp(lo),
    hi: clamp(hi),
    rawMean: mean,
    rawLo: lo,
    rawHi: hi,
  };
}

function seriesName(series: WeightPoint["series"]): string {
  return series === "posterior"
    ? copy.modelPanel.weights.posterior
    : copy.modelPanel.weights.prior;
}

/**
 * O gráfico de intervalos dos pesos. A posteriori fica acima da linha da
 * característica e a priori abaixo, cada uma com a média e a faixa de 5% a
 * 95%. Valores fora do eixo ficam no limite.
 */
export function WeightsChart({ weights, priorOnly }: WeightsChartProps) {
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
  const yAxisWidth = chartWidth < 500 ? 134 : 170;
  const labels = weights.map((weight) => weight.label);

  const posteriorPoints = weights.map((weight, index) =>
    toPoint(
      weight,
      index,
      "posterior",
      weight.post_mean,
      weight.ci_low,
      weight.ci_high,
    ),
  );
  const priorPoints = weights.map((weight, index) => {
    const priorLo = weight.prior_mean - PRIOR_Z * weight.prior_sd;
    const priorHi = weight.prior_mean + PRIOR_Z * weight.prior_sd;

    return toPoint(weight, index, "prior", weight.prior_mean, priorLo, priorHi);
  });

  const chartA11y = {
    role: "img",
    "aria-label": copy.modelPanel.weights.chartLabel,
  } as const;

  return (
    <Card className="gap-3 rounded-xl border bg-card p-4 text-card-foreground shadow-sm ring-0 md:p-6">
      <div>
        <h2 className="text-lg font-semibold">
          {copy.modelPanel.weights.title}
        </h2>
        <p className="text-sm text-muted-foreground">
          {priorOnly
            ? copy.modelPanel.weights.priorOnlyLead
            : copy.modelPanel.weights.lead}
        </p>
      </div>

      <div className="flex flex-wrap gap-4">
        {priorOnly ? null : (
          <span className="inline-flex items-center gap-1.5 text-sm text-muted-foreground">
            <span
              className="size-2.5 rounded-full"
              style={{ backgroundColor: "var(--chart-1)" }}
            />
            {copy.modelPanel.weights.posterior}
          </span>
        )}
        <span className="inline-flex items-center gap-1.5 text-sm text-muted-foreground">
          <span
            className="size-2.5 rounded-full"
            style={{ backgroundColor: "var(--chart-2)" }}
          />
          {copy.modelPanel.weights.prior}
        </span>
      </div>

      <div ref={containerRef} className="w-full min-w-0">
        <ComposedChart
          {...chartA11y}
          width={chartWidth}
          height={390}
          margin={{ top: 4, right: 12, bottom: 24, left: 0 }}
        >
          <CartesianGrid
            horizontal={false}
            stroke="var(--border)"
            strokeDasharray="0"
          />
          <XAxis
            type="number"
            dataKey="mean"
            domain={[AXIS_MIN, AXIS_MAX]}
            ticks={AXIS_TICKS}
            tickFormatter={(value: number) =>
              value < 0 ? `−${Math.abs(value)}` : String(value)
            }
            tick={{ fontSize: 12, fill: "var(--muted-foreground)" }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            type="number"
            dataKey="row"
            domain={[-0.5, Math.max(weights.length - 0.5, 0.5)]}
            ticks={weights.map((_, index) => index)}
            reversed
            width={yAxisWidth}
            tickFormatter={(value: number) => labels[value] ?? ""}
            tick={{
              fontSize: chartWidth < 500 ? 12 : 14,
              fill: "var(--muted-foreground)",
            }}
            axisLine={false}
            tickLine={false}
          />
          <ReferenceLine x={0} stroke="var(--muted-foreground)" />
          <Tooltip
            cursor={{
              stroke: "var(--muted-foreground)",
              strokeDasharray: "3 3",
            }}
            content={({ active, payload }) => {
              const point = payload?.[0]?.payload as WeightPoint | undefined;

              if (!active || !point) {
                return null;
              }

              return (
                <div className="rounded-lg border bg-card p-2 text-xs text-card-foreground shadow-md">
                  <p className="font-medium">{point.label}</p>
                  <p className="text-muted-foreground">
                    {seriesName(point.series)}
                  </p>
                  <p className="tabular-nums">
                    {decimalFormatter.format(point.rawMean)} (
                    {copy.modelPanel.weights.interval(
                      decimalFormatter.format(point.rawLo),
                      decimalFormatter.format(point.rawHi),
                    )}
                    )
                  </p>
                </div>
              );
            }}
          />
          {priorOnly ? null : (
            <Scatter
              name={copy.modelPanel.weights.posterior}
              data={posteriorPoints}
              dataKey="mean"
              isAnimationActive={false}
              shape={(props: ScatterShapeProps) =>
                props.cx == null || props.cy == null ? null : (
                  <circle
                    cx={props.cx}
                    cy={props.cy}
                    r={4}
                    fill="var(--chart-1)"
                    stroke="var(--card)"
                    strokeWidth={2}
                  />
                )
              }
            >
              <ErrorBar
                dataKey={(point: WeightPoint) => [
                  point.mean - point.lo,
                  point.hi - point.mean,
                ]}
                direction="x"
                width={0}
                stroke="var(--chart-1)"
                strokeWidth={2}
                isAnimationActive={false}
              />
            </Scatter>
          )}
          <Scatter
            name={copy.modelPanel.weights.prior}
            data={priorPoints}
            dataKey="mean"
            isAnimationActive={false}
            shape={(props: ScatterShapeProps) =>
              props.cx == null || props.cy == null ? null : (
                <circle
                  cx={props.cx}
                  cy={props.cy}
                  r={4}
                  fill="var(--chart-2)"
                  stroke="var(--card)"
                  strokeWidth={2}
                />
              )
            }
          >
            <ErrorBar
              dataKey={(point: WeightPoint) => [
                point.mean - point.lo,
                point.hi - point.mean,
              ]}
              direction="x"
              width={0}
              stroke="var(--chart-2)"
              strokeWidth={2}
              isAnimationActive={false}
            />
          </Scatter>
        </ComposedChart>
      </div>

      <WeightsTable weights={weights} />
    </Card>
  );
}
