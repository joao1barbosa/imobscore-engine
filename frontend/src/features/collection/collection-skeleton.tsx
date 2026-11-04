import { Skeleton } from "@/components/ui/skeleton";
import { copy } from "@/lib/copy";

function SectionSkeleton({ lines }: { lines: string[] }) {
  return (
    <div className="flex flex-col gap-4 rounded-xl border bg-card p-4 md:p-6">
      <Skeleton className="h-5 w-1/3" />
      {lines.map((line) => (
        <Skeleton key={line} className={line} />
      ))}
    </div>
  );
}

/** O formulário enquanto os metadados carregam. */
export function CollectionSkeleton() {
  return (
    <div className="flex flex-col gap-4" aria-busy="true">
      <span className="sr-only" role="status">
        {copy.collection.loadingForm}
      </span>
      <div className="flex flex-col gap-1">
        <h1 className="text-2xl font-semibold tracking-tight md:text-3xl">
          {copy.collection.form.title}
        </h1>
        <p className="text-muted-foreground md:text-lg">
          {copy.collection.form.lead}
        </p>
      </div>
      <SectionSkeleton lines={["h-20"]} />
      <SectionSkeleton lines={["h-11", "h-24"]} />
      <SectionSkeleton lines={["h-20"]} />
    </div>
  );
}
