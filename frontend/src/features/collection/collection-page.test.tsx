import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { http, HttpResponse } from "msw";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it } from "vitest";

import { useSessionStore } from "@/stores/session-store";
import { server } from "@/test/setup";
import { copy } from "@/lib/copy";
import { CollectionPage } from "./collection-page";

const SESSION = {
  id: "8b7a3d21-4c6e-4a1e-8f2c-000000000000",
  mode: "collection",
  city: "Goiânia",
  purpose: "sale",
  price_min: "140000.00",
  price_max: "1360000.00",
  persona_slug: "familia",
  target_pairs: 25,
  answered: 0,
  status: "comparing",
};

function renderPage() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={["/coleta"]}>
        <CollectionPage />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

async function openForm() {
  await userEvent.click(
    screen.getByRole("button", { name: copy.collection.welcome.start }),
  );
  await screen.findByRole("heading", { name: copy.collection.form.title });
}

async function fillForm() {
  await userEvent.click(screen.getByRole("checkbox"));
  await userEvent.click(screen.getByRole("radio", { name: /Família/ }));
}

describe("telas da coleta", () => {
  beforeEach(() => {
    useSessionStore.getState().reset();
  });

  it("leva da tela inicial ao formulário", async () => {
    renderPage();

    expect(
      screen.getByRole("heading", { name: copy.collection.welcome.title }),
    ).toBeInTheDocument();

    await openForm();

    expect(
      screen.getByRole("heading", { name: copy.collection.form.title }),
    ).toBeInTheDocument();
  });

  it("não envia o formulário sem o consentimento", async () => {
    let envios = 0;
    server.use(
      http.post("/api/v1/sessions", () => {
        envios += 1;
        return HttpResponse.json(SESSION, { status: 201 });
      }),
    );
    renderPage();
    await openForm();

    await userEvent.click(screen.getByRole("radio", { name: /Família/ }));
    await userEvent.click(
      screen.getByRole("button", { name: copy.collection.submit }),
    );

    expect(
      await screen.findByText(copy.collection.validation.consent),
    ).toBeInTheDocument();
    expect(envios).toBe(0);
  });

  it("cria a sessão em Goiânia e para compra", async () => {
    const corpos: Record<string, unknown>[] = [];
    server.use(
      http.post("/api/v1/sessions", async ({ request }) => {
        corpos.push((await request.json()) as Record<string, unknown>);
        return HttpResponse.json(SESSION, { status: 201 });
      }),
    );
    renderPage();
    await openForm();

    await fillForm();
    await userEvent.click(
      screen.getByRole("button", { name: copy.collection.submit }),
    );

    await waitFor(() => expect(corpos).toHaveLength(1));
    expect(corpos[0]).toMatchObject({
      mode: "collection",
      city: "Goiânia",
      purpose: "sale",
      persona_slug: "familia",
      consent: true,
    });
    expect(typeof corpos[0].price_min).toBe("number");
    expect(typeof corpos[0].price_max).toBe("number");
  });

  it("leva ao agradecimento quando a API responde 204", async () => {
    server.use(
      http.post("/api/v1/sessions", () =>
        HttpResponse.json(SESSION, { status: 201 }),
      ),
      http.get(
        "/api/v1/sessions/:sessionId/next-pair",
        () => new HttpResponse(null, { status: 204 }),
      ),
    );
    renderPage();
    await openForm();

    await fillForm();
    await userEvent.click(
      screen.getByRole("button", { name: copy.collection.submit }),
    );

    expect(
      await screen.findByRole("heading", {
        name: copy.collection.thanks.title,
      }),
    ).toBeInTheDocument();
    expect(
      await screen.findByText(copy.collection.thanks.body(25)),
    ).toBeInTheDocument();
  });

  it("502 mantém a sessão guardada e mostra a mensagem", async () => {
    server.use(
      http.get(
        "/api/v1/sessions/:sessionId",
        () => new HttpResponse(null, { status: 502 }),
      ),
    );
    useSessionStore.setState({ sessionId: SESSION.id, mode: "collection" });
    renderPage();

    expect(
      await screen.findByText(copy.collection.loadError.title),
    ).toBeInTheDocument();
    expect(useSessionStore.getState().sessionId).toBe(SESSION.id);
  });

  it("falha de rede mantém a sessão guardada e mostra a mensagem", async () => {
    server.use(
      http.get("/api/v1/sessions/:sessionId", () => HttpResponse.error()),
    );
    useSessionStore.setState({ sessionId: SESSION.id, mode: "collection" });
    renderPage();

    expect(
      await screen.findByText(copy.collection.loadError.title),
    ).toBeInTheDocument();
    expect(useSessionStore.getState().sessionId).toBe(SESSION.id);
  });

  it("depois de um erro, tentar de novo leva aos pares", async () => {
    let chamadas = 0;
    server.use(
      http.get("/api/v1/sessions/:sessionId", () => {
        chamadas += 1;
        if (chamadas === 1) {
          return new HttpResponse(null, { status: 502 });
        }
        return HttpResponse.json(SESSION);
      }),
    );
    useSessionStore.setState({ sessionId: SESSION.id, mode: "collection" });
    renderPage();

    await userEvent.click(
      await screen.findByRole("button", { name: copy.common.retry }),
    );

    expect(
      await screen.findByRole("heading", { name: copy.compare.question }),
    ).toBeInTheDocument();
    expect(useSessionStore.getState().sessionId).toBe(SESSION.id);
  });

  it("404 session_not_found limpa a sessão e volta à tela inicial", async () => {
    server.use(
      http.get("/api/v1/sessions/:sessionId", () =>
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
    useSessionStore.setState({ sessionId: SESSION.id, mode: "collection" });
    renderPage();

    expect(
      await screen.findByRole("heading", {
        name: copy.collection.welcome.title,
      }),
    ).toBeInTheDocument();
    await waitFor(() =>
      expect(useSessionStore.getState().sessionId).toBeNull(),
    );
  });
});
