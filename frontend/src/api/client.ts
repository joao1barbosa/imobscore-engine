import createClient from "openapi-fetch";

import { copy } from "@/lib/copy";
import type { components, paths } from "./schema";

/**
 * O OpenAPI da API traz o prefixo `/api/v1` em cada caminho. O cliente usa
 * `baseUrl: "/api/v1"`, então o prefixo sai dos tipos e volta na URL.
 */
type ApiPaths = {
  [
    Key in keyof paths as Key extends `/api/v1${infer Rest}` ? Rest : Key
  ]: paths[Key];
};

/**
 * O `openapi-fetch` monta cada requisição com `new Request(url)`, e isso
 * exige uma URL absoluta. O app fala com a API no mesmo origen (`/api/v1`):
 * no desenvolvimento o Vite faz o proxy e, em produção, o Nginx serve os
 * dois. Aqui a URL relativa é resolvida.
 */
class SameOriginRequest extends Request {
  constructor(input: RequestInfo | URL, init?: RequestInit) {
    super(
      typeof input === "string"
        ? new URL(input, window.location.origin)
        : input,
      init,
    );
  }
}

export const client = createClient<ApiPaths>({
  baseUrl: "/api/v1",
  Request: SameOriginRequest,
  // O `openapi-fetch` guarda o `fetch` no momento em que o cliente é criado.
  // Nos testes, o MSW só troca o `globalThis.fetch` depois, então ele é
  // resolvido na hora de cada requisição.
  fetch: (input: Request, init?: RequestInit) => globalThis.fetch(input, init),
});

export type AnswerIn = components["schemas"]["AnswerIn"];
export type AnswerOut = components["schemas"]["AnswerOut"];
export type ListingCard = components["schemas"]["ListingCard"];
export type MetaOptions = components["schemas"]["MetaOptions"];
export type PairOut = components["schemas"]["PairOut"];
export type PersonaOut = components["schemas"]["PersonaOut"];
export type SegmentOptions = components["schemas"]["SegmentOptions"];
export type SessionCreate = components["schemas"]["SessionCreate"];
export type SessionOut = components["schemas"]["SessionOut"];

type ErrorBody = {
  detail?: { code?: string; message?: string };
};

/** Erro da API, no formato único do projeto: `{"detail": {"code", "message"}}`. */
export class ApiRequestError extends Error {
  readonly status: number;
  readonly code: string;

  constructor(status: number, code: string, message: string) {
    super(message);
    this.name = "ApiRequestError";
    this.status = status;
    this.code = code;
  }
}

/** A mensagem de um código de erro, sempre em português do Brasil. */
export function apiErrorMessage(code: string): string {
  const messages = copy.common.apiErrors as Record<string, string>;
  return messages[code] ?? messages.unknown;
}

/** Converte o corpo de erro da API no `ApiRequestError` do projeto. */
export function toApiError(status: number, body: unknown): ApiRequestError {
  const detail = (body as ErrorBody | undefined)?.detail;
  const code = typeof detail?.code === "string" ? detail.code : "unknown";
  const message =
    typeof detail?.message === "string"
      ? detail.message
      : apiErrorMessage(code);
  return new ApiRequestError(status, code, message);
}
