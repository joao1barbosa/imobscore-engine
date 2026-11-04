import { BrowserRouter, Route, Routes } from "react-router-dom";

import { Layout } from "./layout";
import { Providers } from "./providers";

const ROUTE_HOME = "/";

// Rotas do esqueleto. As telas definitivas chegam nas tarefas seguintes.
const APP_ROUTES = [
  ROUTE_HOME,
  "/coleta",
  "/comecar",
  "/demo",
  "/comparar",
  "/feed",
  "/modelo",
  "/experimento",
] as const;

/**
 * Placeholder temporário: mostra o nome da rota até a tela real existir.
 * O nome da rota é um identificador técnico, não um texto de interface.
 */
export function Placeholder({ name }: { name: string }) {
  return <h1 className="text-2xl font-semibold tracking-tight">{name}</h1>;
}

export function AppRoutes() {
  return (
    <Routes>
      <Route path={ROUTE_HOME} element={<Layout />}>
        <Route index element={<Placeholder name={ROUTE_HOME} />} />
        {APP_ROUTES.filter((route) => route !== ROUTE_HOME).map((route) => (
          <Route
            key={route}
            path={route.slice(1)}
            element={<Placeholder name={route} />}
          />
        ))}
        <Route path="*" element={<Placeholder name={ROUTE_HOME} />} />
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
