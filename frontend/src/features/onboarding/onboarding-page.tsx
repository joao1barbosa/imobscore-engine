import { useState } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useQuery } from "@tanstack/react-query";
import { useForm, type Resolver } from "react-hook-form";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, ArrowRight, LoaderCircle } from "lucide-react";
import { toast } from "sonner";

import type { PersonaOut, SegmentOptions } from "@/api/client";
import {
  createSession,
  metaOptionsQuery,
  metaPersonasQuery,
} from "@/api/queries";
import { Button } from "@/components/ui/button";
import { Form } from "@/components/ui/form";
import { Progress } from "@/components/ui/progress";
import {
  COLLECTION_CITY,
  COLLECTION_PURPOSE,
  sliderCeiling,
  sliderFloor,
} from "@/features/collection/schema";
import { PageHeader } from "@/features/compare/page-header";
import { useSessionStore } from "@/stores/session-store";
import { cn } from "@/lib/cn";
import { copy } from "@/lib/copy";
import { OnboardingMessage } from "./onboarding-message";
import { OnboardingSkeleton } from "./onboarding-skeleton";
import { step1Schema, step2Schema, type OnboardingValues } from "./schema";
import { StepPersona } from "./step-persona";
import { StepPrice } from "./step-price";

type Step = 1 | 2;

type OnboardingFormProps = {
  segment: SegmentOptions;
  personas: PersonaOut[];
  step: Step;
  onStepChange: (step: Step) => void;
};

/** O formulário de dois passos. Ele só monta depois que os metadados chegam. */
function OnboardingForm({
  segment,
  personas,
  step,
  onStepChange,
}: OnboardingFormProps) {
  const navigate = useNavigate();
  const setSession = useSessionStore((state) => state.setSession);
  const [submitting, setSubmitting] = useState(false);

  const form = useForm<OnboardingValues>({
    resolver: zodResolver(
      step === 1 ? step1Schema(segment) : step2Schema,
    ) as unknown as Resolver<OnboardingValues>,
    defaultValues: {
      priceMin: sliderFloor(segment),
      priceMax: sliderCeiling(segment),
      personaSlug: undefined,
    },
  });

  const onSubmit = async () => {
    if (step === 1) {
      onStepChange(2);
      return;
    }

    const values = form.getValues();
    if (!values.personaSlug) {
      return;
    }

    setSubmitting(true);
    try {
      const session = await createSession({
        mode: "product",
        city: COLLECTION_CITY,
        purpose: COLLECTION_PURPOSE,
        price_min: values.priceMin,
        price_max: values.priceMax,
        persona_slug: values.personaSlug,
        consent: false,
      });
      setSession(session.id, "product");
      navigate("/comparar");
    } catch {
      toast.error(copy.onboarding.submitError);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Form {...form}>
      <form
        onSubmit={form.handleSubmit(onSubmit)}
        className="flex flex-col gap-4 md:gap-6"
        noValidate
      >
        <div className="flex items-center gap-3" aria-live="polite">
          <span className="shrink-0 text-sm font-medium">
            {copy.onboarding.step(step, 2)}
          </span>
          <Progress value={step * 50} className="flex-1" />
        </div>

        <div className="flex flex-col gap-1">
          <h1 className="text-2xl font-semibold tracking-tight md:text-3xl">
            {step === 1
              ? copy.onboarding.price.title
              : copy.onboarding.persona.title}
          </h1>
          <p className="text-muted-foreground md:text-lg">
            {step === 1
              ? copy.onboarding.price.lead
              : copy.onboarding.persona.lead}
          </p>
        </div>

        {step === 1 ? (
          <StepPrice segment={segment} disabled={submitting} />
        ) : (
          <StepPersona personas={personas} disabled={submitting} />
        )}

        <div className="flex flex-col-reverse gap-2 md:flex-row md:justify-between">
          {step === 1 ? (
            <span />
          ) : (
            <Button
              type="button"
              variant="outline"
              disabled={submitting}
              onClick={() => onStepChange(1)}
              className="h-12 gap-2 px-6 text-base"
            >
              <ArrowLeft className="size-4" aria-hidden="true" />
              {copy.onboarding.back}
            </Button>
          )}
          <Button
            type="submit"
            disabled={submitting}
            className="h-12 gap-2 px-6 text-base"
          >
            {submitting ? (
              <LoaderCircle
                className="size-4 animate-spin"
                aria-hidden="true"
              />
            ) : null}
            {step === 1
              ? copy.onboarding.next
              : submitting
                ? copy.onboarding.submitting
                : copy.onboarding.submit}
            {submitting ? null : (
              <ArrowRight className="size-4" aria-hidden="true" />
            )}
          </Button>
        </div>
      </form>
    </Form>
  );
}

/** A rota do onboarding: faixa de preço e perfil, em dois passos. */
export function OnboardingPage() {
  const [step, setStep] = useState<Step>(1);

  const optionsState = useQuery(metaOptionsQuery);
  const personasState = useQuery(metaPersonasQuery);

  const segment = optionsState.data?.segments.find(
    (item) =>
      item.city === COLLECTION_CITY && item.purpose === COLLECTION_PURPOSE,
  );
  const personas = personasState.data ?? [];
  const metaPending = optionsState.isPending || personasState.isPending;
  const metaFailed = optionsState.isError || personasState.isError;
  const metaEmpty =
    !metaPending && !metaFailed && (!segment || personas.length === 0);

  return (
    <div className="flex min-h-dvh flex-col">
      <PageHeader />
      <main
        className={cn(
          "mx-auto flex w-full flex-1 flex-col gap-4 px-4 py-5 md:gap-6 md:py-10",
          step === 1 ? "max-w-2xl" : "max-w-4xl",
        )}
      >
        {metaPending ? <OnboardingSkeleton /> : null}
        {metaFailed ? (
          <OnboardingMessage
            tone="error"
            title={copy.onboarding.loadError.title}
            description={copy.onboarding.loadError.description}
            onRetry={() => {
              void optionsState.refetch();
              void personasState.refetch();
            }}
          />
        ) : null}
        {metaEmpty ? (
          <OnboardingMessage
            tone="empty"
            title={copy.onboarding.empty.title}
            description={copy.onboarding.empty.description}
          />
        ) : null}
        {!metaPending && !metaFailed && !metaEmpty && segment ? (
          <OnboardingForm
            segment={segment}
            personas={personas}
            step={step}
            onStepChange={setStep}
          />
        ) : null}
      </main>
    </div>
  );
}
