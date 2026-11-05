import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { copy } from "@/lib/copy";

/** O passo 1 enquanto os metadados carregam. */
export function OnboardingSkeleton() {
  return (
    <div className="flex flex-col gap-4 md:gap-6" aria-busy="true">
      <span className="sr-only" role="status">
        {copy.onboarding.loading}
      </span>
      <div className="flex items-center gap-3" aria-live="polite">
        <span className="shrink-0 text-sm font-medium">
          {copy.onboarding.step(1, 2)}
        </span>
        <Progress value={50} className="flex-1" />
      </div>
      <div className="flex flex-col gap-1">
        <h1 className="text-2xl font-semibold tracking-tight md:text-3xl">
          {copy.onboarding.price.title}
        </h1>
        <p className="text-muted-foreground md:text-lg">
          {copy.onboarding.price.lead}
        </p>
      </div>
      <div className="flex flex-col gap-4 rounded-xl border bg-card p-4 shadow-sm md:p-6">
        <Skeleton className="h-11 w-full" />
        <Skeleton className="h-6 w-full" />
        <Skeleton className="h-16 w-full" />
      </div>
    </div>
  );
}
