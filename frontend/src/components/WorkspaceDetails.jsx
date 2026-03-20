import ParsedGoalCard from "./ParsedGoalCard";

function prettyJson(value) {
  try {
    if (typeof value === "string") {
      try {
        return JSON.stringify(JSON.parse(value), null, 2);
      } catch {
        return value;
      }
    }
    return JSON.stringify(value, null, 2);
  } catch {
    return String(value);
  }
}

export default function WorkspaceDetails({ workspace, recentFlowEvents }) {
  if (!workspace) return null;

  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20, marginTop: 20 }}>
      <div style={{ display: "grid", gap: 20 }}>
        <ParsedGoalCard workspace={workspace} />

        <div style={{ background: "#fff", border: "1px solid #e5e5e5", borderRadius: 16, padding: 20 }}>
          <h2>原始 Workspace 详情</h2>

          <div style={{ marginTop: 12 }}>
            <div style={{ fontSize: 14, color: "#666" }}>Parsed Goal JSON</div>
            <pre style={{ marginTop: 8, background: "#f8f8f8", padding: 12, borderRadius: 12, overflowX: "auto", fontSize: 12 }}>
              {prettyJson(workspace.goal.parsed_goal)}
            </pre>
          </div>

          <div style={{ marginTop: 16 }}>
            <div style={{ fontSize: 14, color: "#666" }}>Next Action JSON</div>
            <pre style={{ marginTop: 8, background: "#f8f8f8", padding: 12, borderRadius: 12, overflowX: "auto", fontSize: 12 }}>
              {prettyJson(workspace.latest_outcome?.next_action ?? {})}
            </pre>
          </div>

          <div style={{ marginTop: 16 }}>
            <div style={{ fontSize: 14, color: "#666" }}>Current Result JSON</div>
            <pre style={{ marginTop: 8, background: "#f8f8f8", padding: 12, borderRadius: 12, overflowX: "auto", fontSize: 12 }}>
              {prettyJson(workspace.latest_outcome?.current_result ?? {})}
            </pre>
          </div>
        </div>
      </div>

      <div style={{ background: "#fff", border: "1px solid #e5e5e5", borderRadius: 16, padding: 20 }}>
        <h2>最近事件流</h2>
        <div style={{ marginTop: 12, display: "grid", gap: 10 }}>
          {recentFlowEvents.length === 0 ? (
            <div style={{ color: "#666" }}>暂无事件流记录。</div>
          ) : (
            recentFlowEvents.map((event) => (
              <div
                key={event.id}
                style={{
                  padding: 12,
                  borderRadius: 12,
                  border: "1px solid #eee",
                  background: "#fff"
                }}
              >
                <div style={{ fontWeight: 600 }}>
                  {event.trigger_type} · {event.to_status}
                </div>
                <div style={{ marginTop: 6, fontSize: 12, color: "#666" }}>
                  event_id: {event.id} · outcome_id: {event.outcome_id}
                </div>
                <div style={{ marginTop: 6, fontSize: 12, color: "#666" }}>
                  created_at: {event.created_at}
                </div>
                <pre style={{ marginTop: 8, background: "#f8f8f8", padding: 12, borderRadius: 12, overflowX: "auto", fontSize: 12 }}>
                  {event.note}
                </pre>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
