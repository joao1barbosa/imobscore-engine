import {
  GraduationCap,
  LoaderCircle,
  TrendingUp,
  Users,
  type LucideIcon,
} from "lucide-react";

import type { PersonaOut } from "@/api/client";
import { cn } from "@/lib/cn";
import { copy } from "@/lib/copy";
import { formatBRL } from "@/lib/format";

type DemoPersonaCardProps = {
  persona: PersonaOut;
  state: "idle" | "active" | "dimmed";
  disabled: boolean;
  onChoose: () => void;
};

const PERSONA_ICONS: Record<string, LucideIcon> = {
  familia: Users,
  investidor: TrendingUp,
  estudante: GraduationCap,
};

/** O cartão de uma persona no modo demo: o cartão inteiro é o botão. */
export function DemoPersonaCard({
  persona,
  state,
  disabled,
  onChoose,
}: DemoPersonaCardProps) {
  const active = state === "active";
  const Icon = active ? LoaderCircle : (PERSONA_ICONS[persona.slug] ?? Users);
  const { price_min, price_max } = persona.demo_defaults;

  return (
    <button
      type="button"
      aria-label={copy.demo.chooseLabel(persona.name)}
      disabled={disabled}
      onClick={onChoose}
      className={cn(
        "flex w-full items-start gap-4 rounded-xl border bg-card p-4 text-left shadow-sm transition md:flex-col md:p-6",
        "focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring",
        disabled
          ? "cursor-not-allowed"
          : "cursor-pointer hover:-translate-y-0.5 hover:border-primary hover:shadow-md",
        active && "border-primary ring-2 ring-primary",
        state === "dimmed" && "opacity-50",
      )}
    >
      <span
        className={cn(
          "grid size-12 shrink-0 place-items-center rounded-lg",
          active
            ? "bg-primary text-primary-foreground"
            : "bg-accent text-accent-foreground",
        )}
      >
        <Icon
          className={cn("size-6", active && "animate-spin")}
          aria-hidden="true"
        />
      </span>
      <span className="flex flex-col gap-1">
        <span className="text-lg font-semibold">{persona.name}</span>
        <span className="text-sm text-muted-foreground">
          {persona.description}
        </span>
        <span className="mt-1 text-sm font-medium tabular-nums">
          {copy.demo.range(formatBRL(price_min), formatBRL(price_max))}
        </span>
      </span>
    </button>
  );
}
