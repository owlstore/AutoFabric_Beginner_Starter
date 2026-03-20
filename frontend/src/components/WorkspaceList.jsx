import {
  clampText,
  buildCurrentSummary,
  describeStage,
  formatTime,
  getCardAccent,
  getGoalTypeBadge,
  getRiskBadge,
  getScopeBadge,
  getSimpleBadge,
  getSourceBadge,
  getStageBadge,
  getStatusBadge,
  getStepTypeBadge,
} from "./workspaceUi";

function Badge({ badge }) {
  if (!badge) return null;
  return <div style={badge.style}>{badge.label}</div>;
}

export default function WorkspaceList({ workspaceList, refreshWorkspace, isLoading, activeGoalId }) {
  return (
    <div style={{ background: "#fff", border: "1px solid #e5e5e5", borderRadius: 16, padding: 20 }}>
      <h2>最近 Workspace</h2>

      <div style={{ marginTop: 12, display: "grid", gap: 10 }}>
        {isLoading ? (
          <div style={{ color: "#666" }}>正在加载 Workspace 列表...</div>
        ) : workspaceList.length === 0 ? (
          <div style={{ color: "#666" }}>还没有历史 Workspace，先从上方创建一个。</div>
        ) : (
          workspaceList.map((item, index) => {
            const isActive = item.goal_id === activeGoalId;
            const status = item.latest_outcome?.status ?? "unknown";

            const displayTitle =
              item.title ||
              item.latest_outcome?.title ||
              item.latest_outcome?.current_result?.summary ||
              `Workspace #${item.goal_id}`;

            const currentSummary = buildCurrentSummary(
              item.latest_outcome?.current_result?.summary,
              status
            );

            const topBadges = [
              getStageBadge(item.stage),
              getStatusBadge(status),
              getGoalTypeBadge(item.goal_type),
              getScopeBadge(item.scope),
              getStepTypeBadge(item.step_type),
              getRiskBadge(item.risk_level),
              getSourceBadge(item.parser_meta?.source),
            ];

            const bottomBadges = [
              item.execution_hint_available
                ? getSimpleBadge("可执行器", "success")
                : getSimpleBadge("待推进", "neutral"),
              item.executor_touched ? getSimpleBadge("已执行器", "info") : null,
              item.executor_result_available ? getSimpleBadge("有执行结果", "success") : null,
              item.recommendation_reason_available ? getSimpleBadge("有推荐原因", "purple") : null,
              item.flow_event_count
                ? getSimpleBadge(`事件流 ${item.flow_event_count}`, "purple")
                : getSimpleBadge("无事件流", "neutral"),
            ];

            return (
              <button
                key={item.goal_id}
                onClick={() => {
                  console.log("clicked goal_id =", item.goal_id);
                  refreshWorkspace(item.goal_id);
                }}
                style={{
                  textAlign: "left",
                  padding: 12,
                  borderRadius: 12,
                  border: isActive ? "1px solid #111" : "1px solid #e5e5e5",
                  borderLeft: `4px solid ${getCardAccent(status, isActive)}`,
                  background: isActive ? "#fafafa" : "#fff",
                  cursor: "pointer",
                  boxShadow: isActive ? "0 0 0 2px rgba(17,17,17,0.04)" : "none",
                }}
              >
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    gap: 12,
                    alignItems: "flex-start",
                  }}
                >
                  <div
                    style={{
                      fontWeight: 600,
                      lineHeight: 1.4,
                      fontSize: 15,
                      display: "-webkit-box",
                      WebkitLineClamp: 1,
                      WebkitBoxOrient: "vertical",
                      overflow: "hidden",
                    }}
                  >
                    {displayTitle}
                  </div>

                  <div
                    style={{
                      display: "flex",
                      gap: 8,
                      alignItems: "center",
                      flexWrap: "wrap",
                      justifyContent: "flex-end",
                      flexShrink: 0,
                    }}
                  >
                    {index === 0 ? <Badge badge={getSimpleBadge("最近活跃", "orange")} /> : null}
                    {isActive ? <Badge badge={getSimpleBadge("当前查看", "neutral")} /> : null}
                  </div>
                </div>

                <div style={{ marginTop: 8, display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
                  {topBadges.map((badge, idx) => (
                    <Badge key={idx} badge={badge} />
                  ))}
                </div>

                <div style={{ marginTop: 6, fontSize: 12, color: "#666" }}>
                  {describeStage(item.stage)}
                </div>

                <div
                  style={{
                    marginTop: 10,
                    padding: 10,
                    borderRadius: 10,
                    background: "#fafafa",
                    border: "1px solid #eee",
                  }}
                >
                  <div style={{ fontSize: 12, color: "#666" }}>当前状态摘要</div>
                  <div style={{ marginTop: 6, fontSize: 13, color: "#333" }}>
                    {clampText(currentSummary)}
                  </div>
                </div>

                <div style={{ marginTop: 10, display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
                  <div style={{ fontSize: 11, color: "#666" }}>
                    LLM：{item.parser_meta?.llm_enabled ? "已开启" : "未开启"}
                  </div>
                  {bottomBadges.map((badge, idx) => (
                    <Badge key={idx} badge={badge} />
                  ))}
                </div>

                <div style={{ marginTop: 8, fontSize: 12, color: "#666" }}>
                  goal_id: {item.goal_id} · created_at: {formatTime(item.created_at)} · updated_at:{" "}
                  {formatTime(item.updated_at)}
                </div>
              </button>
            );
          })
        )}
      </div>
    </div>
  );
}