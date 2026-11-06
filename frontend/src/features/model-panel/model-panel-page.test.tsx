import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { http, HttpResponse } from "msw";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { useSessionStore } from "@/stores/session-store";
import { server } from "@/test/setup";
import { copy } from "@/lib/copy";
import { ModelPanelPage } from "./model-panel-page";

const SESSION = {
  id: "8b7a3d21-4c6e-4a1e-8f2c-000000000000",
  mode: "demo",
  city: "Goiânia",
  purpose: "sale",
  price_min: "350000.00",
  price_max: "900000.00",
  persona_slug: "familia",
  target_pairs: 3,
  answered: 3,
  status: "done",
};

const FEATURE_LABELS = [
  "Preço",
  "Área",
  "Quartos",
  "Distância de 3 quartos",
  "Banheiros",
  "Vagas",
  "Distância do centro",
  "Idade",
  "Casa",
  "Lazer",
  "Aceita pet",
  "Portaria 24 h",
];

const WEIGHT = {
  feature_key: "dist_center",
  label: "Distância do centro",
  prior_mean: -0.3,
  prior_sd: 1,
  post_mean: -1.13,
  post_sd: 0.62,
  ci_low: -2.54,
  ci_high: 0.19,
};

const POSTERIOR_ALERT = {
  n_comparisons: 3,
  weights: [WEIGHT],
  diagnostics: {
    accept_rate: 0.09,
    rhat_max: 1.12,
    ess_min: 180,
    step_size: 0.42,
    elapsed_ms: 190,
    ok: false,
  },
};

function renderPage() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={["/modelo"]}>
        <ModelPanelPage />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

beforeEach(() => {
  useSessionStore.getState().reset();
});

afterEach(() => {
  vi.restoreAllMocks();
});

describe("painel do modelo", () => {
  it("renderiza as 12 linhas de pesos com os dados do MSW", async () => {
    server.use(
      http.get("/api/v1/sessions/:sessionId", () => HttpResponse.json(SESSION)),
    );
    useSessionStore.setState({ sessionId: SESSION.id, mode: "demo" });

    renderPage();

    expect(
      await screen.findByText(copy.modelPanel.weights.title),
    ).toBeInTheDocument();

    await userEvent.click(
      screen.getByText(copy.modelPanel.weights.tableToggle),
    );

    const table = screen.getByRole("table");
    const rows = within(table).getAllByRole("row");

    expect(rows).toHaveLength(FEATURE_LABELS.length + 1);

    for (const label of FEATURE_LABELS) {
      expect(within(table).getByText(label)).toBeInTheDocument();
    }
  });

  it("mostra o alerta quando os diagnósticos ficam fora da faixa", async () => {
    server.use(
      http.get("/api/v1/sessions/:sessionId", () => HttpResponse.json(SESSION)),
      http.get("/api/v1/sessions/:sessionId/posterior", () =>
        HttpResponse.json(POSTERIOR_ALERT),
      ),
    );
    useSessionStore.setState({ sessionId: SESSION.id, mode: "demo" });

    renderPage();

    const alert = await screen.findByRole("alert");

    expect(alert).toHaveTextContent(copy.modelPanel.diagnostics.alert);
    expect(
      screen.queryByText(copy.modelPanel.diagnostics.ok),
    ).not.toBeInTheDocument();
  });
});
