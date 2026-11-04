import { CircleCheck, RefreshCw, TriangleAlert } from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/cn";
import { copy } from "@/lib/copy";

type CompareMessageProps = {
  tone: "done" | "error";
  title: string;
  description: string;
  onRetry?: () => void;
};

/** A tela de fim da coleta ou de erro, no lugar dos cartões do par. */
export function CompareMessage({
  tone,
  title,
  description,
  onRetry,
}: CompareMessageProps) {
  const Icon = tone === "done" ? CircleCheck : TriangleAlert;

  return (
    <div className="my-auto flex flex-col items-center gap-3 text-center">
      <span
        className={cn(
          "grid size-12 place-items-center rounded-full",
          tone === "done"
            ? "bg-accent text-accent-foreground"
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
