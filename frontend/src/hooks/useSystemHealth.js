import { useEffect, useState } from "react";
import { fetchHealth } from "../api/workbenchApi";

export default function useSystemHealth() {
  const [health, setHealth] = useState({
    ok: false,
    loading: true,
    error: "",
    service: "",
    version: "",
  });

  async function loadHealth() {
    try {
      setHealth((prev) => ({ ...prev, loading: true, error: "" }));
      const payload = await fetchHealth();
      setHealth({
        ok: Boolean(payload?.ok),
        loading: false,
        error: "",
        service: payload?.service || "AutoFabric API",
        version: payload?.version || "unknown",
      });
    } catch (err) {
      setHealth({
        ok: false,
        loading: false,
        error: String(err?.message || err),
        service: "AutoFabric API",
        version: "unknown",
      });
    }
  }

  useEffect(() => {
    loadHealth();
  }, []);

  return {
    health,
    loadHealth,
  };
}
