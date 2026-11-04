import {
  Bath,
  BedDouble,
  CalendarDays,
  CarFront,
  Check,
  Dumbbell,
  MapPin,
  PawPrint,
  Ruler,
  ShieldCheck,
} from "lucide-react";

import type { ListingCard as ListingCardType } from "@/api/client";
import { cn } from "@/lib/cn";
import { copy } from "@/lib/copy";
import { formatArea, formatBRL, formatDistance } from "@/lib/format";

type ListingChoiceCardProps = {
  listing: ListingCardType;
  shortcut: "←" | "→";
  disabled: boolean;
  state: "idle" | "chosen" | "dimmed";
  onChoose: () => void;
};

const ILLUSTRATION_ALT = copy.compare.listing.illustrationAlt as Record<
  string,
  string
>;

/** O cartão de um imóvel do par. O cartão inteiro é o botão da escolha. */
export function ListingChoiceCard({
  listing,
  shortcut,
  disabled,
  state,
  onChoose,
}: ListingChoiceCardProps) {
  const price = formatBRL(listing.price_brl);
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
      wide: true,
    },
  ];

  return (
    <button
      type="button"
      disabled={disabled}
      onClick={onChoose}
      aria-label={copy.compare.chooseLabel(listing.title, price)}
      className={cn(
        "group relative flex w-full gap-3 overflow-hidden rounded-xl border bg-card p-3 text-left text-card-foreground shadow-sm transition focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring md:flex-col md:gap-0 md:p-0",
        disabled
          ? "cursor-not-allowed"
          : "cursor-pointer hover:-translate-y-0.5 hover:border-primary hover:shadow-md",
        state === "chosen" && "border-primary ring-2 ring-primary",
        state === "dimmed" && "opacity-50",
      )}
    >
      <div className="size-20 shrink-0 rounded-lg bg-accent p-2 md:h-44 md:w-full md:rounded-none md:p-6">
        <img
          src={`/illustrations/${listing.illustration}.svg`}
          alt={ILLUSTRATION_ALT[listing.kind] ?? listing.title}
          className="h-full w-full"
        />
      </div>
      <div className="flex min-w-0 flex-1 flex-col gap-1.5 md:gap-3 md:p-5">
        <div>
          <p className="text-xl font-semibold tracking-tight md:text-2xl">
            {price}
          </p>
          <h2 className="text-sm leading-snug font-medium md:text-base">
            {listing.title}
          </h2>
          <p className="text-xs text-muted-foreground md:text-sm">
            {copy.compare.listing.location(listing.neighborhood, listing.city)}
          </p>
        </div>
        <ul className="grid grid-cols-2 gap-x-2 gap-y-1 text-xs md:gap-y-2 md:text-sm">
          {specs.map((spec) => (
            <li
              key={spec.text}
              className={cn(
                "flex items-center gap-1.5",
                spec.wide && "col-span-2",
              )}
            >
              <spec.icon
                className="size-4 text-muted-foreground"
                aria-hidden="true"
              />
              {spec.text}
            </li>
          ))}
        </ul>
        <div className="flex min-h-6 flex-wrap gap-1.5">
          {listing.pet_friendly ? (
            <span className="inline-flex items-center gap-1 rounded-md bg-secondary px-2 py-0.5 text-xs font-medium text-secondary-foreground">
              <PawPrint className="size-3.5" aria-hidden="true" />
              {copy.compare.listing.petFriendly}
            </span>
          ) : null}
          {listing.doorman_24h ? (
            <span className="inline-flex items-center gap-1 rounded-md bg-secondary px-2 py-0.5 text-xs font-medium text-secondary-foreground">
              <ShieldCheck className="size-3.5" aria-hidden="true" />
              {copy.compare.listing.doorman}
            </span>
          ) : null}
        </div>
      </div>
      {state === "chosen" ? (
        <span className="absolute top-3 right-3 grid size-7 place-items-center rounded-full bg-primary text-primary-foreground">
          <Check className="size-4" aria-hidden="true" />
        </span>
      ) : (
        <kbd className="absolute top-3 right-3 hidden rounded-md border bg-card px-2 py-0.5 font-sans text-sm font-medium text-muted-foreground md:block">
          {shortcut}
        </kbd>
      )}
    </button>
  );
}
