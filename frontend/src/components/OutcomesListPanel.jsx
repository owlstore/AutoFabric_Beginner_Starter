export default function OutcomesListPanel({ outcomesList, hasLoaded }) {
  return (
    <div style={{ background: "#fff", border: "1px solid #e5e5e5", borderRadius: 16, padding: 20 }}>
      <h2>结果对象列表</h2>
      <div style={{ marginTop: 12, display: "grid", gap: 10 }}>
        {!hasLoaded ? (
          <div style={{ color: "#666" }}>点击“查看所有结果对象”后，这里会显示数据。</div>
        ) : outcomesList.length === 0 ? (
          <div style={{ color: "#666" }}>当前没有可显示的结果对象。</div>
        ) : (
          outcomesList.map((outcome) => (
            <div key={outcome.id} style={{ padding: 12, borderRadius: 12, border: "1px solid #eee" }}>
              <div style={{ fontWeight: 600 }}>{outcome.title}</div>
              <div style={{ marginTop: 6, fontSize: 12, color: "#666" }}>
                outcome_id: {outcome.id} · goal_id: {outcome.goal_id}
              </div>
              <div style={{ marginTop: 6, fontSize: 12, color: "#666" }}>
                status: {outcome.status} · stage: {outcome.stage ?? "-"}
              </div>
              <div style={{ marginTop: 6, fontSize: 12, color: "#666" }}>
                summary: {outcome.summary ?? "-"}
              </div>
              <div style={{ marginTop: 6, fontSize: 12, color: "#666" }}>
                updated_at: {outcome.updated_at ?? "-"}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
