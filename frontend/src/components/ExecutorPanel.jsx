export default function ExecutorPanel({ lastExecutorRun, lastExecutorMessage }) {
  function renderModeTag(mode) {
    const isBridge = mode === "bridge";

    let label = mode || "unknown";
    let background = "#f5f5f5";
    let color = "#666";
    let border = "1px solid #e5e5e5";

    if (isBridge) {
      label = "Bridge 模式";
      background = "#eef4ff";
      color = "#2457c5";
      border = "1px solid #cfe0ff";
    }

    return (
      <div
        style={{
          display: "inline-flex",
          alignItems: "center",
          padding: "6px 10px",
          borderRadius: 999,
          fontSize: 12,
          fontWeight: 700,
          background,
          color,
          border,
        }}
      >
        {label}
      </div>
    );
  }

  return (
    <div
      style={{
        marginTop: 20,
        background: "#fff",
        border: "1px solid #e5e5e5",
        borderRadius: 16,
        padding: 20
      }}
    >
      <h2>最近执行结果</h2>

      {!lastExecutorRun ? (
        <div style={{ marginTop: 12, color: "#666" }}>当前 Workspace 还没有执行器结果。</div>
      ) : (
        <>
          <div style={{ marginTop: 12, padding: 12, border: "1px solid #eee", borderRadius: 12, background: "#fafafa" }}>
            <div style={{ fontSize: 13, color: "#666" }}>执行说明</div>
            <div style={{ marginTop: 6, fontSize: 15 }}>
              当前结果来自执行器调用返回，便于判断这次是桥接模式还是后续真实执行模式。
            </div>
          </div>

          <div style={{ marginTop: 12, display: "grid", gridTemplateColumns: "1fr 1fr 1fr 2fr", gap: 12 }}>
            <div style={{ padding: 12, border: "1px solid #eee", borderRadius: 12 }}>
              <div style={{ fontSize: 13, color: "#666" }}>Task</div>
              <div style={{ marginTop: 6, fontSize: 16, fontWeight: 700 }}>{lastExecutorRun.task_name}</div>
            </div>

            <div style={{ padding: 12, border: "1px solid #eee", borderRadius: 12 }}>
              <div style={{ fontSize: 13, color: "#666" }}>Status</div>
              <div style={{ marginTop: 6, fontSize: 16, fontWeight: 700 }}>{lastExecutorRun.status}</div>
            </div>

            <div style={{ padding: 12, border: "1px solid #eee", borderRadius: 12 }}>
              <div style={{ fontSize: 13, color: "#666" }}>Mode</div>
              <div style={{ marginTop: 8 }}>
                {renderModeTag(lastExecutorRun.mode)}
              </div>
            </div>

            <div style={{ padding: 12, border: "1px solid #eee", borderRadius: 12 }}>
              <div style={{ fontSize: 13, color: "#666" }}>Message</div>
              <div style={{ marginTop: 6, fontSize: 15 }}>{lastExecutorMessage ?? "-"}</div>
              <div style={{ marginTop: 8, fontSize: 12, color: "#666" }}>
                executed_at: {lastExecutorRun.executed_at ?? "-"}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
