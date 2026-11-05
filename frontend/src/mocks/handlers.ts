import { http, HttpResponse, type HttpHandler } from "msw";

// A API simulada dos testes. Os dados são do catálogo de demonstração.
const SEGMENT = {
  city: "Goiânia",
  purpose: "sale",
  price_floor: 147000,
  price_ceiling: 1358000,
};

const PERSONAS = [
  {
    slug: "familia",
    name: "Família",
    description:
      "Prioriza espaço, quartos e vagas, mesmo pagando um pouco mais.",
    demo_defaults: {
      city: "Goiânia",
      purpose: "sale",
      price_min: 350000,
      price_max: 900000,
    },
  },
  {
    slug: "investidor",
    name: "Investidor",
    description:
      "Busca bom preço e localização, pensando em alugar ou revender.",
    demo_defaults: {
      city: "Goiânia",
      purpose: "sale",
      price_min: 200000,
      price_max: 600000,
    },
  },
  {
    slug: "estudante",
    name: "Estudante",
    description: "Quer pagar pouco e morar perto do centro.",
    demo_defaults: {
      city: "Goiânia",
      purpose: "sale",
      price_min: 150000,
      price_max: 350000,
    },
  },
];

const LISTING_A = {
  id: "3f1c0f7e-6c1a-4f0e-9a1b-000000000001",
  code: "GYN-V-0133",
  title: "Apartamento de 3 quartos no Setor Bueno",
  neighborhood: "Setor Bueno",
  city: "Goiânia",
  purpose: "sale",
  kind: "apartment",
  price_brl: "512000.00",
  area_m2: 98.6,
  bedrooms: 3,
  bathrooms: 2,
  parking: 2,
  dist_center_km: 4.2,
  age_years: 8,
  leisure_count: 2,
  pet_friendly: true,
  doorman_24h: true,
  illustration: "apartment-1",
};

const LISTING_B = {
  id: "3f1c0f7e-6c1a-4f0e-9a1b-000000000002",
  code: "GYN-V-0249",
  title: "Casa de 4 quartos no Jardim América",
  neighborhood: "Jardim América",
  city: "Goiânia",
  purpose: "sale",
  kind: "house",
  price_brl: "798000.00",
  area_m2: 168.2,
  bedrooms: 4,
  bathrooms: 3,
  parking: 3,
  dist_center_km: 5.8,
  age_years: 15,
  leisure_count: 0,
  pet_friendly: true,
  doorman_24h: false,
  illustration: "house-1",
};

const PAIR = {
  position: 1,
  total: 25,
  listing_a: LISTING_A,
  listing_b: LISTING_B,
};

const SESSION_ID = "8b7a3d21-4c6e-4a1e-8f2c-000000000000";

export const handlers: HttpHandler[] = [
  http.get("/api/v1/meta/options", () =>
    HttpResponse.json({ segments: [SEGMENT] }),
  ),

  http.get("/api/v1/meta/personas", () => HttpResponse.json(PERSONAS)),

  http.post("/api/v1/sessions", async ({ request }) => {
    const body = (await request.json()) as {
      mode?: string;
      price_min?: number;
      price_max?: number;
      persona_slug?: string;
    };
    const mode = body.mode ?? "collection";
    const targetPairs = mode === "collection" ? 25 : mode === "demo" ? 3 : 8;

    return HttpResponse.json(
      {
        id: SESSION_ID,
        mode,
        city: SEGMENT.city,
        purpose: SEGMENT.purpose,
        price_min: String(body.price_min ?? 350000),
        price_max: String(body.price_max ?? 900000),
        persona_slug: body.persona_slug ?? "familia",
        target_pairs: targetPairs,
        answered: 0,
        status: "comparing",
      },
      { status: 201 },
    );
  }),

  http.get("/api/v1/sessions/:sessionId", () =>
    HttpResponse.json({
      id: SESSION_ID,
      mode: "collection",
      city: SEGMENT.city,
      purpose: SEGMENT.purpose,
      price_min: "350000.00",
      price_max: "900000.00",
      persona_slug: "familia",
      target_pairs: 25,
      answered: 0,
      status: "comparing",
    }),
  ),

  http.get("/api/v1/sessions/:sessionId/next-pair", () =>
    HttpResponse.json(PAIR),
  ),

  http.post("/api/v1/sessions/:sessionId/comparisons/:position", () =>
    HttpResponse.json({
      answered: 1,
      total: 25,
      done: false,
      diagnostics: null,
    }),
  ),
];
