import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { ChartNoAxesColumn, Info } from "lucide-react";

import { feedQuery, metaPersonasQuery, sessionQuery } from "@/api/queries";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { PageHeader } from "@/features/compare/page-header";
import { useSessionStore } from "@/stores/session-store";
import { copy } from "@/lib/copy";
import { BeforeAfterToggle } from "./before-after-toggle";
import { FeedCard } from "./feed-card";
import { FeedMessage } from "./feed-message";

/**
 * O feed da sessão: o ranking de afinidade com a alternância entre o cálculo
 * só com o perfil e o ajustado pelas escolhas.
 */
export function FeedPage() {
  const sessionId = useSessionStore((state) => state.sessionId);
  const reduceMotion = useReducedMotion();
  const [selection, setSelection] = useState<"before" | "after" | null>(null);

  const sessionState = useQuery({
    ...sessionQuery(sessionId ?? ""),
    enabled: Boolean(sessionId),
  });
  const personasState = useQuery(metaPersonasQuery);

  const session = sessionState.data;
  const answered = session?.answered ?? 0;
  const feedsEnabled = Boolean(sessionId) && sessionState.isSuccess;

  const beforeState = useQuery({
    ...feedQuery(sessionId ?? "", 0),
    enabled: feedsEnabled,
  });
  const afterState = useQuery({
    ...feedQuery(sessionId ?? "", answered),
    enabled: feedsEnabled,
  });

  const mode = selection ?? (answered > 0 ? "after" : "before");
  const showAfter = answered > 0 && mode === "after";

  const persona = personasState.data?.find(
    (item) => item.slug === session?.persona_slug,
  );
  const summary = session
    ? copy.feed.summary(persona?.name ?? session.persona_slug, answered)
    : null;

  const failed =
    sessionState.isError ||
    personasState.isError ||
    beforeState.isError ||
    afterState.isError;
  const loading =
    !sessionId ||
    sessionState.isPending ||
    personasState.isPending ||
    (sessionState.isSuccess && (beforeState.isPending || afterState.isPending));

  const retry = () => {
    void sessionState.refetch();
    void personasState.refetch();
    void beforeState.refetch();
    void afterState.refetch();
  };

  if (failed) {
    return (
      <div className="flex min-h-dvh flex-col">
        <PageHeader active="feed" />
        <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col gap-4 px-4 py-5 md:gap-6 md:py-10">
          <FeedMessage tone="error" onRetry={retry} />
          <p className="text-center text-xs text-muted-foreground md:hidden">
            {copy.common.demoCatalog}
          </p>
        </main>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex min-h-dvh flex-col">
        <PageHeader active="feed" />
        <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col gap-4 px-4 py-5 md:gap-6 md:py-10">
          <div className="flex flex-col gap-1">
            <h1 className="text-2xl font-semibold tracking-tight md:text-3xl">
              {copy.feed.title}
            </h1>
            {summary && persona ? (
              <p className="text-muted-foreground">{summary}</p>
            ) : null}
          </div>
          <div aria-busy="true" className="flex flex-col gap-3">
            <span className="sr-only" role="status">
              {copy.feed.loading}
            </span>
            <Skeleton className="h-36" />
            <Skeleton className="h-36" />
            <Skeleton className="h-36" />
          </div>
          <p className="text-center text-xs text-muted-foreground md:hidden">
            {copy.common.demoCatalog}
          </p>
        </main>
      </div>
    );
  }

  const items = (showAfter ? afterState.data : beforeState.data)?.items ?? [];
  const previousRanks = new Map(
    (beforeState.data?.items ?? []).map((item) => [item.listing.id, item.rank]),
  );

  if (items.length === 0) {
    return (
      <div className="flex min-h-dvh flex-col">
        <PageHeader active="feed" />
        <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col gap-4 px-4 py-5 md:gap-6 md:py-10">
          <FeedMessage tone="empty" />
          <p className="text-center text-xs text-muted-foreground md:hidden">
            {copy.common.demoCatalog}
          </p>
        </main>
      </div>
    );
  }

  return (
    <div className="flex min-h-dvh flex-col">
      <PageHeader active="feed" />
      <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col gap-4 px-4 py-5 md:gap-6 md:py-10">
        <div className="flex flex-col gap-1">
          <h1 className="text-2xl font-semibold tracking-tight md:text-3xl">
            {copy.feed.title}
          </h1>
          <p className="text-muted-foreground">{summary}</p>
        </div>

        {answered > 0 ? (
          <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
            <BeforeAfterToggle value={mode} onChange={setSelection} />
            <p className="text-sm font-medium" aria-live="polite">
              {showAfter ? copy.feed.afterHint(answered) : copy.feed.beforeHint}
            </p>
          </div>
        ) : (
          <p className="flex items-center gap-2 rounded-lg bg-muted p-3 text-sm font-medium">
            <Info className="size-4 shrink-0 text-primary" aria-hidden="true" />
            {copy.feed.noPairsHint}
          </p>
        )}

        <ol className="flex flex-col gap-3">
          <AnimatePresence initial={false}>
            {items.map((item) => (
              <motion.li
                key={item.listing.id}
                layout
                transition={
                  reduceMotion
                    ? { duration: 0 }
                    : {
                        duration: 0.5,
                        ease: [0.2, 0.8, 0.2, 1] as const,
                      }
                }
              >
                <FeedCard
                  item={item}
                  showReasons={showAfter}
                  previousRank={
                    showAfter
                      ? (previousRanks.get(item.listing.id) ?? null)
                      : undefined
                  }
                />
              </motion.li>
            ))}
          </AnimatePresence>
        </ol>

        <Button
          render={<Link to="/modelo" />}
          nativeButton={false}
          variant="outline"
          className="h-11 gap-2 self-center rounded-md px-5"
        >
          <ChartNoAxesColumn className="size-4" aria-hidden="true" />
          {copy.feed.toModel}
        </Button>

        <p className="text-center text-xs text-muted-foreground md:hidden">
          {copy.common.demoCatalog}
        </p>
      </main>
    </div>
  );
}
