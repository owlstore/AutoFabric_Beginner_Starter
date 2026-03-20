import { getSourceBadge } from "./workspaceUi";

export default function ParsedGoalCard({ workspace }) {
  if (!workspace) return null;

  const parsedGoal = workspace.goal?.parsed_goal ?? {};
  const riskLevel = workspace.goal?.risk_level ?? "-";
  const goalType = workspace.goal?.goal_type ?? "-";
  const nextAction = workspace.latest_outcome?.next_action ?? {};
  const parserMeta = workspace.goal?.parser_meta ?? {};

  const steps = Array.isArray(nextAction.steps) ? nextAction.steps : [];
  const sourceBadge = getSourceBadge(parserMeta.source);
  const llmEnabled = Boolean(parserMeta.llm_enabled);

  function renderEnabledLabel(value) {
    return value ? "已开启" : "未开启";
  }

  function renderExplainText(source, enabled) {
    if (source === "llm") {
      return "本次目标解析由大模型完成。";
    }
    if (source === "rules_fallback" && enabled) {
      return "本次大模型未成功返回结果，系统已自动回退到规则解析。";
    }
    if (!enabled) {
      return "当前未启用 LLM，系统使用规则解析。";
    }
    return "当前解析来源未知。";
  }

  return (
    <div style={{ background: "#fff", border: "1px solid #e5e5e5", borderRadius: 16, padding: 20 }}>
      <h2>智能解析结果</h2>

      <div style={{ marginTop: 12, padding: 12, border: "1px solid #eee", borderRadius: 12, background: "#fafafa" }}>
        <div style={{ fontSize: 13, color: "#666" }}>解析说明</div>
        <div style={{ marginTop: 6, fontSize: 15 }}>
          {renderExplainText(parserMeta.source, llmEnabled)}
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginTop: 12 }}>
        <div style={{ padding: 12, border: "1px solid #eee", borderRadius: 12 }}>
          <div style={{ fontSize: 13, color: "#666" }}>Parser Source</div>
          <div style={{ marginTop: 8 }}>
            <div style={sourceBadge.style}>{sourceBadge.label}</div>
          </div>
        </div>

        <div style={{ padding: 12, border: "1px solid #eee", borderRadius: 12 }}>
          <div style={{ fontSize: 13, color: "#666" }}>LLM Enabled</div>
          <div style={{ marginTop: 6, fontSize: 16, fontWeight: 700 }}>
            {renderEnabledLabel(llmEnabled)}
          </div>
        </div>

        <div style={{ padding: 12, border: "1px solid #eee", borderRadius: 12 }}>
          <div style={{ fontSize: 13, color: "#666" }}>Intent</div>
          <div style={{ marginTop: 6, fontSize: 16, fontWeight: 700 }}>{parsedGoal.intent ?? "-"}</div>
        </div>

        <div style={{ padding: 12, border: "1px solid #eee", borderRadius: 12 }}>
          <div style={{ fontSize: 13, color: "#666" }}>Scope</div>
          <div style={{ marginTop: 6, fontSize: 16, fontWeight: 700 }}>{parsedGoal.scope ?? "-"}</div>
        </div>

        <div style={{ padding: 12, border: "1px solid #eee", borderRadius: 12 }}>
          <div style={{ fontSize: 13, color: "#666" }}>Goal Type</div>
          <div style={{ marginTop: 6, fontSize: 16, fontWeight: 700 }}>{goalType}</div>
        </div>

        <div style={{ padding: 12, border: "1px solid #eee", borderRadius: 12 }}>
          <div style={{ fontSize: 13, color: "#666" }}>Risk Level</div>
          <div style={{ marginTop: 6, fontSize: 16, fontWeight: 700 }}>{riskLevel}</div>
        </div>
      </div>

      <div style={{ marginTop: 16, padding: 12, border: "1px solid #eee", borderRadius: 12 }}>
        <div style={{ fontSize: 13, color: "#666" }}>Target</div>
        <div style={{ marginTop: 6, fontSize: 16 }}>{parsedGoal.target ?? "-"}</div>
      </div>

      <div style={{ marginTop: 16, padding: 12, border: "1px solid #eee", borderRadius: 12 }}>
        <div style={{ fontSize: 13, color: "#666" }}>Recommended Next Action</div>
        <div style={{ marginTop: 6, fontSize: 16, fontWeight: 600 }}>{nextAction.summary ?? "-"}</div>

        <div style={{ marginTop: 10, fontSize: 13, color: "#666" }}>
          step_type: {nextAction.step_type ?? "-"}
        </div>

        <div style={{ marginTop: 12 }}>
          {steps.length === 0 ? (
            <div style={{ fontSize: 14, color: "#666" }}>暂无步骤。</div>
          ) : (
            <ol style={{ margin: 0, paddingLeft: 20 }}>
              {steps.map((step, index) => (
                <li key={index} style={{ marginTop: index === 0 ? 0 : 8 }}>
                  {step}
                </li>
              ))}
            </ol>
          )}
        </div>
      </div>
    </div>
  );
}