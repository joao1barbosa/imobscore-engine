import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it } from "vitest";

import { useSessionStore } from "@/stores/session-store";
import { copy } from "@/lib/copy";
import { App, AppRoutes } from "./router";

const SESSION_ID = "8b7a3d21-4c6e-4a1e-8f2c-000000000000";

function renderRoute(path: string) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[path]}>
        <AppRoutes />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("rotas do app", () => {
  beforeEach(() => {
    useSessionStore.getState().reset();
  });

  it("renderiza a tela de início em /", () => {
    renderRoute("/");

    expect(
      screen.getByRole("heading", { name: copy.home.headline }),
    ).toBeInTheDocument();
  });

  it("leva rota desconhecida para a inicial", () => {
    renderRoute("/rota-que-nao-existe");

    expect(
      screen.getByRole("heading", { name: copy.home.headline }),
    ).toBeInTheDocument();
  });

  it("sem sessão, uma tela protegida vai para o onboarding", () => {
    renderRoute("/feed");

    expect(
      screen.getByRole("heading", { name: copy.onboarding.price.title }),
    ).toBeInTheDocument();
  });

  it("com sessão, uma tela protegida mostra a tela", () => {
    useSessionStore.setState({ sessionId: SESSION_ID, mode: "product" });

    renderRoute("/feed");

    expect(screen.getByRole("heading", { name: "/feed" })).toBeInTheDocument();
  });

  it("monta o app inteiro, com os providers, em /feed", () => {
    useSessionStore.setState({ sessionId: SESSION_ID, mode: "product" });
    window.history.pushState({}, "", "/feed");

    render(<App />);

    expect(screen.getByRole("heading", { name: "/feed" })).toBeInTheDocument();
  });
});
