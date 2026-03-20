export default function ActionPanel({ workspace, actionPanel, handleAction, isExecuting }) {
  const recommendationReason =
    workspace?.execution_hint?.reason || workspace?.latest_outcome?.next_action?.summary || "";

  return (
    <div style={{ background: "#fff", border: "1px solid #e5e5e5", borderRadius: 16, padding: 20 }}>
      <h2>Action Panel</h2>

      {!workspace ? (
        <div style={{ marginTop: 12, color: "#666" }}>提交后这里会自动加载后端返回的动作面板。</div>
      ) : (
        <>
          <div
            style={{
              marginTop: 12,
              padding: 12,
              border: "1px solid #eee",
              borderRadius: 12,
              background: "#fafafa"
            }}
          >
            <div style={{ fontSize: 13, color: "#666" }}>推荐原因</div>
            <div style={{ marginTop: 6, fontSize: 15 }}>
              {recommendationReason || "系统正在根据当前目标与结果状态生成下一步推荐。"}
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12, marginTop: 12 }}>
            {actionPanel.map((item) => (
              <div key={item.label} style={{ padding: 12, border: "1px solid #eee", borderRadius: 12 }}>
                <div style={{ fontWeight: 600 }}>{item.label}</div>
                <div style={{ marginTop: 8, fontSize: 14, color: "#666" }}>{item.description}</div>
                <div style={{ marginTop: 8, fontSize: 12, color: "#999" }}>{item.action_type}</div>
                <div style={{ marginTop: 8, fontSize: 12, color: "#999" }}>priority: {item.priority ?? "-"}</div>

                <button
                  onClick={() => handleAction(item)}
                  disabled={isExecuting}
                  style={{
                    marginTop: 12,
                    padding: "10px 12px",
                    borderRadius: 10,
                    border: "1px solid #d4d4d8",
                    background: "#111",
                    color: "#fff",
                    cursor: "pointer",
                    fontSize: 14,
                    fontWeight: 600,
                    minWidth: 120
                  }}
                >
                  {isExecuting ? "执行中..." : "执行此动作"}
                </button>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
