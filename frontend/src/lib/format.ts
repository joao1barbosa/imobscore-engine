// Formatação de números da interface. Dono dos textos: o `copy.ts` do arquiteto.

const brlFormatter = new Intl.NumberFormat("pt-BR", {
  style: "currency",
  currency: "BRL",
  maximumFractionDigits: 0,
});

const decimalFormatter = new Intl.NumberFormat("pt-BR", {
  maximumFractionDigits: 1,
});

/**
 * O preço chega como texto no JSON (`Decimal` do Pydantic), então o valor é
 * convertido antes de ser formatado.
 */
export function formatBRL(value: number | string): string {
  return brlFormatter.format(Number(value));
}

/** A área do imóvel, em metros quadrados: "98,6 m²". */
export function formatArea(areaM2: number): string {
  return `${decimalFormatter.format(areaM2)} m²`;
}

/** A distância ao centro, em quilômetros: "2,3 km". */
export function formatDistance(distanceKm: number): string {
  return `${decimalFormatter.format(distanceKm)} km`;
}
