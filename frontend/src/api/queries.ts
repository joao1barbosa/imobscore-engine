import { queryOptions } from "@tanstack/react-query";

import {
  client,
  toApiError,
  type AnswerIn,
  type AnswerOut,
  type MetaOptions,
  type PairOut,
  type PersonaOut,
  type SessionCreate,
  type SessionOut,
} from "./client";

/** As faixas de preço do catálogo. Não mudam durante a sessão. */
export const metaOptionsQuery = queryOptions({
  queryKey: ["meta", "options"],
  queryFn: async (): Promise<MetaOptions> => {
    const { data, error, response } = await client.GET("/meta/options");
    if (data === undefined) {
      throw toApiError(response.status, error);
    }
    return data;
  },
  staleTime: Infinity,
});

/** As três personas, na ordem do arquivo `personas.yaml`. */
export const metaPersonasQuery = queryOptions({
  queryKey: ["meta", "personas"],
  queryFn: async (): Promise<PersonaOut[]> => {
    const { data, error, response } = await client.GET("/meta/personas");
    if (data === undefined) {
      throw toApiError(response.status, error);
    }
    return data;
  },
  staleTime: Infinity,
});

/** O estado da sessão e o progresso da coleta. */
export const sessionQuery = (sessionId: string) =>
  queryOptions({
    queryKey: ["session", sessionId],
    queryFn: async (): Promise<SessionOut> => {
      const { data, error, response } = await client.GET(
        "/sessions/{session_id}",
        {
          params: { path: { session_id: sessionId } },
        },
      );
      if (data === undefined) {
        throw toApiError(response.status, error);
      }
      return data;
    },
  });

/**
 * O par pendente da coleta. Devolve `null` quando a API responde `204`, que
 * é o sinal de que a sessão acabou.
 */
export const pairQuery = (sessionId: string) =>
  queryOptions({
    queryKey: ["pair", sessionId],
    queryFn: async (): Promise<PairOut | null> => {
      const { data, error, response } = await client.GET(
        "/sessions/{session_id}/next-pair",
        { params: { path: { session_id: sessionId } } },
      );
      if (response.status === 204) {
        return null;
      }
      if (data === undefined) {
        throw toApiError(response.status, error);
      }
      return data;
    },
  });

/** Cria a sessão a partir do onboarding. */
export async function createSession(body: SessionCreate): Promise<SessionOut> {
  const { data, error, response } = await client.POST("/sessions", { body });
  if (data === undefined) {
    throw toApiError(response.status, error);
  }
  return data;
}

/** Registra a escolha da pessoa em um par. */
export async function answerPair(
  sessionId: string,
  position: number,
  body: AnswerIn,
): Promise<AnswerOut> {
  const { data, error, response } = await client.POST(
    "/sessions/{session_id}/comparisons/{position}",
    { params: { path: { session_id: sessionId, position } }, body },
  );
  if (data === undefined) {
    throw toApiError(response.status, error);
  }
  return data;
}
