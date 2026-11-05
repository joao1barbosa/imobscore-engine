import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { http, HttpResponse } from "msw";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { TooltipProvider } from "@/components/ui/tooltip";
import { useSessionStore } from "@/stores/session-store";
import { server } from "@/test/setup";
import { copy } from "@/lib/copy";
import { FeedPage } from "./feed-page";
import { ScoreBadge } from "./score-badge";

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

const TITLE_C = "Apartamento de 3 quartos no Setor Central";
const TITLE_A = "Apartamento de 3 quartos no Setor Bueno";
const TITLE_B = "Casa de 4 quartos no Jardim América";

function renderPage() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={["/feed"]}>
        <FeedPage />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

function titlesInOrder(root: Element | null): (string | null)[] {
  if (!root) {
    return [];
  }
  return within(root as HTMLElement)
    .getAllByRole("heading", { level: 2 })
    .map((heading) => heading.textContent);
}

beforeEach(() => {
  useSessionStore.getState().reset();
});

afterEach(() => {
  vi.restoreAllMocks();
});

describe("feed", () => {
  it("troca a ordem entre Depois e Antes sem pedir o feed de novo", async () => {
    server.use(
      http.get("/api/v1/sessions/:sessionId", () =>
        HttpResponse.json({ ...SESSION, answered: 3 }),
      ),
    );
    useSessionStore.setState({ sessionId: SESSION.id, mode: "demo" });
    const fetchSpy = vi.spyOn(globalThis, "fetch");
    const feedCalls = () =>
      fetchSpy.mock.calls.filter(([input]) => {
        const url = input instanceof Request ? input.url : String(input);
        return url.includes("/feed");
      }).length;

    const { container } = renderPage();

    await waitFor(() =>
      expect(titlesInOrder(container.querySelector("ol"))).toEqual([
        TITLE_C,
        TITLE_A,
        TITLE_B,
      ]),
    );
    expect(feedCalls()).toBe(2);

    await userEvent.click(screen.getByRole("tab", { name: copy.feed.before }));

    await waitFor(() =>
      expect(titlesInOrder(container.querySelector("ol"))).toEqual([
        TITLE_A,
        TITLE_B,
        TITLE_C,
      ]),
    );
    expect(feedCalls()).toBe(2);
  });

  it("mostra o número e a faixa de cor nos limites do selo", () => {
    const cases = [
      { score: 39, band: "bg-score-low" },
      { score: 40, band: "bg-score-mid" },
      { score: 69, band: "bg-score-mid" },
      { score: 70, band: "bg-score-high" },
    ];

    for (const { score, band } of cases) {
      const { unmount } = render(
        <TooltipProvider>
          <ScoreBadge score={score} low={0} high={100} />
        </TooltipProvider>,
      );

      expect(screen.getByText(String(score))).toHaveClass(band);
      unmount();
    }
  });

  it("mostra os textos dos estados vazio e de erro", async () => {
    let failing = false;
    server.use(
      http.get("/api/v1/sessions/:sessionId/feed", () => {
        if (failing) {
          return new HttpResponse(null, { status: 500 });
        }
        return HttpResponse.json({
          items: [],
          next_offset: null,
          method: "bayes",
          n_comparisons: 0,
        });
      }),
    );
    useSessionStore.setState({ sessionId: SESSION.id, mode: "demo" });

    const empty = renderPage();

    expect(await screen.findByText(copy.feed.empty.title)).toBeInTheDocument();
    expect(screen.getByText(copy.feed.empty.description)).toBeInTheDocument();

    empty.unmount();
    failing = true;

    renderPage();

    expect(
      await screen.findByText(copy.feed.loadError.title),
    ).toBeInTheDocument();
    expect(
      screen.getByText(copy.feed.loadError.description),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: copy.common.retry }),
    ).toBeInTheDocument();
  });
});
