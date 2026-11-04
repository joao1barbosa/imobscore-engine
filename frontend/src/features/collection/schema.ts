import { z } from "zod";

import type { SegmentOptions } from "@/api/client";
import { copy } from "@/lib/copy";

export const COLLECTION_CITY = "Goiânia";
export const COLLECTION_PURPOSE = "sale";

export const PERSONA_SLUGS = ["familia", "investidor", "estudante"] as const;

export type PersonaSlug = (typeof PERSONA_SLUGS)[number];

/** A grade do slider e dos campos de preço: R$ 10 mil. */
export const PRICE_STEP = 10_000;

/** O menor preço do slider, arredondado para a grade de R$ 10 mil. */
export function sliderFloor(segment: SegmentOptions): number {
  return Math.floor(segment.price_floor / PRICE_STEP) * PRICE_STEP;
}

/** O maior preço do slider, arredondado para a grade de R$ 10 mil. */
export function sliderCeiling(segment: SegmentOptions): number {
  return Math.ceil(segment.price_ceiling / PRICE_STEP) * PRICE_STEP;
}

const baseSchema = z.object({
  consent: z.literal(true, { error: copy.collection.validation.consent }),
  priceMin: z
    .number()
    .positive({ error: copy.collection.validation.priceRequired }),
  priceMax: z
    .number()
    .positive({ error: copy.collection.validation.priceRequired }),
  personaSlug: z.enum(PERSONA_SLUGS, {
    error: copy.collection.validation.persona,
  }),
});

/**
 * O formulário da coleta: o consentimento, a faixa de preço e a persona.
 * A cidade e a finalidade são fixas, e o preço tem de caber no catálogo.
 */
export const collectionFormSchema = (segment: SegmentOptions) =>
  baseSchema.superRefine((values, ctx) => {
    if (values.priceMin >= values.priceMax) {
      ctx.addIssue({
        code: "custom",
        path: ["priceMax"],
        message: copy.collection.validation.priceOrder,
      });
    }
    if (values.priceMax < segment.price_floor) {
      ctx.addIssue({
        code: "custom",
        path: ["priceMax"],
        message: copy.collection.validation.priceEmpty,
      });
    }
  });

/** Os valores do formulário, como o React Hook Form os guarda. */
export type CollectionFormValues = {
  consent: boolean;
  priceMin: number;
  priceMax: number;
  personaSlug?: PersonaSlug;
};
