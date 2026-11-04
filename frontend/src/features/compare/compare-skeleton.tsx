import { Skeleton } from "@/components/ui/skeleton";
import { copy } from "@/lib/copy";

function CardSkeleton() {
  return (
    <div className="flex gap-3 rounded-xl border bg-card p-3 md:flex-col md:gap-0 md:p-0">
      <Skeleton className="size-20 shrink-0 rounded-lg md:h-44 md:w-full md:rounded-none" />
      <div className="flex flex-1 flex-col gap-2 md:gap-3 md:p-5">
        <Skeleton className="h-7 w-2/3" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-1/2" />
        <Skeleton className="h-12 w-full" />
      </div>
    </div>
  );
}

/** Os dois cartões do par enquanto a consulta do par está em andamento. */
export function CompareSkeleton() {
  return (
    <div className="grid gap-3 md:grid-cols-2 md:gap-6" aria-busy="true">
      <span className="sr-only" role="status">
        {copy.compare.loading}
      </span>
      <CardSkeleton />
      <CardSkeleton />
    </div>
  );
}
