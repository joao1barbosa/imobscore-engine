import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";

import {
  metaOptionsQuery,
  metaPersonasQuery,
  sessionQuery,
} from "@/api/queries";
import { ComparePanel } from "@/features/compare/compare-panel";
import { PageHeader } from "@/features/compare/page-header";
import { useSessionStore } from "@/stores/session-store";
import { copy } from "@/lib/copy";
import { CollectionForm } from "./collection-form";
import { CollectionMessage } from "./collection-message";
import { CollectionSkeleton } from "./collection-skeleton";
import { COLLECTION_CITY, COLLECTION_PURPOSE } from "./schema";
import { ThankYou } from "./thank-you";
import { Welcome } from "./welcome";

type Phase = "welcome" | "form" | "pairs" | "thanks";

/**
 * A rota da coleta: tela inicial, formulário, os 25 pares e o agradecimento.
 */
export function CollectionPage() {
  const sessionId = useSessionStore((state) => state.sessionId);
  const mode = useSessionStore((state) => state.mode);
  const setSession = useSessionStore((state) => state.setSession);
  const reset = useSessionStore((state) => state.reset);

  const [localPhase, setLocalPhase] = useState<Phase>("welcome");

  const hasStoredSession = Boolean(sessionId) && mode === "collection";
  const sessionState = useQuery({
    ...sessionQuery(sessionId ?? ""),
    enabled: hasStoredSession,
  });
  const storedSession = sessionState.data;

  // A sessão guardada define a fase enquanto a pessoa não fez nada na tela.
  const storedPhase: Phase | "none" =
    !hasStoredSession ||
    sessionState.isPending ||
    sessionState.isError ||
    !storedSession
      ? "none"
      : storedSession.status === "done"
        ? "thanks"
        : "pairs";

  // A sessão guardada não existe mais: ela é limpa e a tela inicial volta.
  useEffect(() => {
    if (hasStoredSession && sessionState.isError) {
      reset();
    }
  }, [hasStoredSession, reset, sessionState.isError]);

  const phase: Phase =
    localPhase === "welcome" && storedPhase !== "none"
      ? storedPhase
      : localPhase === "pairs" && !sessionId
        ? "form"
        : localPhase;

  const totalPairs = storedSession?.target_pairs ?? 0;

  const metaEnabled = phase === "form";
  const optionsState = useQuery({ ...metaOptionsQuery, enabled: metaEnabled });
  const personasState = useQuery({
    ...metaPersonasQuery,
    enabled: metaEnabled,
  });

  const segment = optionsState.data?.segments.find(
    (item) =>
      item.city === COLLECTION_CITY && item.purpose === COLLECTION_PURPOSE,
  );
  const personas = personasState.data ?? [];
  const metaPending = optionsState.isPending || personasState.isPending;
  const metaFailed = optionsState.isError || personasState.isError;
  const metaEmpty =
    !metaPending && !metaFailed && (!segment || personas.length === 0);

  if (phase === "pairs" && sessionId) {
    return (
      <ComparePanel
        sessionId={sessionId}
        onDone={() => setLocalPhase("thanks")}
      />
    );
  }

  return (
    <div className="flex min-h-dvh flex-col">
      <PageHeader />
      <main className="mx-auto flex w-full max-w-2xl flex-1 flex-col gap-4 px-4 py-5 md:gap-6 md:py-10">
        {phase === "welcome" ? (
          <Welcome onStart={() => setLocalPhase("form")} />
        ) : null}

        {phase === "thanks" ? <ThankYou total={totalPairs} /> : null}

        {phase === "form" ? (
          <>
            {metaPending ? <CollectionSkeleton /> : null}
            {metaFailed ? (
              <CollectionMessage
                tone="error"
                title={copy.collection.loadError.title}
                description={copy.collection.loadError.description}
                onRetry={() => {
                  void optionsState.refetch();
                  void personasState.refetch();
                }}
              />
            ) : null}
            {metaEmpty ? (
              <CollectionMessage
                tone="empty"
                title={copy.collection.empty.title}
                description={copy.collection.empty.description}
              />
            ) : null}
            {!metaPending && !metaFailed && !metaEmpty && segment ? (
              <CollectionForm
                segment={segment}
                personas={personas}
                onCreated={(id) => {
                  setSession(id, "collection");
                  setLocalPhase("pairs");
                }}
              />
            ) : null}
          </>
        ) : null}
      </main>
    </div>
  );
}
