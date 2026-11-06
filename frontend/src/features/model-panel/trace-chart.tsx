import { useEffect, useRef, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  CartesianGrid,
  Line,
  LineChart,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { traceQuery, type FeatureOut } from "@/api/queries";
import { Card } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { copy } from "@/lib/copy";

type TraceChartProps = {
  sessionId: string;
  n: number;
  features: FeatureOut[];
};

const DEFAULT_FEATURE = "dist_center";
const CHAIN_COUNT = 4;

const decimalFormatter = new Intl.NumberFormat("pt-BR", {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

/**
 * O traço das quatro primeiras cadeias do peso escolhido: cada linha mostra
 * uma cadeia percorrendo os valores possíveis daquele peso.
 */
export function TraceChart({ sessionId, n, features }: TraceChartProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [width, setWidth] = useState(0);
  const [feature, setFeature] = useState(DEFAULT_FEATURE);

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

  const traceState = useQuery(traceQuery(sessionId, n, feature));
  const chains = (traceState.data?.chains ?? []).slice(0, CHAIN_COUNT);
  const pointCount = chains.reduce(
    (longest, chain) => Math.max(longest, chain.length),
    0,
  );
  const chartData = Array.from({ length: pointCount }, (_, index) => {
    const point: Record<string, number> = { index };

    chains.forEach((chain, chainIndex) => {
      const value = chain[index];

      if (typeof value === "number") {
        point[`chain${chainIndex}`] = value;
      }
    });

    return point;
  });

  const values = chains.flat();
  const min = values.length > 0 ? Math.min(...values) : 0;
  const max = values.length > 0 ? Math.max(...values) : 1;
  // O eixo do zero tem marcas de distância igual: o passo é 1 quando o
  // intervalo é curto e 2 quando é longo.
  const step = Math.ceil(max) - Math.floor(min) <= 6 ? 1 : 2;
  const low = Math.floor(min / step) * step;
  const high = Math.ceil(max / step) * step;
  const ticks: number[] = [];

  for (let value = low; value <= high; value += step) {
    ticks.push(value);
  }

  const chartWidth = width || 640;
  const selectedLabel =
    features.find((item) => item.key === feature)?.label ?? "";

  const chartA11y = {
    role: "img",
    "aria-label": copy.modelPanel.trace.chartLabel,
  } as const;

  return (
    <Card className="gap-3 rounded-xl border bg-card p-4 text-card-foreground shadow-sm ring-0 md:p-6">
      <div>
        <h2 className="text-lg font-semibold">{copy.modelPanel.trace.title}</h2>
        <p className="text-sm text-muted-foreground">
          {copy.modelPanel.trace.lead}
        </p>
      </div>

      <div className="flex flex-col gap-1.5 md:w-72">
        <label htmlFor="trace-feature" className="text-sm font-medium">
          {copy.modelPanel.trace.select}
        </label>
        <Select
          value={feature}
          onValueChange={(value) => {
            if (typeof value === "string") {
              setFeature(value);
            }
          }}
        >
          <SelectTrigger id="trace-feature" className="h-11 w-full bg-card">
            <SelectValue>{selectedLabel}</SelectValue>
          </SelectTrigger>
          <SelectContent>
            {features.map((item) => (
              <SelectItem key={item.key} value={item.key}>
                {item.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="flex flex-wrap gap-4">
        {Array.from({ length: CHAIN_COUNT }, (_, index) => (
          <span
            key={index}
            className="inline-flex items-center gap-1.5 text-sm text-muted-foreground"
          >
            <span
              className="h-0.5 w-4"
              style={{ backgroundColor: `var(--chart-${index + 1})` }}
            />
            {copy.modelPanel.trace.chain(index + 1)}
          </span>
        ))}
      </div>

      <div ref={containerRef} className="relative w-full min-w-0">
        <LineChart
          {...chartA11y}
          width={chartWidth}
          height={200}
          data={chartData}
          margin={{ top: 6, right: 8, bottom: 22, left: 0 }}
        >
          <CartesianGrid vertical={false} stroke="var(--border)" />
          <XAxis
            dataKey="index"
            type="number"
            domain={["dataMin", "dataMax"]}
            hide
          />
          <YAxis
            width={30}
            domain={[low, high]}
            ticks={ticks}
            tickFormatter={(value: number) =>
              value < 0 ? `−${Math.abs(value)}` : String(value)
            }
            tick={{ fontSize: 12, fill: "var(--muted-foreground)" }}
            axisLine={{ stroke: "var(--border)" }}
            tickLine={false}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "var(--card)",
              borderColor: "var(--border)",
              color: "var(--foreground)",
            }}
            labelStyle={{ color: "var(--muted-foreground)" }}
            itemStyle={{ color: "var(--foreground)" }}
            formatter={(value) => decimalFormatter.format(Number(value))}
          />
          {chains.map((_, index) => (
            <Line
              key={index}
              type="linear"
              dataKey={`chain${index}`}
              name={copy.modelPanel.trace.chain(index + 1)}
              stroke={`var(--chart-${index + 1})`}
              strokeWidth={1.25}
              dot={false}
              isAnimationActive={false}
            />
          ))}
        </LineChart>
        <span className="pointer-events-none absolute right-2 bottom-1 text-xs text-muted-foreground">
          {copy.modelPanel.trace.points}
        </span>
      </div>
    </Card>
  );
}
