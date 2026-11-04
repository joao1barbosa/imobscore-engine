import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { http, HttpResponse } from "msw";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it } from "vitest";

import { useSessionStore } from "@/stores/session-store";
import { server } from "@/test/setup";
import { copy } from "@/lib/copy";
import { ComparePanel } from "./compare-panel";

const SESSION_ID = "8b7a3d21-4c6e-4a1e-8f2c-000000000000";

function renderPanel() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <ComparePanel sessionId={SESSION_ID} onDone={() => undefined} />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("painel de comparação", () => {
  beforeEach(() => {
    useSessionStore.getState().reset();
  });

  it("escolhe A com o clique e com a seta para a esquerda", async () => {
    const escolhas: string[] = [];
    server.use(
      http.post(
        "/api/v1/sessions/:sessionId/comparisons/:position",
        async ({ request }) => {
          const body = (await request.json()) as { chosen: string };
          escolhas.push(body.chosen);
          return HttpResponse.json({
            answered: escolhas.length,
            total: 25,
            done: false,
            diagnostics: null,
          });
        },
      ),
    );
    renderPanel();

    const card = await screen.findByRole("button", {
      name: /Escolher Apartamento de 3 quartos/,
    });
    await userEvent.click(card);
    await waitFor(() => expect(escolhas).toEqual(["A"]));

    await userEvent.keyboard("{ArrowLeft}");
    await waitFor(() => expect(escolhas).toEqual(["A", "A"]));
  });

  it("desabilita os cartões durante o envio", async () => {
    let liberar: () => void = () => undefined;
    server.use(
      http.post(
        "/api/v1/sessions/:sessionId/comparisons/:position",
        async () => {
          await new Promise<void>((resolve) => {
            liberar = resolve;
          });
          return HttpResponse.json({
            answered: 1,
            total: 25,
            done: false,
            diagnostics: null,
          });
        },
      ),
    );
    renderPanel();

    const card = await screen.findByRole("button", {
      name: /Escolher Apartamento de 3 quartos/,
    });
    await userEvent.click(card);

    await waitFor(() => expect(card).toBeDisabled());
    expect(screen.getByRole("status")).toHaveTextContent(copy.compare.sending);

    liberar();
    await waitFor(() => expect(card).toBeEnabled());
  });
});
