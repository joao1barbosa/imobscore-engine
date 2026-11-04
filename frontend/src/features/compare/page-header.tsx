import { Link } from "react-router-dom";

import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/cn";
import { copy } from "@/lib/copy";

type PageHeaderProps = {
  active?: "feed" | "model" | "experiment";
};

const NAV_ITEMS = [
  { id: "feed", to: "/feed", label: copy.common.nav.feed },
  { id: "model", to: "/modelo", label: copy.common.nav.model },
  { id: "experiment", to: "/experimento", label: copy.common.nav.experiment },
] as const;

/**
 * O cabeçalho das telas: a marca à esquerda, a navegação das telas de
 * resultado (quando há uma) e o selo do catálogo de demonstração.
 */
export function PageHeader({ active }: PageHeaderProps) {
  return (
    <header className="border-b bg-card">
      <div className="mx-auto flex h-12 max-w-5xl items-center justify-between gap-3 px-4 md:h-14">
        <span className="font-semibold tracking-tight text-primary md:text-lg">
          {copy.common.appName}
        </span>
        {active ? (
          <nav
            className="flex items-center gap-1"
            aria-label={copy.common.nav.label}
          >
            {NAV_ITEMS.map((item) => (
              <Link
                key={item.id}
                to={item.to}
                aria-current={active === item.id ? "page" : undefined}
                className={cn(
                  "rounded-md px-2 py-1 text-sm font-medium focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring",
                  active === item.id
                    ? "bg-accent text-accent-foreground"
                    : "text-muted-foreground hover:text-foreground",
                )}
              >
                {item.label}
              </Link>
            ))}
          </nav>
        ) : null}
        <Badge
          variant="secondary"
          className={cn(
            "rounded-md",
            active ? "hidden md:inline-flex" : undefined,
          )}
        >
          {copy.common.demoCatalog}
        </Badge>
      </div>
    </header>
  );
}
