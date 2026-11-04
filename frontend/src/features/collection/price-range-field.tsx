import { useState } from "react";
import { useFormContext } from "react-hook-form";
import { CircleAlert } from "lucide-react";

import { Input } from "@/components/ui/input";
import { Slider } from "@/components/ui/slider";
import { copy } from "@/lib/copy";
import { formatBRL } from "@/lib/format";
import { PRICE_STEP, type CollectionFormValues } from "./schema";

type PriceRangeFieldProps = {
  floor: number;
  ceiling: number;
  disabled: boolean;
};

/** O valor digitado, arredondado para a grade de R$ 10 mil e dentro do limite. */
function snap(value: number, max: number): number {
  const stepped = Math.round(value / PRICE_STEP) * PRICE_STEP;
  return Math.min(max, stepped);
}

/**
 * A faixa de preço: o slider e os dois campos ficam sincronizados, em passos
 * de R$ 10 mil. O texto do limite mostra os valores reais do catálogo.
 */
export function PriceRangeField({
  floor,
  ceiling,
  disabled,
}: PriceRangeFieldProps) {
  const form = useFormContext<CollectionFormValues>();
  const priceMin = form.watch("priceMin");
  const priceMax = form.watch("priceMax");
  const minError = form.formState.errors.priceMin?.message;
  const maxError = form.formState.errors.priceMax?.message;

  const min = Math.floor(floor / PRICE_STEP) * PRICE_STEP;
  const max = Math.ceil(ceiling / PRICE_STEP) * PRICE_STEP;

  const [draftMin, setDraftMin] = useState<string | null>(null);
  const [draftMax, setDraftMax] = useState<string | null>(null);

  const setPrice = (field: "priceMin" | "priceMax", text: string) => {
    const digits = text.replace(/\D/g, "");
    form.setValue(field, snap(digits ? Number(digits) : 0, max));
  };

  return (
    <div className="flex flex-col gap-3">
      <span className="text-sm font-medium">{copy.collection.price.label}</span>
      <Slider
        value={[priceMin, priceMax]}
        min={min}
        max={max}
        step={PRICE_STEP}
        disabled={disabled}
        onValueChange={(value) => {
          const [nextMin, nextMax] = value as number[];
          form.setValue("priceMin", nextMin);
          form.setValue("priceMax", nextMax);
        }}
        className="h-6 [&_[data-slot=slider-thumb]]:size-5 [&_[data-slot=slider-thumb]]:border-2 [&_[data-slot=slider-thumb]]:border-primary [&_[data-slot=slider-thumb]]:bg-card [&_[data-slot=slider-thumb]]:shadow [&_[data-slot=slider-track]]:h-2 [&_[data-slot=slider-track]]:bg-secondary"
      />
      <div className="flex gap-3">
        <div className="flex min-w-0 flex-1 flex-col gap-1.5">
          <label htmlFor="price-min" className="text-sm text-muted-foreground">
            {copy.collection.price.min}
          </label>
          <Input
            id="price-min"
            inputMode="numeric"
            disabled={disabled}
            value={draftMin ?? formatBRL(priceMin)}
            aria-invalid={Boolean(minError)}
            onFocus={() => setDraftMin(String(priceMin))}
            onBlur={() => setDraftMin(null)}
            onChange={(event) => {
              setDraftMin(event.target.value);
              setPrice("priceMin", event.target.value);
            }}
            className="h-11 min-w-0 rounded-md bg-card px-3 text-base tabular-nums md:text-base"
          />
        </div>
        <div className="flex min-w-0 flex-1 flex-col gap-1.5">
          <label htmlFor="price-max" className="text-sm text-muted-foreground">
            {copy.collection.price.max}
          </label>
          <Input
            id="price-max"
            inputMode="numeric"
            disabled={disabled}
            value={draftMax ?? formatBRL(priceMax)}
            aria-invalid={Boolean(maxError)}
            onFocus={() => setDraftMax(String(priceMax))}
            onBlur={() => setDraftMax(null)}
            onChange={(event) => {
              setDraftMax(event.target.value);
              setPrice("priceMax", event.target.value);
            }}
            className="h-11 min-w-0 rounded-md bg-card px-3 text-base tabular-nums md:text-base"
          />
        </div>
      </div>
      {maxError || minError ? (
        <p className="flex items-center gap-1.5 text-sm font-medium text-destructive">
          <CircleAlert className="size-4" aria-hidden="true" />
          {maxError ?? minError}
        </p>
      ) : (
        <p className="text-sm text-muted-foreground">
          {copy.collection.price.limits(formatBRL(floor), formatBRL(ceiling))}
        </p>
      )}
    </div>
  );
}
