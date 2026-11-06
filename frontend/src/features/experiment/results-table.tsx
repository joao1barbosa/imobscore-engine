import type { ExperimentRow } from "@/api/queries";
import { Card } from "@/components/ui/card";
import { copy } from "@/lib/copy";

type ResultsTableProps = {
  rows: ExperimentRow[];
};

type Method = ExperimentRow["method"];

const METHODS: Method[] = ["bayes", "mle", "persona", "equal"];

const percentFormatter = new Intl.NumberFormat("pt-BR", {
  style: "percent",
  maximumFractionDigits: 0,
});

const decimalFormatter = new Intl.NumberFormat("pt-BR", {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

/** A tabela da curva: acurácia e perda logarítmica de cada método. */
export function ResultsTable({ rows }: ResultsTableProps) {
  const nValues = [...new Set(rows.map((row) => row.n_train))].sort(
    (a, b) => a - b,
  );
  const byMethodAndPairs = new Map(
    rows.map((row) => [`${row.method}-${row.n_train}`, row]),
  );

  return (
    <Card className="gap-3 rounded-xl border bg-card p-4 text-card-foreground shadow-sm ring-0 md:p-6">
      <h2 className="text-lg font-semibold">{copy.experiment.table.title}</h2>

      <div className="overflow-x-auto">
        <table className="w-full min-w-[440px] text-left text-sm tabular-nums">
          <thead className="text-muted-foreground">
            <tr>
              <th className="py-1 font-medium">
                {copy.experiment.table.method}
              </th>
              {nValues.map((nTrain) => (
                <th key={nTrain} className="font-medium">
                  {copy.experiment.table.pairs(nTrain)}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {METHODS.map((method) => (
              <tr key={method} className="border-t">
                <td className="py-1.5 pr-2">
                  {copy.experiment.methods[method]}
                </td>
                {nValues.map((nTrain) => {
                  const row = byMethodAndPairs.get(`${method}-${nTrain}`);

                  return (
                    <td key={nTrain}>
                      {row ? (
                        <>
                          {percentFormatter.format(row.acc_mean)}{" "}
                          <span className="text-muted-foreground">
                            · {decimalFormatter.format(row.ll_mean)}
                          </span>
                        </>
                      ) : null}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <p className="text-xs text-muted-foreground">
        {copy.experiment.table.note}
      </p>
    </Card>
  );
}
