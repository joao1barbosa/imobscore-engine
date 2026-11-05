import { useRef, useState } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm, type FieldErrors, type Resolver } from "react-hook-form";
import { ArrowRight, CircleAlert, LoaderCircle, MapPin } from "lucide-react";
import { toast } from "sonner";

import type { PersonaOut, SegmentOptions } from "@/api/client";
import { createSession } from "@/api/queries";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  useFormField,
} from "@/components/ui/form";
import { RadioGroup } from "@/components/ui/radio-group";
import { copy } from "@/lib/copy";
import { PersonaOption } from "./persona-option";
import { PriceRangeField } from "./price-range-field";
import {
  COLLECTION_CITY,
  COLLECTION_PURPOSE,
  collectionFormSchema,
  sliderCeiling,
  sliderFloor,
  type CollectionFormValues,
} from "./schema";

type CollectionFormProps = {
  segment: SegmentOptions;
  personas: PersonaOut[];
  onCreated: (sessionId: string) => void;
};

/**
 * O erro de um campo, com ícone e texto: a mensagem não depende só da cor.
 */
function FieldError() {
  const { error, formMessageId } = useFormField();
  const message = error?.message;

  if (!message) {
    return null;
  }

  return (
    <p
      id={formMessageId}
      className="flex items-center gap-1.5 text-sm font-medium text-destructive"
    >
      <CircleAlert className="size-4" aria-hidden="true" />
      {String(message)}
    </p>
  );
}

/** O formulário da coleta: consentimento, faixa de preço e persona. */
export function CollectionForm({
  segment,
  personas,
  onCreated,
}: CollectionFormProps) {
  const [submitting, setSubmitting] = useState(false);

  // As três seções do formulário, para o erro aparecer à vista.
  const consentRef = useRef<HTMLElement>(null);
  const priceRef = useRef<HTMLElement>(null);
  const personaRef = useRef<HTMLElement>(null);

  const form = useForm<CollectionFormValues>({
    resolver: zodResolver(
      collectionFormSchema(segment),
    ) as unknown as Resolver<CollectionFormValues>,
    defaultValues: {
      consent: false,
      priceMin: sliderFloor(segment),
      priceMax: sliderCeiling(segment),
      personaSlug: undefined,
    },
  });

  /**
   * O envio foi recusado: a primeira seção com erro vai para o centro da
   * tela, para a pessoa ver a mensagem sem rolar.
   */
  const onInvalid = (errors: FieldErrors<CollectionFormValues>) => {
    if (errors.consent) {
      consentRef.current?.scrollIntoView({ block: "center" });
      return;
    }
    if (errors.priceMin || errors.priceMax) {
      priceRef.current?.scrollIntoView({ block: "center" });
      return;
    }
    if (errors.personaSlug) {
      personaRef.current?.scrollIntoView({ block: "center" });
    }
  };

  /**
   * O envio é tratado no evento: o React Hook Form valida e só então chama o
   * `onInvalid`, que leva a seção com erro para o centro da tela.
   */
  const onFormSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    void form.handleSubmit(onSubmit, onInvalid)(event);
  };

  const onSubmit = async (values: CollectionFormValues) => {
    if (!values.personaSlug) {
      return;
    }
    setSubmitting(true);
    try {
      const session = await createSession({
        mode: "collection",
        city: COLLECTION_CITY,
        purpose: COLLECTION_PURPOSE,
        price_min: values.priceMin,
        price_max: values.priceMax,
        persona_slug: values.personaSlug,
        consent: true,
      });
      onCreated(session.id);
    } catch {
      toast.error(copy.collection.submitError);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Form {...form}>
      <form
        onSubmit={onFormSubmit}
        className="flex flex-col gap-4 md:gap-6"
        noValidate
      >
        <div className="flex flex-col gap-1">
          <h1 className="text-2xl font-semibold tracking-tight md:text-3xl">
            {copy.collection.form.title}
          </h1>
          <p className="text-muted-foreground md:text-lg">
            {copy.collection.form.lead}
          </p>
        </div>

        <section
          ref={consentRef}
          className="flex flex-col gap-4 rounded-xl border bg-card p-4 text-card-foreground shadow-sm md:p-6"
        >
          <h2 className="font-semibold">
            {copy.collection.sections.participation}
          </h2>
          <FormField
            control={form.control}
            name="consent"
            render={({ field }) => (
              <FormItem>
                <label className="flex cursor-pointer items-start gap-3 rounded-lg border border-input bg-muted p-3 has-[:focus-visible]:ring-2 has-[:focus-visible]:ring-ring has-[&>[aria-invalid=true]]:border-destructive">
                  <FormControl>
                    <Checkbox
                      checked={field.value}
                      onCheckedChange={field.onChange}
                      className="mt-0.5 size-5"
                    />
                  </FormControl>
                  <span className="flex flex-col gap-1">
                    <span className="text-sm font-medium">
                      {copy.collection.consent.label}
                    </span>
                    <span className="text-sm text-muted-foreground">
                      {copy.collection.consent.details}
                    </span>
                  </span>
                </label>
                <FieldError />
              </FormItem>
            )}
          />
        </section>

        <section
          ref={priceRef}
          className="flex flex-col gap-4 rounded-xl border bg-card p-4 text-card-foreground shadow-sm md:p-6"
        >
          <h2 className="font-semibold">{copy.collection.sections.search}</h2>
          <p className="flex items-center gap-2 rounded-lg bg-muted p-3 text-sm font-medium">
            <MapPin className="size-4 text-primary" aria-hidden="true" />
            {copy.collection.segment}
          </p>
          <PriceRangeField
            floor={segment.price_floor}
            ceiling={segment.price_ceiling}
            disabled={submitting}
          />
        </section>

        <section
          ref={personaRef}
          className="flex flex-col gap-4 rounded-xl border bg-card p-4 text-card-foreground shadow-sm md:p-6"
        >
          <h2 className="font-semibold">{copy.collection.sections.persona}</h2>
          <FormField
            control={form.control}
            name="personaSlug"
            render={({ field }) => (
              <FormItem>
                <RadioGroup
                  value={field.value ?? ""}
                  onValueChange={(value) => field.onChange(value)}
                  aria-label={copy.collection.sections.persona}
                  className="gap-2"
                >
                  <div className="grid gap-2 md:grid-cols-3">
                    {personas.map((persona) => (
                      <PersonaOption
                        key={persona.slug}
                        persona={persona}
                        selected={field.value === persona.slug}
                      />
                    ))}
                  </div>
                </RadioGroup>
                <FieldError />
              </FormItem>
            )}
          />
        </section>

        <Button
          type="submit"
          disabled={submitting}
          className="h-12 w-full gap-2 px-6 text-base md:w-auto md:self-end"
        >
          {submitting ? (
            <LoaderCircle className="size-4 animate-spin" aria-hidden="true" />
          ) : null}
          {submitting ? copy.collection.submitting : copy.collection.submit}
          {submitting ? null : (
            <ArrowRight className="size-4" aria-hidden="true" />
          )}
        </Button>
      </form>
    </Form>
  );
}
