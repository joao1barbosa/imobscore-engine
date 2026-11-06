import { useQuery } from "@tanstack/react-query";

import {
  metaFeaturesQuery,
  metaPersonasQuery,
  posteriorQuery,
  sessionQuery,
} from "@/api/queries";
import { Skeleton } from "@/components/ui/skeleton";
import { PageHeader } from "@/features/compare/page-header";
import { copy } from "@/lib/copy";
import { useSessionStore } from "@/stores/session-store";
import { DiagnosticsBoard } from "./diagnostics-board";
import { ModelMessage } from "./model-message";
import { TraceChart } from "./trace-chart";
import { WeightsChart } from "./weights-chart";

const MAIN_CLASS =
  "mx-auto flex w-full max-w-5xl flex-1 flex-col gap-4 px-4 py-5 md:gap-6 md:py-10";

const DEMO_LINE_CLASS = "text-center text-xs text-muted-foreground md:hidden";

/**
 * O painel do modelo: os pesos da priori e da posteriori, o quadro de
 * diagnósticos e o traço das cadeias do peso escolhido.
 */
export function ModelPanelPage() {
  const sessionId = useSessionStore((state) => state.sessionId);

  const sessionState = useQuery({
    ...sessionQuery(sessionId ?? ""),
    enabled: Boolean(sessionId),
  });
  const personasState = useQuery(metaPersonasQuery);
  const posteriorState = useQuery({
    ...posteriorQuery(sessionId ?? ""),
    enabled: Boolean(sessionId),
  });
  const featuresState = useQuery(metaFeaturesQuery);

  const session = sessionState.data;
  const answered = session?.answered ?? 0;
  const priorOnly = answered === 0;
  const persona = personasState.data?.find(
    (item) => item.slug === session?.persona_slug,
  );
  const summary = session
    ? copy.feed.summary(persona?.name ?? session.persona_slug, session.answered)
    : null;

  const failed =
    sessionState.isError || personasState.isError || posteriorState.isError;
  const loading =
    !sessionId ||
    sessionState.isPending ||
    personasState.isPending ||
    posteriorState.isPending;

  const retry = () => {
    void sessionState.refetch();
    void personasState.refetch();
    void posteriorState.refetch();
  };

  if (failed) {
    return (
      <div className="flex min-h-dvh flex-col">
        <PageHeader active="model" />
        <main className={MAIN_CLASS}>
          <ModelMessage onRetry={retry} />
          <p className={DEMO_LINE_CLASS}>{copy.common.demoCatalog}</p>
        </main>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex min-h-dvh flex-col">
        <PageHeader active="model" />
        <main className={MAIN_CLASS}>
          <div className="flex flex-col gap-1">
            <h1 className="text-2xl font-semibold tracking-tight md:text-3xl">
              {copy.modelPanel.title}
            </h1>
            {summary ? (
              <p className="text-muted-foreground">{summary}</p>
            ) : null}
          </div>
          <div aria-busy="true" className="flex flex-col gap-4">
            <span className="sr-only" role="status">
              {copy.modelPanel.loading}
            </span>
            <Skeleton className="h-96" />
            <Skeleton className="h-40" />
          </div>
          <p className={DEMO_LINE_CLASS}>{copy.common.demoCatalog}</p>
        </main>
      </div>
    );
  }

  const posterior = posteriorState.data;

  if (!posterior) {
    return null;
  }

  return (
    <div className="flex min-h-dvh flex-col">
      <PageHeader active="model" />
      <main className={MAIN_CLASS}>
        <div className="flex flex-col gap-1">
          <h1 className="text-2xl font-semibold tracking-tight md:text-3xl">
            {copy.modelPanel.title}
          </h1>
          {summary ? <p className="text-muted-foreground">{summary}</p> : null}
        </div>

        <WeightsChart weights={posterior.weights} priorOnly={priorOnly} />

        {priorOnly ? null : (
          <>
            <DiagnosticsBoard diagnostics={posterior.diagnostics} />
            <TraceChart
              sessionId={sessionId ?? ""}
              n={answered}
              features={featuresState.data ?? []}
            />
          </>
        )}

        <p className={DEMO_LINE_CLASS}>{copy.common.demoCatalog}</p>
      </main>
    </div>
  );
}
