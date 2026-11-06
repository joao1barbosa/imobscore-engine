import { useEffect, useRef, useState } from "react";
import { Bar, BarChart, Tooltip, XAxis, YAxis } from "recharts";

import type { ParticipantRow } from "@/api/queries";
import { Card } from "@/components/ui/card";
import { copy } from "@/lib/copy";
import { MethodLegend } from "./method-legend";

type ParticipantBarsProps = {
  rows: ParticipantRow[];
};

type Method = "bayes" | "mle" | "persona" | "equal";

type ParticipantPoint = {
  participant_code: string;
  [key: string]: number | string;
};

const METHODS: { method: Method; color: string }[] = [
  { method: "bayes", color: "var(--chart-1)" },
  { method: "mle", color: "var(--chart-2)" },
  { method: "persona", color: "var(--chart-3)" },
  { method: "equal", color: "var(--chart-4)" },
];

const X_TICKS = [0, 0.25, 0.5, 0.75, 1];
const ROW_HEIGHT = 46;
const CHART_TOP = 4;
const CHART_BOTTOM = 22;

const percentFormatter = new Intl.NumberFormat("pt-BR", {
  style: "percent",
  maximumFractionDigits: 0,
});

/**
 * As barras da acurácia de cada participante, com as quatro barras dos métodos
 * agrupadas na linha da pessoa.
 */
export function ParticipantBars({ rows }: ParticipantBarsProps) {
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

  const participantCodes = [
    ...new Set(rows.map((row) => row.participant_code)),
  ];
  const chartHeight =
    CHART_TOP +
    ROW_HEIGHT * Math.max(participantCodes.length, 1) +
    CHART_BOTTOM;
  const byParticipantAndMethod = new Map(
    rows.map((row) => [`${row.participant_code}-${row.method}`, row]),
  );

  const data: ParticipantPoint[] = participantCodes.map((code) => {
    const point: ParticipantPoint = { participant_code: code };

    for (const { method } of METHODS) {
      const row = byParticipantAndMethod.get(`${code}-${method}`);
      point[method] = row?.acc_mean ?? 0;
    }

    return point;
  });

  const chartA11y = {
    role: "img",
    "aria-label": copy.experiment.participants.chartLabel,
  } as const;

  return (
    <Card className="gap-3 rounded-xl border bg-card p-4 text-card-foreground shadow-sm ring-0 md:p-6">
      <div>
        <h2 className="text-lg font-semibold">
          {copy.experiment.participants.title}
        </h2>
        <p className="text-sm text-muted-foreground">
          {copy.experiment.participants.lead}
        </p>
      </div>

      <MethodLegend />

      <div ref={containerRef} className="w-full min-w-0">
        <BarChart
          {...chartA11y}
          width={chartWidth}
          height={chartHeight}
          data={data}
          layout="vertical"
          margin={{ top: CHART_TOP, right: 14, bottom: CHART_BOTTOM, left: 0 }}
          barGap={2}
        >
          <XAxis
            type="number"
            domain={[0, 1]}
            ticks={X_TICKS}
            tickFormatter={(value: number) => percentFormatter.format(value)}
            tick={{ fontSize: 12, fill: "var(--muted-foreground)" }}
            tickLine={false}
            axisLine={false}
          />
          <YAxis
            type="category"
            dataKey="participant_code"
            width={42}
            interval={0}
            tick={{ fontSize: 13, fill: "var(--foreground)" }}
            tickLine={false}
            axisLine={false}
          />
          <Tooltip
            cursor={{ fill: "var(--muted)" }}
            content={({ active, payload }) => {
              const point = payload?.[0]?.payload as
                ParticipantPoint | undefined;

              if (!active || !point) {
                return null;
              }

              return (
                <div className="rounded-lg border bg-card p-2 text-xs text-card-foreground shadow-md">
                  <p className="font-medium">{point.participant_code}</p>
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
            <Bar
              key={method}
              dataKey={method}
              name={copy.experiment.methods[method]}
              fill={color}
              barSize={7}
              radius={[3, 3, 3, 3]}
              isAnimationActive={false}
            />
          ))}
        </BarChart>
      </div>
    </Card>
  );
}
