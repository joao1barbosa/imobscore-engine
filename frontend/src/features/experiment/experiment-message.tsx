import { FlaskConical, RefreshCw, TriangleAlert } from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/cn";
import { copy } from "@/lib/copy";

type ExperimentMessageProps = {
  tone: "empty" | "error";
  onRetry?: () => void;
};

/** A tela de estado vazio ou de erro do painel do experimento. */
export function ExperimentMessage({ tone, onRetry }: ExperimentMessageProps) {
  const isError = tone === "error";
  const title = isError
    ? copy.experiment.loadError.title
    : copy.experiment.empty.title;
  const description = isError
    ? copy.experiment.loadError.description
    : copy.experiment.empty.description;
  const Icon = isError ? TriangleAlert : FlaskConical;

  return (
    <div className="my-auto flex flex-col items-center gap-3 text-center">
      <span
        className={cn(
          "grid size-12 place-items-center rounded-full",
          isError
            ? "bg-destructive text-destructive-foreground"
            : "bg-secondary text-secondary-foreground",
        )}
      >
        <Icon className="size-6" aria-hidden="true" />
      </span>
      <h1 className="text-xl font-semibold tracking-tight">{title}</h1>
      <p className="max-w-md text-sm text-muted-foreground">{description}</p>
      {isError && onRetry ? (
        <Button onClick={onRetry} className="mt-1 h-10 gap-2 rounded-md px-4">
          <RefreshCw className="size-4" aria-hidden="true" />
          {copy.common.retry}
        </Button>
      ) : null}
    </div>
  );
}
