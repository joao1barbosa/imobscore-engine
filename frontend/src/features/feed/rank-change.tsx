import { ArrowDown, ArrowUp, Sparkles } from "lucide-react";

import { copy } from "@/lib/copy";

type RankChangeProps = {
  rank: number;
  previousRank: number | null;
};

/** A mudança de posição de um imóvel em relação à lista de Antes. */
export function RankChange({ rank, previousRank }: RankChangeProps) {
  if (previousRank === null) {
    return (
      <span className="inline-flex items-center gap-1 text-xs font-medium text-muted-foreground">
        <Sparkles className="size-3.5" aria-hidden="true" />
        {copy.feed.enteredTop}
      </span>
    );
  }

  if (rank === previousRank) {
    return (
      <span className="text-xs font-medium text-muted-foreground">
        {copy.feed.kept}
      </span>
    );
  }

  const movedUp = rank < previousRank;
  const Icon = movedUp ? ArrowUp : ArrowDown;

  return (
    <span className="inline-flex items-center gap-1 text-xs font-medium text-muted-foreground">
      <Icon className="size-3.5" aria-hidden="true" />
      {movedUp
        ? copy.feed.movedUp(previousRank - rank)
        : copy.feed.movedDown(rank - previousRank)}
    </span>
  );
}
