import {
  Bath,
  BedDouble,
  CalendarDays,
  CarFront,
  Dumbbell,
  MapPin,
  Minus,
  Plus,
  Ruler,
} from "lucide-react";

import type { FeedItem } from "@/api/queries";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/cn";
import { copy } from "@/lib/copy";
import { formatArea, formatBRL, formatDistance } from "@/lib/format";
import { RankChange } from "./rank-change";
import { ScoreBadge } from "./score-badge";

type FeedCardProps = {
  item: FeedItem;
  showReasons: boolean;
  previousRank: number | null | undefined;
};

const ILLUSTRATION_ALT = copy.compare.listing.illustrationAlt as Record<
  string,
  string
>;

/** O cartão de um imóvel do feed: ilustração, dados e selo de afinidade. */
export function FeedCard({ item, showReasons, previousRank }: FeedCardProps) {
  const { listing } = item;
  const specs = [
    { icon: Ruler, text: formatArea(listing.area_m2) },
    { icon: BedDouble, text: copy.compare.listing.bedrooms(listing.bedrooms) },
    { icon: Bath, text: copy.compare.listing.bathrooms(listing.bathrooms) },
    { icon: CarFront, text: copy.compare.listing.parking(listing.parking) },
    { icon: CalendarDays, text: copy.compare.listing.age(listing.age_years) },
    {
      icon: Dumbbell,
      text: copy.compare.listing.leisure(listing.leisure_count),
    },
    {
      icon: MapPin,
      text: copy.compare.listing.distCenter(
        formatDistance(listing.dist_center_km),
      ),
    },
  ];

  return (
    <Card className="flex-row gap-3 rounded-xl border bg-card p-3 text-card-foreground shadow-sm ring-0 md:gap-5 md:p-4">
      <div className="hidden size-24 shrink-0 rounded-lg bg-accent p-2 md:block">
        <img
          src={`/illustrations/${listing.illustration}.svg`}
          alt={ILLUSTRATION_ALT[listing.kind] ?? listing.title}
          className="h-full w-full"
        />
      </div>
      <div className="flex min-w-0 flex-1 flex-col gap-1.5">
        <div className="flex items-center gap-2">
          <span className="text-sm font-semibold text-muted-foreground tabular-nums">
            {copy.feed.rank(item.rank)}
          </span>
          {previousRank !== undefined ? (
            <RankChange rank={item.rank} previousRank={previousRank} />
          ) : null}
        </div>
        <div>
          <p className="text-lg font-semibold tracking-tight md:text-xl">
            {formatBRL(listing.price_brl)}
          </p>
          <h2 className="text-sm leading-snug font-medium md:text-base">
            {listing.title}
          </h2>
          <p className="text-xs text-muted-foreground md:text-sm">
            {copy.compare.listing.location(listing.neighborhood, listing.city)}
          </p>
        </div>
        <ul className="flex flex-wrap gap-x-3 gap-y-1 text-xs md:text-sm">
          {specs.map((spec) => (
            <li key={spec.text} className="flex items-center gap-1.5">
              <spec.icon
                className="size-4 text-muted-foreground"
                aria-hidden="true"
              />
              {spec.text}
            </li>
          ))}
        </ul>
        {showReasons && item.reasons.length > 0 ? (
          <ul className="flex flex-wrap gap-1.5">
            {item.reasons.slice(0, 4).map((reason) => {
              const positive = reason.contribution > 0;

              return (
                <li
                  key={reason.feature_key}
                  className={cn(
                    "inline-flex items-center gap-1 rounded-md px-2 py-0.5 text-xs font-medium",
                    positive
                      ? "bg-secondary text-secondary-foreground"
                      : "border bg-card text-muted-foreground",
                  )}
                >
                  {positive ? (
                    <Plus className="size-3" aria-hidden="true" />
                  ) : (
                    <Minus className="size-3" aria-hidden="true" />
                  )}
                  {reason.text}
                </li>
              );
            })}
          </ul>
        ) : null}
      </div>
      <div className="flex w-20 shrink-0 flex-col items-center gap-1 text-center md:w-24">
        <ScoreBadge
          score={item.score}
          low={item.interval[0]}
          high={item.interval[1]}
        />
      </div>
    </Card>
  );
}
