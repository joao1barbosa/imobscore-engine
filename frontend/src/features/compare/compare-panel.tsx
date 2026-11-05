import { useCallback, useEffect, useRef, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { LoaderCircle } from "lucide-react";
import { toast } from "sonner";

import { ApiRequestError } from "@/api/client";
import { answerPair, pairQuery } from "@/api/queries";
import { Progress } from "@/components/ui/progress";
import { useSessionStore } from "@/stores/session-store";
import { copy } from "@/lib/copy";
import { CompareMessage } from "./compare-message";
import { CompareSkeleton } from "./compare-skeleton";
import { ListingChoiceCard } from "./listing-choice-card";
import { PageHeader } from "./page-header";

type ComparePanelProps = {
  sessionId: string;
  onDone: () => void;
};

/**
 * A comparação de um par: busca o par pendente, mede o tempo da resposta e
 * manda a escolha para a API.
 */
export function ComparePanel({ sessionId, onDone }: ComparePanelProps) {
  const queryClient = useQueryClient();
  const reset = useSessionStore((state) => state.reset);
  const reduceMotion = useReducedMotion();
  const [sending, setSending] = useState<"A" | "B" | null>(null);
  const [notFound, setNotFound] = useState(false);
  const appearedAt = useRef(0);

  const onDoneRef = useRef(onDone);
  useEffect(() => {
    onDoneRef.current = onDone;
  }, [onDone]);

  const pairState = useQuery(pairQuery(sessionId));
  const pair = pairState.data ?? null;
  const position = pair?.position;

  // A sessão que não existe mais é a única que some da tela: nos outros
  // erros, as respostas já gravadas ficam guardadas e a pessoa pode tentar
  // de novo.
  const sessionMissing =
    pairState.error instanceof ApiRequestError &&
    pairState.error.code === "session_not_found";

  // O tempo de resposta conta desde que o par aparece.
  useEffect(() => {
    if (position !== undefined) {
      appearedAt.current = performance.now();
    }
  }, [position]);

  const handleError = useCallback(
    (error: unknown, fallback: string) => {
      if (error instanceof ApiRequestError) {
        if (
          error.code === "pair_already_answered" ||
          error.code === "pair_out_of_order"
        ) {
          // Não é erro para a pessoa: o par é buscado de novo, em silêncio.
          void queryClient.invalidateQueries({ queryKey: ["pair", sessionId] });
          return;
        }
        if (error.code === "session_done") {
          onDoneRef.current();
          return;
        }
        if (error.code === "session_not_found") {
          reset();
          setNotFound(true);
          return;
        }
      }
      toast.error(fallback);
    },
    [queryClient, reset, sessionId],
  );

  // A sessão acabou: a API respondeu 204 no par pendente.
  useEffect(() => {
    if (pairState.isSuccess && pair === null) {
      onDoneRef.current();
    }
  }, [pairState.isSuccess, pair]);

  const choose = useCallback(
    async (choice: "A" | "B") => {
      if (sending !== null || !pair) {
        return;
      }
      setSending(choice);
      const responseMs = Math.max(
        0,
        Math.round(performance.now() - appearedAt.current),
      );
      try {
        const answer = await answerPair(sessionId, pair.position, {
          chosen: choice,
          response_ms: responseMs,
        });
        if (answer.done) {
          onDoneRef.current();
          return;
        }
        await queryClient.invalidateQueries({ queryKey: ["pair", sessionId] });
        await queryClient.invalidateQueries({
          queryKey: ["session", sessionId],
        });
      } catch (error) {
        handleError(error, copy.compare.answerError);
      } finally {
        setSending(null);
      }
    },
    [handleError, pair, queryClient, sending, sessionId],
  );

  // As setas escolhem o par, fora dos campos de texto.
  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") {
        return;
      }
      const target = event.target as HTMLElement | null;
      if (
        target &&
        (target.tagName === "INPUT" ||
          target.tagName === "TEXTAREA" ||
          target.isContentEditable)
      ) {
        return;
      }
      event.preventDefault();
      void choose(event.key === "ArrowLeft" ? "A" : "B");
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [choose]);

  if (notFound || sessionMissing) {
    return (
      <div className="flex min-h-dvh flex-col">
        <PageHeader />
        <main className="mx-auto flex w-full max-w-md flex-1 items-center px-4 py-3">
          <CompareMessage
            tone="error"
            title={copy.common.apiErrors.session_not_found}
            description={copy.compare.loadError.description}
          />
        </main>
      </div>
    );
  }

  if (pairState.isError) {
    return (
      <div className="flex min-h-dvh flex-col">
        <PageHeader />
        <main className="mx-auto flex w-full max-w-md flex-1 items-center px-4 py-3">
          <CompareMessage
            tone="error"
            title={copy.compare.loadError.title}
            description={copy.compare.loadError.description}
            onRetry={() => {
              void pairState.refetch();
            }}
          />
        </main>
      </div>
    );
  }

  if (pairState.isPending) {
    return (
      <div className="flex min-h-dvh flex-col">
        <PageHeader />
        <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col gap-3 px-4 py-3 md:gap-6 md:py-8">
          <div className="flex flex-col gap-1">
            <h1 className="text-xl font-semibold tracking-tight md:text-3xl">
              {copy.compare.question}
            </h1>
            <p className="text-sm text-muted-foreground md:text-base">
              {copy.compare.hint}
            </p>
          </div>
          <CompareSkeleton />
        </main>
      </div>
    );
  }

  if (pair === null) {
    return (
      <div className="flex min-h-dvh flex-col">
        <PageHeader />
        <main className="mx-auto flex w-full max-w-md flex-1 items-center px-4 py-3">
          <CompareMessage
            tone="done"
            title={copy.compare.empty.title}
            description={copy.compare.empty.description}
          />
        </main>
      </div>
    );
  }

  return (
    <div className="flex min-h-dvh flex-col">
      <PageHeader />
      <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col gap-3 px-4 py-3 md:gap-6 md:py-8">
        <div className="flex items-center gap-3" aria-live="polite">
          <span className="shrink-0 text-sm font-medium tabular-nums">
            {copy.compare.progress(pair.position, pair.total)}
          </span>
          <Progress
            value={pair.position - 1}
            max={pair.total}
            className="h-2 min-w-0 flex-1 gap-0"
          />
        </div>
        <div className="flex flex-col gap-1">
          <h1 className="text-xl font-semibold tracking-tight md:text-3xl">
            {copy.compare.question}
          </h1>
          <p className="text-sm text-muted-foreground md:text-base">
            {copy.compare.hint}
          </p>
        </div>
        <AnimatePresence mode="wait" initial={false}>
          <motion.div
            key={pair.position}
            initial={reduceMotion ? false : { opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={reduceMotion ? undefined : { opacity: 0, scale: 0.98 }}
            transition={{ duration: 0.2 }}
            className="grid gap-3 md:grid-cols-2 md:gap-6"
          >
            <ListingChoiceCard
              listing={pair.listing_a}
              shortcut={copy.compare.keyLeft}
              disabled={sending !== null}
              state={
                sending === "A" ? "chosen" : sending === "B" ? "dimmed" : "idle"
              }
              onChoose={() => void choose("A")}
            />
            <ListingChoiceCard
              listing={pair.listing_b}
              shortcut={copy.compare.keyRight}
              disabled={sending !== null}
              state={
                sending === "B" ? "chosen" : sending === "A" ? "dimmed" : "idle"
              }
              onChoose={() => void choose("B")}
            />
          </motion.div>
        </AnimatePresence>
        {sending !== null ? (
          <p
            className="flex items-center justify-center gap-2 text-sm text-muted-foreground"
            role="status"
          >
            <LoaderCircle className="size-4 animate-spin" aria-hidden="true" />
            {copy.compare.sending}
          </p>
        ) : (
          <p className="hidden items-center justify-center gap-2 text-sm text-muted-foreground md:flex">
            {copy.compare.keyboardHint}
          </p>
        )}
      </main>
    </div>
  );
}
