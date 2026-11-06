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

const LISTING_C = {
  id: "3f1c0f7e-6c1a-4f0e-9a1b-000000000003",
  code: "GYN-V-0224",
  title: "Apartamento de 3 quartos no Setor Central",
  neighborhood: "Setor Central",
  city: "Goiânia",
  purpose: "sale",
  kind: "apartment",
  price_brl: "424000.00",
  area_m2: 86.7,
  bedrooms: 3,
  bathrooms: 3,
  parking: 2,
  age_years: 29,
  leisure_count: 2,
  dist_center_km: 0.9,
  pet_friendly: true,
  doorman_24h: true,
  illustration: "apartment-2",
};

/** O feed simulado: a mesma lista, em ordens diferentes antes e depois. */
const FEED_BEFORE = [
  {
    listing: LISTING_A,
    score: 68,
    affinity_pct: 68.2,
    interval: [8, 99],
    inspection_delta: 0,
    reasons: [],
    rank: 1,
  },
  {
    listing: LISTING_B,
    score: 55,
    affinity_pct: 55.4,
    interval: [4, 97],
    inspection_delta: 0,
    reasons: [],
    rank: 2,
  },
  {
    listing: LISTING_C,
    score: 71,
    affinity_pct: 71.1,
    interval: [10, 100],
    inspection_delta: 0,
    reasons: [],
    rank: 3,
  },
];

const FEED_AFTER = [
  {
    listing: LISTING_C,
    score: 74,
    affinity_pct: 74.3,
    interval: [19, 100],
    inspection_delta: 0,
    reasons: [
      {
        feature_key: "dist_center",
        text: "perto do centro",
        contribution: 0.31,
      },
      {
        feature_key: "bedrooms",
        text: "perto de 3 quartos",
        contribution: 0.12,
      },
      {
        feature_key: "log_price",
        text: "mais caro que o típico",
        contribution: -0.08,
      },
    ],
    rank: 1,
  },
  {
    listing: LISTING_A,
    score: 79,
    affinity_pct: 79.6,
    interval: [21, 100],
    inspection_delta: 0,
    reasons: [
      {
        feature_key: "dist_center",
        text: "perto do centro",
        contribution: 0.22,
      },
      {
        feature_key: "leisure",
        text: "mais itens de lazer",
        contribution: 0.09,
      },
    ],
    rank: 2,
  },
  {
    listing: LISTING_B,
    score: 62,
    affinity_pct: 62.8,
    interval: [4, 99],
    inspection_delta: 0,
    reasons: [
      { feature_key: "is_house", text: "é casa", contribution: 0.15 },
      {
        feature_key: "log_price",
        text: "mais caro que o típico",
        contribution: -0.11,
      },
    ],
    rank: 3,
  },
];

const PAIR = {
  position: 1,
  total: 25,
  listing_a: LISTING_A,
  listing_b: LISTING_B,
};

/** As doze características do motor, na ordem de `FEATURE_KEYS`. */
const FEATURES = [
  {
    key: "log_price",
    label: "Preço",
    text_high: "mais caro que o típico",
    text_low: "mais barato que o típico",
  },
  {
    key: "log_area",
    label: "Área",
    text_high: "mais espaçoso",
    text_low: "mais compacto",
  },
  {
    key: "bedrooms",
    label: "Quartos",
    text_high: "mais quartos",
    text_low: "menos quartos",
  },
  {
    key: "bedrooms_sq",
    label: "Distância de 3 quartos",
    text_high: "longe de 3 quartos",
    text_low: "perto de 3 quartos",
  },
  {
    key: "bathrooms",
    label: "Banheiros",
    text_high: "mais banheiros",
    text_low: "menos banheiros",
  },
  {
    key: "parking",
    label: "Vagas",
    text_high: "mais vagas",
    text_low: "menos vagas",
  },
  {
    key: "dist_center",
    label: "Distância do centro",
    text_high: "longe do centro",
    text_low: "perto do centro",
  },
  {
    key: "age",
    label: "Idade",
    text_high: "mais antigo",
    text_low: "mais novo",
  },
  {
    key: "is_house",
    label: "Casa",
    text_high: "é casa",
    text_low: "é apartamento",
  },
  {
    key: "leisure",
    label: "Lazer",
    text_high: "mais lazer",
    text_low: "menos lazer",
  },
  {
    key: "pet",
    label: "Aceita pet",
    text_high: "aceita pet",
    text_low: "não aceita pet",
  },
  {
    key: "doorman",
    label: "Portaria 24 h",
    text_high: "tem portaria 24 h",
    text_low: "sem portaria",
  },
];

/** Os pesos da demo: a priori da persona de Família e a posteriori. */
const WEIGHTS = [
  { key: "log_price", prior: -1, post: -0.91, lo: -2.53, hi: 0.63 },
  { key: "log_area", prior: 0.8, post: 0.69, lo: -0.89, hi: 2.22 },
  { key: "bedrooms", prior: 0.6, post: 0.59, lo: -1.09, hi: 2.27 },
  { key: "bedrooms_sq", prior: -0.4, post: -0.39, lo: -2.02, hi: 1.29 },
  { key: "bathrooms", prior: 0.4, post: 0.13, lo: -1.45, hi: 1.76 },
  { key: "parking", prior: 0.5, post: 0.25, lo: -1.35, hi: 1.87 },
  { key: "dist_center", prior: -0.3, post: -1.13, lo: -2.54, hi: 0.19 },
  { key: "age", prior: -0.3, post: -0.22, lo: -1.81, hi: 1.37 },
  { key: "is_house", prior: 0.5, post: 0.63, lo: -0.86, hi: 2.14 },
  { key: "leisure", prior: 0.4, post: 0.04, lo: -1.46, hi: 1.47 },
  { key: "pet", prior: 0.3, post: 0.74, lo: -0.78, hi: 2.3 },
  { key: "doorman", prior: 0.4, post: 0.77, lo: -0.76, hi: 2.27 },
];

const POSTERIOR = {
  n_comparisons: 3,
  weights: WEIGHTS.map((weight) => {
    const feature = FEATURES.find((item) => item.key === weight.key);
    return {
      feature_key: weight.key,
      label: feature?.label ?? weight.key,
      prior_mean: weight.prior,
      prior_sd: 1,
      post_mean: weight.post,
      post_sd: 0.62,
      ci_low: weight.lo,
      ci_high: weight.hi,
    };
  }),
  diagnostics: {
    accept_rate: 0.27,
    rhat_max: 1.01,
    ess_min: 612,
    step_size: 0.42,
    elapsed_ms: 190,
    ok: true,
  },
};

/** Quatro cadeias de 250 pontos, sem aleatoriedade. */
function traceChains(): number[][] {
  return [0, 1, 2, 3].map((chain) =>
    Array.from({ length: 250 }, (_, index) => {
      const base = Math.sin((index + chain * 12) / 9) * 0.8;
      const drift = (index / 250) * (chain - 1.5) * 0.2;
      return Number((base + drift).toFixed(4));
    }),
  );
}

const SESSION_ID = "8b7a3d21-4c6e-4a1e-8f2c-000000000000";

/** A rodada simulada do experimento, com treino de 3, 5 e 10 pares. */
const EXPERIMENT_ROWS = [
  {
    method: "bayes",
    acc: [0.66, 0.69, 0.72],
    sd: [0.07, 0.06, 0.06],
    ll: [0.64, 0.61, 0.57],
  },
  {
    method: "mle",
    acc: [0.55, 0.6, 0.68],
    sd: [0.09, 0.08, 0.06],
    ll: [0.86, 0.78, 0.63],
  },
  {
    method: "persona",
    acc: [0.63, 0.63, 0.63],
    sd: [0.07, 0.07, 0.07],
    ll: [0.66, 0.66, 0.66],
  },
  {
    method: "equal",
    acc: [0.58, 0.58, 0.58],
    sd: [0.08, 0.08, 0.08],
    ll: [0.69, 0.69, 0.69],
  },
];

const EXPERIMENT_N_TRAIN = [3, 5, 10];

const PARTICIPANT_ACC = [
  [0.78, 0.62, 0.7, 0.6],
  [0.72, 0.58, 0.64, 0.56],
  [0.64, 0.6, 0.66, 0.62],
  [0.7, 0.62, 0.58, 0.54],
  [0.66, 0.54, 0.6, 0.58],
  [0.68, 0.64, 0.62, 0.56],
];

const EXPERIMENT_METHODS = ["bayes", "mle", "persona", "equal"] as const;

const EXPERIMENT_SUMMARY = {
  run_id: "b7f1c0a4-2f1e-4c3a-9d2b-000000000001",
  simulated: true,
  participants: PARTICIPANT_ACC.length,
  rows: EXPERIMENT_ROWS.flatMap((row) =>
    EXPERIMENT_N_TRAIN.map((nTrain, index) => ({
      method: row.method,
      n_train: nTrain,
      acc_mean: row.acc[index],
      acc_sd: row.sd[index],
      ll_mean: row.ll[index],
      ll_sd: 0.05,
      n_participants: PARTICIPANT_ACC.length,
    })),
  ),
  per_participant: PARTICIPANT_ACC.flatMap((values, index) =>
    EXPERIMENT_METHODS.map((method, methodIndex) => ({
      participant_code: `P${String(index + 1).padStart(2, "0")}`,
      method,
      acc_mean: values[methodIndex],
    })),
  ),
};

export const handlers: HttpHandler[] = [
  http.get("/api/v1/meta/options", () =>
    HttpResponse.json({ segments: [SEGMENT] }),
  ),

  http.get("/api/v1/meta/personas", () => HttpResponse.json(PERSONAS)),

  http.get("/api/v1/meta/features", () => HttpResponse.json(FEATURES)),

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

  http.get("/api/v1/sessions/:sessionId/feed", ({ request }) => {
    const at = Number(new URL(request.url).searchParams.get("at") ?? 0);
    const items = at > 0 ? FEED_AFTER : FEED_BEFORE;
    return HttpResponse.json({
      items,
      next_offset: null,
      method: "bayes",
      n_comparisons: at,
    });
  }),

  http.get("/api/v1/sessions/:sessionId/posterior", () =>
    HttpResponse.json(POSTERIOR),
  ),

  http.get("/api/v1/sessions/:sessionId/posterior/trace", ({ request }) => {
    const feature =
      new URL(request.url).searchParams.get("feature") ?? "dist_center";
    return HttpResponse.json({
      feature_key: feature,
      chains: traceChains(),
    });
  }),

  http.get("/api/v1/experiment/summary", () =>
    HttpResponse.json(EXPERIMENT_SUMMARY),
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
