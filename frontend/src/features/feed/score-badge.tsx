import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { cn } from "@/lib/cn";
import { copy } from "@/lib/copy";

type ScoreBadgeProps = {
  score: number;
  low: number;
  high: number;
};

function scoreBand(score: number): string {
  if (score >= 70) {
    return "bg-score-high";
  }
  if (score >= 40) {
    return "bg-score-mid";
  }
  return "bg-score-low";
}

/** O selo do score, com a faixa de cor e o intervalo de incerteza. */
export function ScoreBadge({ score, low, high }: ScoreBadgeProps) {
  const label = copy.feed.scoreTooltip(score);

  return (
    <div className="flex flex-col items-center gap-1 text-center">
      <Tooltip>
        <TooltipTrigger
          render={<span />}
          tabIndex={0}
          aria-label={label}
          className={cn(
            "grid size-14 place-items-center rounded-full text-xl font-semibold text-score-foreground tabular-nums focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring md:size-16 md:text-2xl",
            scoreBand(score),
          )}
        >
          {score}
        </TooltipTrigger>
        <TooltipContent>{label}</TooltipContent>
      </Tooltip>
      <span className="text-xs whitespace-nowrap text-muted-foreground">
        {copy.feed.interval(Math.round(low), Math.round(high))}
      </span>
    </div>
  );
}
