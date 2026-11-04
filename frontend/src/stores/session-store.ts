import { create } from "zustand";
import {
  createJSONStorage,
  persist,
  type StateStorage,
} from "zustand/middleware";

export type SessionMode = "product" | "demo" | "collection";

type SessionState = {
  sessionId: string | null;
  mode: SessionMode | null;
  setSession: (id: string, mode: SessionMode) => void;
  reset: () => void;
};

/**
 * O localStorage pode estar bloqueado (modo privado, cookies desligados).
 * Nesses casos o app continua funcionando, só sem persistir a sessão: o
 * estado fica só na memória da aba.
 */
function safeLocalStorage(): StateStorage {
  try {
    const local = window.localStorage;

    return {
      getItem: (name) => local.getItem(name),
      setItem: (name, value) => local.setItem(name, value),
      removeItem: (name) => local.removeItem(name),
    };
  } catch {
    const memory = new Map<string, string>();

    return {
      getItem: (name) => memory.get(name) ?? null,
      setItem: (name, value) => {
        memory.set(name, value);
      },
      removeItem: (name) => {
        memory.delete(name);
      },
    };
  }
}

export const useSessionStore = create<SessionState>()(
  persist(
    (set) => ({
      sessionId: null,
      mode: null,
      setSession: (id, mode) => set({ sessionId: id, mode }),
      reset: () => set({ sessionId: null, mode: null }),
    }),
    {
      name: "imobscore-session",
      storage: createJSONStorage(() => safeLocalStorage()),
    },
  ),
);
