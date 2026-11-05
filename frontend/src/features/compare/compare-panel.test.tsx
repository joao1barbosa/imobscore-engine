import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { delay, http, HttpResponse } from "msw";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it } from "vitest";

import { useSessionStore } from "@/stores/session-store";
import { server } from "@/test/setup";
import { copy } from "@/lib/copy";
import { ComparePanel } from "./compare-panel";

const SESSION_ID = "8b7a3d21-4c6e-4a1e-8f2c-000000000000";

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
  ...LISTING_A,
  id: "3f1c0f7e-6c1a-4f0e-9a1b-000000000002",
  code: "GYN-V-0249",
  title: "Casa de 4 quartos no Jardim América",
  neighborhood: "Jardim América",
  kind: "house",
  illustration: "house-1",
};

const LISTING_C = {
  ...LISTING_A,
  id: "3f1c0f7e-6c1a-4f0e-9a1b-000000000003",
  code: "GYN-V-0224",
  title: "Apartamento de 2 quartos no Setor Central",
  neighborhood: "Setor Central",
  illustration: "apartment-2",
};

const PAIR_ONE = {
  position: 1,
  total: 25,
  listing_a: LISTING_A,
  listing_b: LISTING_B,
};

const PAIR_TWO = {
  position: 2,
  total: 25,
  listing_a: LISTING_C,
  listing_b: LISTING_B,
};

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

  it("next-pair com 502 mostra o erro com o botão de tentar de novo", async () => {
    server.use(
      http.get(
        "/api/v1/sessions/:sessionId/next-pair",
        () => new HttpResponse(null, { status: 502 }),
      ),
    );
    renderPanel();

    expect(
      await screen.findByText(copy.compare.loadError.title),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: copy.common.retry }),
    ).toBeInTheDocument();
    expect(
      screen.queryByText(copy.common.apiErrors.session_not_found),
    ).not.toBeInTheDocument();
  });

  it("depois de um erro, tentar de novo volta ao par", async () => {
    let chamadas = 0;
    server.use(
      http.get("/api/v1/sessions/:sessionId/next-pair", () => {
        chamadas += 1;
        if (chamadas === 1) {
          return new HttpResponse(null, { status: 502 });
        }
        return undefined;
      }),
    );
    renderPanel();

    await userEvent.click(
      await screen.findByRole("button", { name: copy.common.retry }),
    );

    expect(
      await screen.findByRole("button", {
        name: /Escolher Apartamento de 3 quartos/,
      }),
    ).toBeInTheDocument();
  });

  it("next-pair com 404 session_not_found mantém a mensagem sem botão", async () => {
    server.use(
      http.get("/api/v1/sessions/:sessionId/next-pair", () =>
        HttpResponse.json(
          {
            detail: {
              code: "session_not_found",
              message: "Não encontramos esta sessão.",
            },
          },
          { status: 404 },
        ),
      ),
    );
    renderPanel();

    expect(
      await screen.findByText(copy.common.apiErrors.session_not_found),
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: copy.common.retry }),
    ).not.toBeInTheDocument();
  });

  it("mantém os cartões desabilitados até o próximo par chegar", async () => {
    let chamadas = 0;
    let respostas = 0;
    server.use(
      http.get("/api/v1/sessions/:sessionId/next-pair", async () => {
        chamadas += 1;
        if (chamadas === 1) {
          return HttpResponse.json(PAIR_ONE);
        }
        await delay(300);
        return HttpResponse.json(PAIR_TWO);
      }),
      http.post(
        "/api/v1/sessions/:sessionId/comparisons/:position",
        async () => {
          respostas += 1;
          return HttpResponse.json({
            answered: respostas,
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

    // O próximo par está atrasado: os cartões ficam desabilitados.
    await waitFor(() => expect(card).toBeDisabled());
    await userEvent.click(card);
    expect(respostas).toBe(1);

    // Quando o par 2 chega, os cartões voltam a aceitar a escolha.
    expect(
      await screen.findByText(copy.compare.progress(2, 25)),
    ).toBeInTheDocument();
    const proximo = await screen.findByRole("button", {
      name: /Escolher Apartamento de 2 quartos/,
    });
    await waitFor(() => expect(proximo).toBeEnabled());
    expect(respostas).toBe(1);
  });
});
