import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { http, HttpResponse } from "msw";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it } from "vitest";

import type { SegmentOptions } from "@/api/client";
import { useSessionStore } from "@/stores/session-store";
import { server } from "@/test/setup";
import { copy } from "@/lib/copy";
import { OnboardingPage } from "./onboarding-page";
import { step1Schema, step2Schema } from "./schema";

const SEGMENT: SegmentOptions = {
  city: "Goiânia",
  purpose: "sale",
  price_floor: 147000,
  price_ceiling: 1358000,
};

const SESSION = {
  id: "8b7a3d21-4c6e-4a1e-8f2c-000000000000",
  mode: "product",
  city: "Goiânia",
  purpose: "sale",
  price_min: "140000.00",
  price_max: "900000.00",
  persona_slug: "familia",
  target_pairs: 8,
  answered: 0,
  status: "comparing",
};

function renderPage() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={["/comecar"]}>
        <Routes>
          <Route path="/comecar" element={<OnboardingPage />} />
          <Route
            path="/comparar"
            element={<div>{copy.compare.question}</div>}
          />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

async function waitForStep1() {
  await screen.findByRole("button", { name: copy.onboarding.next });
}

async function typePriceMax(value: string) {
  const input = screen.getByLabelText(copy.collection.price.max);
  await userEvent.click(input);
  await userEvent.clear(input);
  await userEvent.type(input, value);
}

describe("onboarding", () => {
  beforeEach(() => {
    useSessionStore.getState().reset();
  });

  it("mensagens de erro dos schemas", () => {
    const order = step1Schema(SEGMENT).safeParse({
      priceMin: 500000,
      priceMax: 400000,
    });
    expect(order.success).toBe(false);
    expect(
      order.success ? [] : order.error.issues.map((issue) => issue.message),
    ).toContain(copy.collection.validation.priceOrder);

    const empty = step1Schema(SEGMENT).safeParse({
      priceMin: 100000,
      priceMax: 120000,
    });
    expect(empty.success).toBe(false);
    expect(
      empty.success ? [] : empty.error.issues.map((issue) => issue.message),
    ).toContain(copy.collection.validation.priceEmpty);

    const persona = step2Schema.safeParse({});
    expect(persona.success).toBe(false);
    expect(
      persona.success ? [] : persona.error.issues.map((issue) => issue.message),
    ).toContain(copy.collection.validation.persona);
  });

  it("máximo menor que o mínimo não envia", async () => {
    let envios = 0;
    server.use(
      http.post("/api/v1/sessions", () => {
        envios += 1;
        return HttpResponse.json(SESSION, { status: 201 });
      }),
    );
    renderPage();
    await waitForStep1();

    await typePriceMax("100000");
    await userEvent.click(
      screen.getByRole("button", { name: copy.onboarding.next }),
    );

    expect(
      await screen.findByText(copy.collection.validation.priceOrder),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: copy.onboarding.price.title }),
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("heading", { name: copy.onboarding.persona.title }),
    ).not.toBeInTheDocument();
    expect(envios).toBe(0);
  });

  it("cria a sessão e vai para /comparar", async () => {
    const corpos: Record<string, unknown>[] = [];
    server.use(
      http.post("/api/v1/sessions", async ({ request }) => {
        corpos.push((await request.json()) as Record<string, unknown>);
        return HttpResponse.json(SESSION, { status: 201 });
      }),
    );
    renderPage();
    await waitForStep1();

    await typePriceMax("900000");
    await userEvent.click(
      screen.getByRole("button", { name: copy.onboarding.next }),
    );

    await screen.findByRole("heading", { name: copy.onboarding.persona.title });
    await userEvent.click(screen.getByRole("radio", { name: /Família/ }));
    await userEvent.click(
      screen.getByRole("button", { name: copy.onboarding.submit }),
    );

    await waitFor(() => expect(corpos).toHaveLength(1));
    expect(corpos[0]).toMatchObject({
      mode: "product",
      city: "Goiânia",
      purpose: "sale",
      persona_slug: "familia",
    });
    expect(typeof corpos[0].price_min).toBe("number");
    expect(typeof corpos[0].price_max).toBe("number");

    expect(await screen.findByText(copy.compare.question)).toBeInTheDocument();
    expect(useSessionStore.getState().sessionId).toBe(SESSION.id);
    expect(useSessionStore.getState().mode).toBe("product");
  });
});
