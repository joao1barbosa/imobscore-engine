import { useFormContext } from "react-hook-form";
import { CircleAlert } from "lucide-react";

import type { PersonaOut } from "@/api/client";
import { RadioGroup } from "@/components/ui/radio-group";
import { PersonaOption } from "@/features/collection/persona-option";
import type { PersonaSlug } from "@/features/collection/schema";
import { copy } from "@/lib/copy";
import type { OnboardingValues } from "./schema";

type StepPersonaProps = {
  personas: PersonaOut[];
  disabled: boolean;
};

/** O passo 2: os cartões das três personas. */
export function StepPersona({ personas, disabled }: StepPersonaProps) {
  const form = useFormContext<OnboardingValues>();
  const selected = form.watch("personaSlug");
  const error = form.formState.errors.personaSlug?.message;

  return (
    <div className="flex flex-col gap-2">
      <RadioGroup
        value={selected ?? ""}
        onValueChange={(value) => {
          form.setValue("personaSlug", value as PersonaSlug, {
            shouldValidate: true,
          });
        }}
        aria-label={copy.onboarding.persona.title}
        className="gap-3"
        disabled={disabled}
      >
        <div className="grid gap-3 md:grid-cols-3">
          {personas.map((persona) => (
            <PersonaOption
              key={persona.slug}
              persona={persona}
              selected={selected === persona.slug}
            />
          ))}
        </div>
      </RadioGroup>
      {error ? (
        <p className="flex items-center gap-1.5 text-sm font-medium text-destructive">
          <CircleAlert className="size-4" aria-hidden="true" />
          {String(error)}
        </p>
      ) : null}
    </div>
  );
}
