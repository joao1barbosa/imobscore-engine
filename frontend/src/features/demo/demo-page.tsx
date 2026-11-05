import { useRef, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";

import type { PersonaOut, SessionCreate } from "@/api/client";
import { createSession, metaPersonasQuery } from "@/api/queries";
import { Skeleton } from "@/components/ui/skeleton";
import { PageHeader } from "@/features/compare/page-header";
import { useSessionStore } from "@/stores/session-store";
import { copy } from "@/lib/copy";
import { DemoMessage } from "./demo-message";
import { DemoPersonaCard } from "./demo-persona-card";

/**
 * O modo demo: um toque em uma persona cria a sessão com os
 * `demo_defaults` dela e leva o visitante direto às comparações.
 */
export function DemoPage() {
  const navigate = useNavigate();
  const setSession = useSessionStore((state) => state.setSession);
  const personasState = useQuery(metaPersonasQuery);

  const [pendingSlug, setPendingSlug] = useState<string | null>(null);
  const submitting = useRef(false);

  const personas = personasState.data ?? [];
  const sending = pendingSlug !== null;

  const choosePersona = async (persona: PersonaOut) => {
    if (submitting.current) {
      return;
    }
    submitting.current = true;
    setPendingSlug(persona.slug);

    const { city, purpose, price_min, price_max } = persona.demo_defaults;
    const body: SessionCreate = {
      mode: "demo",
      city,
      purpose: purpose as SessionCreate["purpose"],
      price_min,
      price_max,
      persona_slug: persona.slug as SessionCreate["persona_slug"],
      consent: false,
    };

    try {
      const session = await createSession(body);
      setSession(session.id, "demo");
      navigate("/comparar");
    } catch {
      toast.error(copy.onboarding.submitError);
    } finally {
      submitting.current = false;
      setPendingSlug(null);
    }
  };

  const intro = (
    <div className="flex flex-col gap-1 md:text-center">
      <h1 className="text-2xl font-semibold tracking-tight md:text-4xl">
        {copy.demo.title}
      </h1>
      <p className="text-muted-foreground md:text-lg">{copy.demo.lead}</p>
    </div>
  );

  return (
    <div className="flex min-h-dvh flex-col">
      <PageHeader />
      <main className="mx-auto flex w-full max-w-4xl flex-1 flex-col gap-4 px-4 py-5 md:gap-6 md:py-10">
        {personasState.isPending ? (
          <>
            {intro}
            <div
              aria-busy="true"
              className="grid gap-3 md:grid-cols-3 md:gap-6"
            >
              <span className="sr-only" role="status">
                {copy.demo.loading}
              </span>
              <Skeleton className="h-32" />
              <Skeleton className="h-32" />
              <Skeleton className="h-32" />
            </div>
          </>
        ) : null}

        {personasState.isError ? (
          <DemoMessage
            tone="error"
            onRetry={() => {
              void personasState.refetch();
            }}
          />
        ) : null}

        {!personasState.isPending &&
        !personasState.isError &&
        personas.length === 0 ? (
          <DemoMessage tone="empty" />
        ) : null}

        {!personasState.isPending &&
        !personasState.isError &&
        personas.length > 0 ? (
          <>
            {intro}
            <div className="grid gap-3 md:grid-cols-3 md:gap-6">
              {personas.map((persona) => (
                <DemoPersonaCard
                  key={persona.slug}
                  persona={persona}
                  state={
                    pendingSlug === persona.slug
                      ? "active"
                      : sending
                        ? "dimmed"
                        : "idle"
                  }
                  disabled={sending}
                  onChoose={() => {
                    void choosePersona(persona);
                  }}
                />
              ))}
            </div>
            {sending ? (
              <p
                className="text-center text-sm text-muted-foreground"
                role="status"
              >
                {copy.demo.submitting}
              </p>
            ) : null}
          </>
        ) : null}
      </main>
    </div>
  );
}
