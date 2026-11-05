import { MapPin } from "lucide-react";

import type { SegmentOptions } from "@/api/client";
import { PriceRangeField } from "@/features/collection/price-range-field";
import { copy } from "@/lib/copy";

type StepPriceProps = {
  segment: SegmentOptions;
  disabled: boolean;
};

/** O passo 1: o aviso fixo do segmento e a faixa de preço. */
export function StepPrice({ segment, disabled }: StepPriceProps) {
  return (
    <section className="flex flex-col gap-4 rounded-xl border bg-card p-4 shadow-sm md:p-6">
      <p className="flex items-center gap-2 rounded-lg bg-muted p-3 text-sm font-medium">
        <MapPin className="size-4 text-primary" aria-hidden="true" />
        {copy.collection.segment}
      </p>
      <PriceRangeField
        floor={segment.price_floor}
        ceiling={segment.price_ceiling}
        disabled={disabled}
      />
    </section>
  );
}
