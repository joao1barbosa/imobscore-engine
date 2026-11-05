import type { ReactNode } from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import { CollectionPage } from "@/features/collection/collection-page";
import { ComparePage } from "@/features/compare/compare-page";
import { DemoPage } from "@/features/demo/demo-page";
import { FeedPage } from "@/features/feed/feed-page";
import { HomePage } from "@/features/home/home-page";
import { OnboardingPage } from "@/features/onboarding/onboarding-page";
import { useSessionStore } from "@/stores/session-store";
import { Layout } from "./layout";
import { Providers } from "./providers";

const ROUTE_HOME = "/";
const ROUTE_COLLECTION = "/coleta";
const ROUTE_ONBOARDING = "/comecar";
const ROUTE_DEMO = "/demo";
const ROUTE_COMPARE = "/comparar";
const ROUTE_FEED = "/feed";
const ROUTE_MODEL = "/modelo";
const ROUTE_EXPERIMENT = "/experimento";

// As telas que só existem com uma sessão guardada. O painel do modelo chega
// na tarefa E13.
const PROTECTED_ROUTES = [ROUTE_MODEL] as const;

/**
 * Placeholder temporário: mostra o nome da rota até a tela real existir.
 * O nome da rota é um identificador técnico, não um texto de interface.
 */
export function Placeholder({ name }: { name: string }) {
  return <h1 className="text-2xl font-semibold tracking-tight">{name}</h1>;
}

/**
 * As telas que dependem de uma sessão. Sem `sessionId` guardado, a pessoa vai
 * para o onboarding, que cria a sessão.
 */
function RequireSession({ children }: { children: ReactNode }) {
  const sessionId = useSessionStore((state) => state.sessionId);

  if (!sessionId) {
    return <Navigate to={ROUTE_ONBOARDING} replace />;
  }

  return children;
}

export function AppRoutes() {
  return (
    <Routes>
      <Route path={ROUTE_HOME} element={<Layout />}>
        <Route index element={<HomePage />} />
        <Route path={ROUTE_COLLECTION.slice(1)} element={<CollectionPage />} />
        <Route path={ROUTE_ONBOARDING.slice(1)} element={<OnboardingPage />} />
        <Route path={ROUTE_DEMO.slice(1)} element={<DemoPage />} />
        <Route
          path={ROUTE_COMPARE.slice(1)}
          element={
            <RequireSession>
              <ComparePage />
            </RequireSession>
          }
        />
        <Route
          path={ROUTE_FEED.slice(1)}
          element={
            <RequireSession>
              <FeedPage />
            </RequireSession>
          }
        />
        {PROTECTED_ROUTES.map((route) => (
          <Route
            key={route}
            path={route.slice(1)}
            element={
              <RequireSession>
                <Placeholder name={route} />
              </RequireSession>
            }
          />
        ))}
        <Route
          path={ROUTE_EXPERIMENT.slice(1)}
          element={<Placeholder name={ROUTE_EXPERIMENT} />}
        />
        <Route path="*" element={<HomePage />} />
      </Route>
    </Routes>
  );
}

export function App() {
  return (
    <Providers>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </Providers>
  );
}
