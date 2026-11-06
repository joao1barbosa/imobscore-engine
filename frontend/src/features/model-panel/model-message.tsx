import { RefreshCw, TriangleAlert } from "lucide-react";

import { Button } from "@/components/ui/button";
import { copy } from "@/lib/copy";

type ModelMessageProps = {
  onRetry: () => void;
};

/** A tela de erro do painel do modelo, no lugar dos painéis. */
export function ModelMessage({ onRetry }: ModelMessageProps) {
  return (
    <div className="my-auto flex flex-col items-center gap-3 text-center">
      <span className="grid size-12 place-items-center rounded-full bg-destructive text-destructive-foreground">
        <TriangleAlert className="size-6" aria-hidden="true" />
      </span>
      <h1 className="text-xl font-semibold tracking-tight">
        {copy.modelPanel.loadError.title}
      </h1>
      <p className="max-w-md text-sm text-muted-foreground">
        {copy.modelPanel.loadError.description}
      </p>
      <Button onClick={onRetry} className="mt-1 h-10 gap-2 rounded-md px-4">
        <RefreshCw className="size-4" aria-hidden="true" />
        {copy.common.retry}
      </Button>
    </div>
  );
}
