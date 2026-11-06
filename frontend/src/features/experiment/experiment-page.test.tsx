import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { http, HttpResponse } from "msw";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";

import { copy } from "@/lib/copy";
import { server } from "@/test/setup";
import { ExperimentPage } from "./experiment-page";

const EMPTY_SUMMARY = {
  run_id: null,
  simulated: false,
  participants: 0,
  rows: [],
  per_participant: [],
};

function renderPage() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={["/experimento"]}>
        <ExperimentPage />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("painel do experimento", () => {
  it("mostra o aviso quando os resultados são simulados", async () => {
    renderPage();

    const alert = await screen.findByRole("alert");

    expect(alert).toHaveTextContent(copy.experiment.simulated);
  });

  it("mostra o estado vazio quando não há resultados", async () => {
    server.use(
      http.get("/api/v1/experiment/summary", () =>
        HttpResponse.json(EMPTY_SUMMARY),
      ),
    );

    renderPage();

    expect(
      await screen.findByText(copy.experiment.empty.title),
    ).toBeInTheDocument();
    expect(
      screen.getByText(copy.experiment.empty.description),
    ).toBeInTheDocument();
    expect(
      screen.queryByText(copy.experiment.curve.title),
    ).not.toBeInTheDocument();
  });
});
