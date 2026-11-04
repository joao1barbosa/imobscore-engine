import {
  Check,
  GraduationCap,
  TrendingUp,
  Users,
  type LucideIcon,
} from "lucide-react";

import type { PersonaOut } from "@/api/client";
import { RadioGroupItem } from "@/components/ui/radio-group";
import { cn } from "@/lib/cn";

type PersonaOptionProps = {
  persona: PersonaOut;
  selected: boolean;
};

const PERSONA_ICONS: Record<string, LucideIcon> = {
  familia: Users,
  investidor: TrendingUp,
  estudante: GraduationCap,
};

/** O cartão de uma persona, dentro do grupo de opções. */
export function PersonaOption({ persona, selected }: PersonaOptionProps) {
  const Icon = PERSONA_ICONS[persona.slug] ?? Users;

  return (
    <label
      className={cn(
        "relative flex cursor-pointer items-start gap-3 rounded-lg border p-3 md:flex-col md:gap-2",
        selected
          ? "border-primary bg-accent text-accent-foreground ring-1 ring-primary"
          : "border-input",
        "has-[:focus-visible]:ring-2 has-[:focus-visible]:ring-ring",
      )}
    >
      <RadioGroupItem value={persona.slug} className="sr-only" />
      <span
        className={cn(
          "grid size-9 shrink-0 place-items-center rounded-md",
          selected
            ? "bg-primary text-primary-foreground"
            : "bg-secondary text-secondary-foreground",
        )}
      >
        <Icon className="size-4" aria-hidden="true" />
      </span>
      <span className="flex flex-col gap-0.5">
        <span className="text-sm font-semibold">{persona.name}</span>
        <span className={cn("text-sm", !selected && "text-muted-foreground")}>
          {persona.description}
        </span>
      </span>
      {selected ? (
        <Check
          className="absolute top-3 right-3 size-4 text-primary"
          aria-hidden="true"
        />
      ) : null}
    </label>
  );
}
