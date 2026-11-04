import { Check } from "lucide-react";

import { Card } from "@/components/ui/card";
import { copy } from "@/lib/copy";

type ThankYouProps = {
  total: number;
};

/** O fim da coleta: as respostas foram registradas e a pessoa pode sair. */
export function ThankYou({ total }: ThankYouProps) {
  return (
    <Card className="my-auto items-center gap-3 border p-6 text-center shadow-sm md:p-10">
      <span className="grid size-14 place-items-center rounded-full bg-primary text-primary-foreground">
        <Check className="size-7" aria-hidden="true" />
      </span>
      <h1 className="text-2xl font-semibold tracking-tight md:text-3xl">
        {copy.collection.thanks.title}
      </h1>
      <p className="text-lg font-medium">
        {copy.collection.thanks.body(total)}
      </p>
      <p className="max-w-md text-muted-foreground">
        {copy.collection.thanks.purpose}
      </p>
      <p className="text-sm text-muted-foreground">
        {copy.collection.thanks.close}
      </p>
    </Card>
  );
}
