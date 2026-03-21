import { getSourceBadge } from "./workspaceUi";

export default function WorkspaceSummary({ workspace }) {
  return (
    <div style={{ background: "#fff", border: "1px solid #e5e5e5", borderRadius: 16, padding: 20 }}>
      <h2>Workspace 概览</h2>

      {!workspace ? (
        <div style={{ marginTop: 12, color: "#666" }}>提交后这里会显示真实 Workspace。</div>
      ) : (
        <div style={{ marginTop: 12 }}>
          <div style={{ padding: 12, border: "1px solid #eee", borderRadius: 12, marginBottom: 12 }}>
            <div style={{ color: "#666", fontSize: 14 }}>Goal</div>
            <div style={{ fontSize: 18, marginTop: 6 }}>{workspace.goal.raw_input}</div>

            <div style={{ marginTop: 12, display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
              {(() => {
                const badge = getSourceBadge(workspace.goal?.parser_meta?.source);
                return <div style={badge.style}>{badge.label}</div>;
              })()}
              <div style={{ fontSize: 12, color: "#666" }}>
                LLM：
                {workspace.goal?.parser_meta?.llm_enabled === true
                  ? "已开启"
                  : workspace.goal?.parser_meta?.llm_enabled === false
                  ? "未开启"
                  : "未知"}
              </div>
            </div>
          </div>

          <div style={{ padding: 12, border: "1px solid #eee", borderRadius: 12, marginBottom: 12 }}>
            <div style={{ color: "#666", fontSize: 14 }}>Latest Outcome</div>
            <div style={{ fontSize: 18, marginTop: 6 }}>
              {workspace.latest_outcome?.current_result?.summary ?? "暂无结果"}
            </div>
            <div style={{ marginTop: 8 }}>Stage: {workspace.latest_outcome?.current_result?.stage ?? "-"}</div>
            <div style={{ marginTop: 8 }}>Status: {workspace.latest_outcome?.status ?? "-"}</div>

            {workspace.latest_outcome?.current_result?.last_executor_message ? (
              <>
                <div style={{ marginTop: 8 }}>
                  Executor: {workspace.latest_outcome.current_result.last_executor_message}
                </div>
                <div style={{ marginTop: 8, fontSize: 12, color: "#666" }}>
                  执行模式：{workspace.latest_outcome?.current_result?.last_executor_run?.mode ?? "-"}
                </div>
              </>
            ) : null}
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12 }}>
            <div style={{ padding: 12, border: "1px solid #eee", borderRadius: 12 }}>
              <div style={{ color: "#666", fontSize: 14 }}>Outcomes</div>
              <div style={{ fontSize: 24 }}>{workspace.summary.outcome_count}</div>
            </div>
            <div style={{ padding: 12, border: "1px solid #eee", borderRadius: 12 }}>
              <div style={{ color: "#666", fontSize: 14 }}>Flow Events</div>
              <div style={{ fontSize: 24 }}>{workspace.summary.flow_event_count}</div>
            </div>
            <div style={{ padding: 12, border: "1px solid #eee", borderRadius: 12 }}>
              <div style={{ color: "#666", fontSize: 14 }}>Latest Status</div>
              <div style={{ fontSize: 24 }}>{workspace.summary.latest_status}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}