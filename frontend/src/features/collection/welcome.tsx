import {
  ArrowRight,
  ChartLine,
  MousePointerClick,
  ShieldCheck,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { copy } from "@/lib/copy";

type WelcomeProps = {
  onStart: () => void;
};

/** A tela inicial da coleta: o que a pessoa vai fazer, antes de qualquer campo. */
export function Welcome({ onStart }: WelcomeProps) {
  const items = [
    {
      icon: MousePointerClick,
      title: copy.collection.welcome.whatToDo.title,
      body: copy.collection.welcome.whatToDo.body,
    },
    {
      icon: ChartLine,
      title: copy.collection.welcome.howWeUse.title,
      body: copy.collection.welcome.howWeUse.body,
    },
    {
      icon: ShieldCheck,
      title: copy.collection.welcome.noPersonalData.title,
      body: copy.collection.welcome.noPersonalData.body,
    },
  ];

  return (
    <>
      <div className="flex flex-col gap-1">
        <h1 className="text-2xl font-semibold tracking-tight md:text-3xl">
          {copy.collection.welcome.title}
        </h1>
        <p className="text-muted-foreground md:text-lg">
          {copy.collection.welcome.lead}
        </p>
      </div>
      {items.map((item) => (
        <Card
          key={item.title}
          className="flex gap-3 border p-4 shadow-sm md:gap-4 md:p-6"
        >
          <span className="grid size-10 shrink-0 place-items-center rounded-lg bg-accent text-accent-foreground">
            <item.icon className="size-5" aria-hidden="true" />
          </span>
          <div className="flex flex-col gap-1">
            <h2 className="font-semibold">{item.title}</h2>
            <p className="text-sm text-muted-foreground md:text-base">
              {item.body}
            </p>
          </div>
        </Card>
      ))}
      <Button
        onClick={onStart}
        className="h-12 w-full gap-2 px-6 text-base md:w-auto md:self-end"
      >
        {copy.collection.welcome.start}
        <ArrowRight className="size-4" aria-hidden="true" />
      </Button>
    </>
  );
}
