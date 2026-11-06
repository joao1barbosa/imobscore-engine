import type { WeightOut } from "@/api/queries";
import { copy } from "@/lib/copy";

type WeightsTableProps = {
  weights: WeightOut[];
};

const decimalFormatter = new Intl.NumberFormat("pt-BR", {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

/**
 * O equivalente acessível do gráfico de pesos: os mesmos valores em uma
 * tabela que abre e fecha.
 */
export function WeightsTable({ weights }: WeightsTableProps) {
  return (
    <details className="text-sm">
      <summary className="cursor-pointer font-medium focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring">
        {copy.modelPanel.weights.tableToggle}
      </summary>
      <div className="mt-2 overflow-x-auto">
        <table className="w-full min-w-[420px] text-left tabular-nums">
          <thead className="text-muted-foreground">
            <tr>
              <th scope="col" className="py-1 font-medium">
                {copy.modelPanel.weights.tableFeature}
              </th>
              <th scope="col" className="font-medium">
                {copy.modelPanel.weights.tablePrior}
              </th>
              <th scope="col" className="font-medium">
                {copy.modelPanel.weights.tablePosterior}
              </th>
              <th scope="col" className="font-medium">
                {copy.modelPanel.weights.tableInterval}
              </th>
            </tr>
          </thead>
          <tbody>
            {weights.map((weight) => (
              <tr key={weight.feature_key} className="border-t">
                <td className="py-1">{weight.label}</td>
                <td>{decimalFormatter.format(weight.prior_mean)}</td>
                <td>{decimalFormatter.format(weight.post_mean)}</td>
                <td>
                  {copy.modelPanel.weights.interval(
                    decimalFormatter.format(weight.ci_low),
                    decimalFormatter.format(weight.ci_high),
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </details>
  );
}
