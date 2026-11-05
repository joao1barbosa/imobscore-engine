import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { http, HttpResponse } from "msw";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it } from "vitest";

import { useSessionStore } from "@/stores/session-store";
import { formatBRL } from "@/lib/format";
import { copy } from "@/lib/copy";
import { server } from "@/test/setup";
import { DemoPage } from "./demo-page";

const SESSION = {
  id: "8b7a3d21-4c6e-4a1e-8f2c-000000000000",
  mode: "demo",
  city: "Goiânia",
  purpose: "sale",
  price_min: "200000.00",
  price_max: "600000.00",
  persona_slug: "investidor",
  target_pairs: 3,
  answered: 0,
  status: "comparing",
};

function renderPage() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={["/demo"]}>
        <Routes>
          <Route path="/demo" element={<DemoPage />} />
          <Route
            path="/comparar"
            element={<div data-testid="compare-route" />}
          />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("modo demo", () => {
  beforeEach(() => {
    useSessionStore.getState().reset();
  });

  it("um toque no modo demo chama POST /sessions com os demo_defaults certos", async () => {
    const corpos: Record<string, unknown>[] = [];
    server.use(
      http.post("/api/v1/sessions", async ({ request }) => {
        corpos.push((await request.json()) as Record<string, unknown>);
        return HttpResponse.json(SESSION, { status: 201 });
      }),
    );
    renderPage();

    const card = await screen.findByRole("button", {
      name: copy.demo.chooseLabel("Investidor"),
    });
    await userEvent.click(card);

    await waitFor(() => expect(corpos).toHaveLength(1));
    expect(corpos[0]).toMatchObject({
      mode: "demo",
      city: "Goiânia",
      purpose: "sale",
      price_min: 200000,
      price_max: 600000,
      persona_slug: "investidor",
    });

    await waitFor(() => {
      expect(useSessionStore.getState().sessionId).toBe(SESSION.id);
      expect(useSessionStore.getState().mode).toBe("demo");
    });
    expect(await screen.findByTestId("compare-route")).toBeInTheDocument();
  });

  it("um segundo toque durante o envio não cria outra sessão", async () => {
    let envios = 0;
    let liberar: (() => void) | undefined;
    const pendente = new Promise<void>((resolve) => {
      liberar = resolve;
    });
    server.use(
      http.post("/api/v1/sessions", async () => {
        envios += 1;
        await pendente;
        return HttpResponse.json(SESSION, { status: 201 });
      }),
    );
    renderPage();

    const card = await screen.findByRole("button", {
      name: copy.demo.chooseLabel("Investidor"),
    });
    fireEvent.click(card);
    fireEvent.click(card);

    await waitFor(() => expect(envios).toBe(1));
    await waitFor(() => expect(card).toBeDisabled());

    liberar?.();
    await waitFor(() =>
      expect(useSessionStore.getState().sessionId).toBe(SESSION.id),
    );
    expect(envios).toBe(1);
  });

  it("mostra a faixa de preço da persona", async () => {
    renderPage();

    const expected = copy.demo.range(formatBRL(350000), formatBRL(900000));
    const normalize = (text: string) => text.replace(/\s+/g, " ").trim();

    expect(
      await screen.findByText(
        (_, element) =>
          element?.tagName === "SPAN" &&
          normalize(element.textContent ?? "") === normalize(expected),
      ),
    ).toBeInTheDocument();
  });
});
