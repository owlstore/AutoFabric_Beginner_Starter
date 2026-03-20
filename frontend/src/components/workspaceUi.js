export function pillStyle(background, color, border) {
  return {
    display: "inline-flex",
    alignItems: "center",
    padding: "4px 8px",
    borderRadius: 999,
    fontSize: 11,
    fontWeight: 700,
    background,
    color,
    border,
    lineHeight: 1.2,
  };
}

export function formatTime(value) {
  if (!value) return "-";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString();
}

export function clampText(text, max = 72) {
  if (!text) return "-";
  if (text.length <= max) return text;
  return text.slice(0, max - 3).trimEnd() + "...";
}

export function buildCurrentSummary(summary, status) {
  if (summary && summary.trim()) return summary.trim();
  if (status === "draft") return "该 Workspace 已创建，等待进入下一步推进。";
  if (status === "in_progress") return "该 Workspace 正在推进中，等待更多执行结果。";
  if (status === "completed") return "该 Workspace 已完成，可回看结果与事件流。";
  return "该 Workspace 暂无可显示摘要。";
}

export function buildNextActionSummary(summary, status) {
  if (summary && summary.trim()) return summary.trim();
  if (status === "completed") return "当前记录已完成，暂无下一步动作。";
  if (status === "in_progress") return "系统正在根据当前状态准备下一步动作。";
  return "等待进入下一步动作生成。";
}

export function describeStage(stage) {
  if (stage === "goal_captured") return "已完成初始解析，等待进入下一步推进。";
  if (stage === "analysis_collecting") return "正在补充系统分析所需的结构与依赖上下文。";
  if (stage === "context_collecting") return "正在收集执行或判断下一步所需的上下文。";
  if (stage === "next_stage") return "当前结果已经推进，系统正进入新的处理阶段。";
  return "当前阶段暂无说明。";
}

export function getCardAccent(status, isActive) {
  if (isActive) return "#111";
  if (status === "in_progress") return "#2457c5";
  if (status === "completed") return "#0a7a33";
  return "#e5e5e5";
}

export function getSimpleBadge(label, kind = "neutral") {
  const map = {
    neutral: pillStyle("#f5f5f5", "#666", "1px solid #e5e5e5"),
    success: pillStyle("#eefaf0", "#0a7a33", "1px solid #cfead7"),
    info: pillStyle("#eef4ff", "#2457c5", "1px solid #cfe0ff"),
    warn: pillStyle("#fff8e8", "#9a6700", "1px solid #f0dfb4"),
    purple: pillStyle("#f3f0ff", "#6941c6", "1px solid #ddd6fe"),
    orange: pillStyle("#fff3f0", "#b54708", "1px solid #ffd8cc"),
    danger: pillStyle("#fff1f1", "#b00020", "1px solid #f2caca"),
  };
  return { label, style: map[kind] || map.neutral };
}

export function getSourceBadge(source) {
  if (source === "llm") return getSimpleBadge("LLM 解析", "success");
  if (source === "rules_fallback") return getSimpleBadge("规则兜底", "warn");
  return getSimpleBadge("未知来源", "neutral");
}

export function getStatusBadge(status) {
  if (status === "in_progress") return getSimpleBadge("进行中", "info");
  if (status === "completed") return getSimpleBadge("已完成", "success");
  return getSimpleBadge("草稿", "neutral");
}

export function getRiskBadge(risk) {
  if (risk === "medium") return getSimpleBadge("中风险", "warn");
  if (risk === "high") return getSimpleBadge("高风险", "danger");
  return getSimpleBadge("低风险", "neutral");
}

export function getGoalTypeBadge(goalType) {
  if (goalType === "system_understanding") return getSimpleBadge("系统理解", "info");
  if (goalType === "bug_fix") return getSimpleBadge("问题修复", "danger");
  if (goalType === "system_build") return getSimpleBadge("系统构建", "success");
  return getSimpleBadge("通用任务", "neutral");
}

export function getScopeBadge(scope) {
  if (scope === "frontend") return getSimpleBadge("前端", "info");
  if (scope === "backend") return getSimpleBadge("后端", "purple");
  if (scope === "infra") return getSimpleBadge("基础设施", "success");
  if (scope === "data") return getSimpleBadge("数据", "warn");
  return getSimpleBadge("未指定", "neutral");
}

export function getStageBadge(stage) {
  if (stage === "goal_captured") return getSimpleBadge("已捕获目标", "neutral");
  if (stage === "analysis_collecting") return getSimpleBadge("分析采集中", "info");
  if (stage === "context_collecting") return getSimpleBadge("上下文采集中", "warn");
  if (stage === "next_stage") return getSimpleBadge("已进入下一阶段", "success");
  return getSimpleBadge("阶段未标记", "neutral");
}

export function getStepTypeBadge(stepType) {
  if (stepType === "analyze_system") return getSimpleBadge("分析阶段", "info");
  if (stepType === "collect_context") return getSimpleBadge("收集上下文", "warn");
  if (stepType === "define_build_scope") return getSimpleBadge("定义构建范围", "success");
  if (stepType === "clarify_goal") return getSimpleBadge("澄清目标", "neutral");
  return getSimpleBadge("未指定步骤", "neutral");
}