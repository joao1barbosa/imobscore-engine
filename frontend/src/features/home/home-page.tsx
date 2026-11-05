import { Link } from "react-router-dom";
import {
  ArrowRight,
  ListOrdered,
  MousePointerClick,
  UserRound,
  Zap,
} from "lucide-react";

import { PageHeader } from "@/features/compare/page-header";
import { Button } from "@/components/ui/button";
import { copy } from "@/lib/copy";
import { HomeStep } from "./home-step";

const STEP_ICONS = [UserRound, MousePointerClick, ListOrdered] as const;

/** A tela de início: o que o ImobScore faz e por onde começar. */
export function HomePage() {
  return (
    <div className="flex min-h-dvh flex-col">
      <PageHeader />
      <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col gap-4 px-4 py-5 md:gap-6 md:py-10">
        <div className="flex flex-col gap-3 md:items-center md:py-8 md:text-center">
          <h1 className="text-4xl font-semibold tracking-tight md:text-6xl">
            {copy.home.headline}
          </h1>
          <p className="max-w-2xl text-lg text-muted-foreground md:text-xl">
            {copy.home.lead}
          </p>
          <div className="mt-2 flex flex-col gap-2 md:flex-row">
            <Button
              render={<Link to="/comecar" />}
              className="h-12 gap-2 rounded-md px-6 text-base hover:opacity-90"
            >
              {copy.home.start}
              <ArrowRight className="size-4" aria-hidden="true" />
            </Button>
            <Button
              render={<Link to="/demo" />}
              variant="outline"
              className="h-12 gap-2 rounded-md px-6 text-base"
            >
              <Zap className="size-4" aria-hidden="true" />
              {copy.home.demo}
            </Button>
          </div>
        </div>
        <ol className="grid gap-3 md:grid-cols-3 md:gap-6">
          {copy.home.steps.map((step, index) => (
            <HomeStep
              key={step.title}
              index={index + 1}
              icon={STEP_ICONS[index]}
              title={step.title}
              body={step.body}
            />
          ))}
        </ol>
        <p className="text-center text-sm text-muted-foreground">
          {copy.home.catalogNote}{" "}
          <Link
            to="/experimento"
            className="font-medium text-foreground underline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring"
          >
            {copy.home.experimentLink}
          </Link>
        </p>
      </main>
    </div>
  );
}
