import { useQuery } from "@tanstack/react-query";
import { TriangleAlert } from "lucide-react";

import { experimentQuery } from "@/api/queries";
import { Skeleton } from "@/components/ui/skeleton";
import { PageHeader } from "@/features/compare/page-header";
import { copy } from "@/lib/copy";
import { AccuracyChart } from "./accuracy-chart";
import { ExperimentMessage } from "./experiment-message";
import { ParticipantBars } from "./participant-bars";
import { ResultsTable } from "./results-table";

const MAIN_CLASS =
  "mx-auto flex w-full max-w-5xl flex-1 flex-col gap-4 px-4 py-5 md:gap-6 md:py-10";

const DEMO_LINE_CLASS = "text-center text-xs text-muted-foreground md:hidden";

/**
 * O painel do experimento: a curva de acurácia por número de pares, a tabela
 * dos números e as barras por participante.
 */
export function ExperimentPage() {
  const experimentState = useQuery(experimentQuery());

  const demoLine = <p className={DEMO_LINE_CLASS}>{copy.common.demoCatalog}</p>;

  if (experimentState.isError) {
    return (
      <div className="flex min-h-dvh flex-col">
        <PageHeader active="experiment" />
        <main className={MAIN_CLASS}>
          <ExperimentMessage
            tone="error"
            onRetry={() => void experimentState.refetch()}
          />
          {demoLine}
        </main>
      </div>
    );
  }

  if (experimentState.isPending) {
    return (
      <div className="flex min-h-dvh flex-col">
        <PageHeader active="experiment" />
        <main className={MAIN_CLASS}>
          <div className="flex flex-col gap-1">
            <h1 className="text-2xl font-semibold tracking-tight md:text-3xl">
              {copy.experiment.title}
            </h1>
            <p className="text-muted-foreground md:text-lg">
              {copy.experiment.lead}
            </p>
          </div>
          <div aria-busy="true" className="flex flex-col gap-4">
            <span className="sr-only" role="status">
              {copy.experiment.loading}
            </span>
            <Skeleton className="h-80" />
            <Skeleton className="h-40" />
          </div>
          {demoLine}
        </main>
      </div>
    );
  }

  const summary = experimentState.data;

  if (summary.run_id === null) {
    return (
      <div className="flex min-h-dvh flex-col">
        <PageHeader active="experiment" />
        <main className={MAIN_CLASS}>
          <ExperimentMessage tone="empty" />
          {demoLine}
        </main>
      </div>
    );
  }

  return (
    <div className="flex min-h-dvh flex-col">
      <PageHeader active="experiment" />
      <main className={MAIN_CLASS}>
        <div className="flex flex-col gap-1">
          <h1 className="text-2xl font-semibold tracking-tight md:text-3xl">
            {copy.experiment.title}
          </h1>
          <p className="text-muted-foreground md:text-lg">
            {copy.experiment.lead}
          </p>
        </div>

        {summary.simulated ? (
          <p
            role="alert"
            className="flex items-start gap-2 rounded-lg border border-destructive bg-card p-3 text-sm font-medium"
          >
            <TriangleAlert
              className="mt-0.5 size-4 shrink-0 text-destructive"
              aria-hidden="true"
            />
            {copy.experiment.simulated}
          </p>
        ) : null}

        <p className="text-sm text-muted-foreground">
          {copy.experiment.how(summary.participants)}
        </p>

        <AccuracyChart rows={summary.rows} />
        <ResultsTable rows={summary.rows} />
        <ParticipantBars rows={summary.per_participant} />

        {demoLine}
      </main>
    </div>
  );
}
