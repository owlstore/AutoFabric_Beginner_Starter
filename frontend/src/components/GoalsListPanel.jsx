export default function GoalsListPanel({ goalsList, hasLoaded }) {
  function renderSourceTag(source) {
    const isLLM = source === "llm";
    const isFallback = source === "rules_fallback";

    let label = "未知来源";
    let background = "#f5f5f5";
    let color = "#666";
    let border = "1px solid #e5e5e5";

    if (isLLM) {
      label = "LLM 解析";
      background = "#eefaf0";
      color = "#0a7a33";
      border = "1px solid #cfead7";
    } else if (isFallback) {
      label = "规则兜底";
      background = "#fff8e8";
      color = "#9a6700";
      border = "1px solid #f0dfb4";
    }

    return (
      <div
        style={{
          display: "inline-flex",
          alignItems: "center",
          padding: "4px 8px",
          borderRadius: 999,
          fontSize: 11,
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
    <div style={{ background: "#fff", border: "1px solid #e5e5e5", borderRadius: 16, padding: 20 }}>
      <h2>目标对象列表</h2>
      <div style={{ marginTop: 12, display: "grid", gap: 10 }}>
        {!hasLoaded ? (
          <div style={{ color: "#666" }}>点击“查看所有目标对象”后，这里会显示数据。</div>
        ) : goalsList.length === 0 ? (
          <div style={{ color: "#666" }}>当前没有可显示的目标对象。</div>
        ) : (
          goalsList.map((goal) => (
            <div key={goal.id} style={{ padding: 12, borderRadius: 12, border: "1px solid #eee" }}>
              <div style={{ fontWeight: 600 }}>{goal.raw_input}</div>

              <div style={{ marginTop: 8, display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
                {renderSourceTag(goal.parser_meta?.source)}
                <div style={{ fontSize: 11, color: "#666" }}>
                  LLM：{goal.parser_meta?.llm_enabled ? "已开启" : "未开启"}
                </div>
              </div>

              <div style={{ marginTop: 6, fontSize: 12, color: "#666" }}>
                id: {goal.id} · {goal.goal_type} · {goal.risk_level}
              </div>
              <div style={{ marginTop: 6, fontSize: 12, color: "#666" }}>
                created_at: {goal.created_at}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
