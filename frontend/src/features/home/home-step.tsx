import type { LucideIcon } from "lucide-react";

import { copy } from "@/lib/copy";

type HomeStepProps = {
  index: number;
  icon: LucideIcon;
  title: string;
  body: string;
};

/** Um dos três passos numerados da tela de início. */
export function HomeStep({ index, icon: Icon, title, body }: HomeStepProps) {
  return (
    <li className="flex gap-3 rounded-xl border bg-card p-4 shadow-sm md:flex-col md:p-5">
      <span className="grid size-10 shrink-0 place-items-center rounded-lg bg-accent text-accent-foreground">
        <Icon className="size-5" aria-hidden="true" />
      </span>
      <div className="flex flex-col gap-1">
        <h2 className="font-semibold">{copy.home.stepTitle(index, title)}</h2>
        <p className="text-sm text-muted-foreground">{body}</p>
      </div>
    </li>
  );
}
