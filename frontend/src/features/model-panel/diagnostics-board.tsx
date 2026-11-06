import { CircleCheck, TriangleAlert } from "lucide-react";

import type { Diagnostics } from "@/api/queries";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/cn";
import { copy } from "@/lib/copy";

type DiagnosticsBoardProps = {
  diagnostics: Diagnostics;
};

const decimalFormatter = new Intl.NumberFormat("pt-BR", {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

const integerFormatter = new Intl.NumberFormat("pt-BR", {
  maximumFractionDigits: 0,
});

/**
 * O quadro de diagnósticos do MCMC: aceitação, R-hat, ESS e tempo, com o
 * alerta do tema quando a rodada fica fora da faixa.
 */
export function DiagnosticsBoard({ diagnostics }: DiagnosticsBoardProps) {
  const ok = diagnostics.ok;
  const tiles = [
    {
      label: copy.modelPanel.diagnostics.acceptance.label,
      value: `${Math.round(diagnostics.accept_rate * 100)}%`,
      hint: copy.modelPanel.diagnostics.acceptance.hint,
    },
    {
      label: copy.modelPanel.diagnostics.rhat.label,
      value: decimalFormatter.format(diagnostics.rhat_max),
      hint: copy.modelPanel.diagnostics.rhat.hint,
    },
    {
      label: copy.modelPanel.diagnostics.ess.label,
      value: integerFormatter.format(Math.round(diagnostics.ess_min)),
      hint: copy.modelPanel.diagnostics.ess.hint,
    },
    {
      label: copy.modelPanel.diagnostics.time.label,
      value: copy.modelPanel.diagnostics.timeValue(diagnostics.elapsed_ms),
      hint: copy.modelPanel.diagnostics.time.hint,
    },
  ];

  return (
    <Card className="gap-3 rounded-xl border bg-card p-4 text-card-foreground shadow-sm ring-0 md:p-6">
      <h2 className="text-lg font-semibold">
        {copy.modelPanel.diagnostics.title}
      </h2>

      {ok ? (
        <p className="flex items-center gap-2 text-sm font-medium">
          <CircleCheck
            className="size-4 shrink-0 text-primary"
            aria-hidden="true"
          />
          {copy.modelPanel.diagnostics.ok}
        </p>
      ) : (
        <p
          role="alert"
          className="flex items-start gap-2 rounded-lg border border-destructive p-3 text-sm font-medium"
        >
          <TriangleAlert
            className="mt-0.5 size-4 shrink-0 text-destructive"
            aria-hidden="true"
          />
          {copy.modelPanel.diagnostics.alert}
        </p>
      )}

      <div className="grid grid-cols-2 gap-2 md:grid-cols-4 md:gap-3">
        {tiles.map((tile) => (
          <div
            key={tile.label}
            className={cn(
              "flex flex-col gap-1 rounded-lg bg-muted p-3 md:p-4",
              !ok && "border border-destructive",
            )}
          >
            <span className="text-sm text-muted-foreground">{tile.label}</span>
            <span className="text-2xl font-semibold tabular-nums">
              {tile.value}
            </span>
            <span className="text-xs text-muted-foreground">{tile.hint}</span>
          </div>
        ))}
      </div>
    </Card>
  );
}
