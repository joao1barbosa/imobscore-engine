import { Link } from "react-router-dom";
import { RefreshCw, SearchX, TriangleAlert } from "lucide-react";

import { Button } from "@/components/ui/button";
import { copy } from "@/lib/copy";

type FeedMessageProps = {
  tone: "empty" | "error";
  onRetry?: () => void;
};

/** A tela de feed vazio ou de erro, no lugar da lista. */
export function FeedMessage({ tone, onRetry }: FeedMessageProps) {
  if (tone === "empty") {
    return (
      <div className="my-auto flex flex-col items-center gap-3 text-center">
        <span className="grid size-12 place-items-center rounded-full bg-secondary text-secondary-foreground">
          <SearchX className="size-6" aria-hidden="true" />
        </span>
        <h1 className="text-xl font-semibold tracking-tight">
          {copy.feed.empty.title}
        </h1>
        <p className="max-w-md text-sm text-muted-foreground">
          {copy.feed.empty.description}
        </p>
        <Button
          render={<Link to="/comecar" />}
          nativeButton={false}
          className="mt-1 h-10 rounded-md px-4"
        >
          <SearchX className="size-4" aria-hidden="true" />
          {copy.feed.empty.action}
        </Button>
      </div>
    );
  }

  return (
    <div className="my-auto flex flex-col items-center gap-3 text-center">
      <span className="grid size-12 place-items-center rounded-full bg-destructive text-destructive-foreground">
        <TriangleAlert className="size-6" aria-hidden="true" />
      </span>
      <h1 className="text-xl font-semibold tracking-tight">
        {copy.feed.loadError.title}
      </h1>
      <p className="max-w-md text-sm text-muted-foreground">
        {copy.feed.loadError.description}
      </p>
      {onRetry ? (
        <Button onClick={onRetry} className="mt-1 h-10 gap-2 px-4">
          <RefreshCw className="size-4" aria-hidden="true" />
          {copy.common.retry}
        </Button>
      ) : null}
    </div>
  );
}
