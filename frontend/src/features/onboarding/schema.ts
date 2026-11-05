import { z } from "zod";

import type { SegmentOptions } from "@/api/client";
import { PERSONA_SLUGS, type PersonaSlug } from "@/features/collection/schema";
import { copy } from "@/lib/copy";

/** O passo 1: a faixa de preço tem de caber no catálogo. */
export const step1Schema = (segment: SegmentOptions) =>
  z
    .object({
      priceMin: z
        .number()
        .positive({ error: copy.collection.validation.priceRequired }),
      priceMax: z
        .number()
        .positive({ error: copy.collection.validation.priceRequired }),
    })
    .superRefine((values, ctx) => {
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

/** O passo 2: a persona é obrigatória. */
export const step2Schema = z.object({
  personaSlug: z.enum(PERSONA_SLUGS, {
    error: copy.collection.validation.persona,
  }),
});

/** Os valores do formulário, como o React Hook Form os guarda. */
export type OnboardingValues = {
  priceMin: number;
  priceMax: number;
  personaSlug?: PersonaSlug;
};
