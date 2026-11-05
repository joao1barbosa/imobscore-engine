import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { copy } from "@/lib/copy";

type BeforeAfterToggleProps = {
  value: "before" | "after";
  onChange: (v: "before" | "after") => void;
};

/** A alternância entre o ranking só com o perfil e o ajustado pelas escolhas. */
export function BeforeAfterToggle({ value, onChange }: BeforeAfterToggleProps) {
  return (
    <Tabs
      value={value}
      onValueChange={(next) => {
        if (next === "before" || next === "after") {
          onChange(next);
        }
      }}
      className="w-full md:w-auto"
    >
      <TabsList
        role="tablist"
        aria-label={copy.feed.toggleLabel}
        className="h-auto w-full gap-1 rounded-lg bg-secondary p-1 md:w-auto md:self-start"
      >
        <TabsTrigger
          value="before"
          className="h-10 flex-1 rounded-md px-5 text-sm font-medium text-muted-foreground hover:text-foreground data-active:bg-primary data-active:text-primary-foreground md:flex-none"
        >
          {copy.feed.before}
        </TabsTrigger>
        <TabsTrigger
          value="after"
          className="h-10 flex-1 rounded-md px-5 text-sm font-medium text-muted-foreground hover:text-foreground data-active:bg-primary data-active:text-primary-foreground md:flex-none"
        >
          {copy.feed.after}
        </TabsTrigger>
      </TabsList>
    </Tabs>
  );
}
