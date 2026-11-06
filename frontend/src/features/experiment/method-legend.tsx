import type { ExperimentRow } from "@/api/queries";
import { copy } from "@/lib/copy";

const METHODS: {
  method: ExperimentRow["method"];
  color: string;
}[] = [
  { method: "bayes", color: "var(--chart-1)" },
  { method: "mle", color: "var(--chart-2)" },
  { method: "persona", color: "var(--chart-3)" },
  { method: "equal", color: "var(--chart-4)" },
];

/** A legenda das cores dos métodos, usada na curva e nas barras. */
export function MethodLegend() {
  return (
    <div className="flex flex-wrap gap-x-4 gap-y-1">
      {METHODS.map(({ method, color }) => (
        <span
          key={method}
          className="inline-flex items-center gap-1.5 text-sm text-muted-foreground"
        >
          <span
            className="size-2.5 rounded-full"
            style={{ backgroundColor: color }}
            aria-hidden="true"
          />
          {copy.experiment.methods[method]}
        </span>
      ))}
    </div>
  );
}
