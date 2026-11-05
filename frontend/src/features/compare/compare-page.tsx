import { useNavigate } from "react-router-dom";

import { useSessionStore } from "@/stores/session-store";
import { ComparePanel } from "./compare-panel";

/**
 * A rota das comparações, nos modos demo e produto: ao terminar os pares, a
 * pessoa vai para o feed.
 */
export function ComparePage() {
  const navigate = useNavigate();
  const sessionId = useSessionStore((state) => state.sessionId);

  if (!sessionId) {
    return null;
  }

  return (
    <ComparePanel sessionId={sessionId} onDone={() => navigate("/feed")} />
  );
}
