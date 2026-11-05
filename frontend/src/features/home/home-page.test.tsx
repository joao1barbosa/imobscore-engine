import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";

import { copy } from "@/lib/copy";
import { HomePage } from "./home-page";

function renderPage() {
  return render(
    <MemoryRouter initialEntries={["/"]}>
      <HomePage />
    </MemoryRouter>,
  );
}

describe("tela de início", () => {
  it("mostra a frase principal, o texto de apoio e os três passos", () => {
    renderPage();

    expect(
      screen.getByRole("heading", { name: copy.home.headline }),
    ).toBeInTheDocument();
    expect(screen.getByText(copy.home.lead)).toBeInTheDocument();

    copy.home.steps.forEach((step, index) => {
      expect(
        screen.getByRole("heading", {
          name: copy.home.stepTitle(index + 1, step.title),
        }),
      ).toBeInTheDocument();
      expect(screen.getByText(step.body)).toBeInTheDocument();
    });
  });

  it("aponta os botões para o onboarding e para o modo demo", () => {
    renderPage();

    expect(screen.getByRole("link", { name: copy.home.start })).toHaveAttribute(
      "href",
      "/comecar",
    );
    expect(screen.getByRole("link", { name: copy.home.demo })).toHaveAttribute(
      "href",
      "/demo",
    );
  });

  it("aponta o link dos resultados para o experimento", () => {
    renderPage();

    expect(
      screen.getByRole("link", { name: copy.home.experimentLink }),
    ).toHaveAttribute("href", "/experimento");
  });
});
