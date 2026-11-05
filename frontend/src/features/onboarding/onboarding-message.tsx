import { PackageOpen, RefreshCw, TriangleAlert } from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/cn";
import { copy } from "@/lib/copy";

type OnboardingMessageProps = {
  tone: "empty" | "error";
  title: string;
  description: string;
  onRetry?: () => void;
};

/** A tela de erro ou de catálogo vazio, no lugar do formulário. */
export function OnboardingMessage({
  tone,
  title,
  description,
  onRetry,
}: OnboardingMessageProps) {
  const Icon = tone === "empty" ? PackageOpen : TriangleAlert;

  return (
    <div className="my-auto flex flex-col items-center gap-3 text-center">
      <span
        className={cn(
          "grid size-12 place-items-center rounded-full",
          tone === "empty"
            ? "bg-secondary text-secondary-foreground"
            : "bg-destructive text-destructive-foreground",
        )}
      >
        <Icon className="size-6" aria-hidden="true" />
      </span>
      <h1 className="text-xl font-semibold tracking-tight">{title}</h1>
      <p className="max-w-md text-sm text-muted-foreground">{description}</p>
      {onRetry ? (
        <Button onClick={onRetry} className="mt-1 h-10 gap-2 px-4">
          <RefreshCw className="size-4" aria-hidden="true" />
          {copy.common.retry}
        </Button>
      ) : null}
    </div>
  );
}
