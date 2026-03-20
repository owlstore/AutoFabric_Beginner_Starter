export default function HeaderStatusBar({ health, apiBase }) {
  const backendOk = health?.status === "ok";
  const databaseOk = health?.database_connected === true;

  return (
    <div
      style={{
        marginBottom: 20,
        background: "#fff",
        border: "1px solid #e5e5e5",
        borderRadius: 16,
        padding: 16,
        display: "grid",
        gridTemplateColumns: "1fr 1fr 2fr",
        gap: 12
      }}
    >
      <div style={{ padding: 12, border: "1px solid #eee", borderRadius: 12 }}>
        <div style={{ fontSize: 13, color: "#666" }}>Backend</div>
        <div style={{ marginTop: 6, fontSize: 20, fontWeight: 700, color: backendOk ? "#0a7a33" : "#b00020" }}>
          {backendOk ? "OK" : "DOWN"}
        </div>
      </div>

      <div style={{ padding: 12, border: "1px solid #eee", borderRadius: 12 }}>
        <div style={{ fontSize: 13, color: "#666" }}>Database</div>
        <div style={{ marginTop: 6, fontSize: 20, fontWeight: 700, color: databaseOk ? "#0a7a33" : "#b00020" }}>
          {databaseOk ? "Connected" : "Disconnected"}
        </div>
      </div>

      <div style={{ padding: 12, border: "1px solid #eee", borderRadius: 12 }}>
        <div style={{ fontSize: 13, color: "#666" }}>API Base</div>
        <div style={{ marginTop: 6, fontSize: 16, fontWeight: 600 }}>{apiBase}</div>
        {health?.database_info?.user ? (
          <div style={{ marginTop: 6, fontSize: 13, color: "#666" }}>
            DB: {health.database_info.database} · User: {health.database_info.user}
          </div>
        ) : null}
      </div>
    </div>
  );
}
