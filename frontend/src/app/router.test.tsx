import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";

import { App, AppRoutes } from "./router";

function renderRoute(path: string) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <AppRoutes />
    </MemoryRouter>,
  );
}

describe("rotas do esqueleto", () => {
  it("renderiza o placeholder em /feed", () => {
    renderRoute("/feed");

    expect(screen.getByRole("heading", { name: "/feed" })).toBeInTheDocument();
  });

  it("renderiza o placeholder na rota inicial", () => {
    renderRoute("/");

    expect(screen.getByRole("heading", { name: "/" })).toBeInTheDocument();
  });

  it("leva rota desconhecida para a inicial", () => {
    renderRoute("/rota-que-nao-existe");

    expect(screen.getByRole("heading", { name: "/" })).toBeInTheDocument();
  });

  it("monta o app inteiro, com os providers, em /feed", () => {
    window.history.pushState({}, "", "/feed");

    render(<App />);

    expect(screen.getByRole("heading", { name: "/feed" })).toBeInTheDocument();
  });
});
