function normalizeStatus(status) {
  const s = String(status || "").toLowerCase();
  if (["completed", "passed", "success"].includes(s)) return "completed";
  if (["failed", "error"].includes(s)) return "failed";
  if (["running", "building", "in_progress", "verifying", "accepted"].includes(s)) return "running";
  return "draft";
}

export function statusTone(status) {
  const s = normalizeStatus(status);
  if (s === "completed") return "success";
  if (s === "failed") return "danger";
  if (s === "running") return "info";
  return "default";
}

export function statusLabel(status) {
  const s = normalizeStatus(status);
  if (s === "completed") return "已完成";
  if (s === "failed") return "失败";
  if (s === "running") return "执行中";
  return "草稿";
}

export function goalTypeLabel(goalType) {
  const v = String(goalType || "");
  if (v === "system_build") return "系统构建";
  if (v === "system_understanding") return "系统理解";
  if (v === "browser_automation") return "浏览器自动化";
  if (v === "general_task") return "通用任务";
  if (v === "general") return "通用任务";
  return v || "未知类型";
}

export function stageLabelFromKey(stageKey) {
  const map = {
    requirement: "需求阶段",
    clarification: "澄清阶段",
    prototype: "原型阶段",
    orchestration: "编排阶段",
    execution: "Agent 执行阶段",
    testing: "测试阶段",
    delivery: "交付阶段",
    unknown: "待识别阶段",
  };
  return map[String(stageKey || "")] || String(stageKey || "待识别阶段");
}

function truncate(text, max = 90) {
  const s = String(text || "—");
  return s.length > max ? `${s.slice(0, max)}...` : s;
}

export function buildCardsFromWorkspaces(payload) {
  const items = payload?.items || [];
  return items.map((item) => {
    const latest = item.latest_outcome || {};
    return {
      goal_id: item.goal_id,
      outcome_id: latest.id,
      title: item.title || latest.title || `结果 #${latest.id || item.goal_id}`,
      status: latest.status,
      statusLabel: statusLabel(latest.status),
      statusTone: statusTone(latest.status),
      goalType: item.goal_type,
      goalTypeLabel: goalTypeLabel(item.goal_type),
      stageKey: item.stage_key || item.stage || latest.stage_key || "unknown",
      stageLabel: item.stage_label || latest.stage_label || stageLabelFromKey(item.stage_key || item.stage),
      rawStage: item.raw_stage || latest.raw_stage || latest.current_result?.stage || null,
      currentResult: truncate(latest.current_result?.summary || "暂无结果摘要"),
      nextAction: truncate(latest.next_action?.summary || "暂无下一步行动"),
      updatedAt: latest.updated_at || item.updated_at || item.created_at || "—",
    };
  });
}

export function buildStatsFromWorkspaces(payload) {
  const items = payload?.items || [];
  let completed = 0;
  let running = 0;
  let failed = 0;

  for (const item of items) {
    const status = normalizeStatus(item?.latest_outcome?.status);
    if (status === "completed") completed += 1;
    else if (status === "running") running += 1;
    else if (status === "failed") failed += 1;
  }

  return {
    total: items.length,
    completed,
    running,
    failed,
  };
}

export function buildStageCounts(payload) {
  const raw = payload?.stage_counts || {};
  return {
    requirement: Number(raw.requirement || 0),
    clarification: Number(raw.clarification || 0),
    prototype: Number(raw.prototype || 0),
    orchestration: Number(raw.orchestration || 0),
    execution: Number(raw.execution || 0),
    testing: Number(raw.testing || 0),
    delivery: Number(raw.delivery || 0),
    unknown: Number(raw.unknown || 0),
  };
}

export function buildDetailView(detail) {
  const goal = detail?.goal || {};
  const latest = detail?.latest_outcome || {};
  const currentResult = latest?.current_result || {};
  const nextAction = latest?.next_action || {};
  const recommendedTemplate =
    currentResult?.openclaw?.task_name ||
    nextAction?.step_type ||
    "collect_system_analysis_context";

  return {
    goalId: goal.id,
    outcomeId: latest.id,
    title: latest.title || goal.raw_input || "—",
    statusLabel: statusLabel(latest.status),
    statusTone: statusTone(latest.status),
    goalTypeLabel: goalTypeLabel(goal.goal_type),
    stageKey: latest.stage_key || "unknown",
    stageLabel: latest.stage_label || stageLabelFromKey(latest.stage_key),
    rawStage: latest.raw_stage || currentResult.stage || "—",
    currentResult: currentResult.summary || "暂无结果摘要",
    nextAction: nextAction.summary || "暂无下一步行动",
    rawInput: goal.raw_input || "—",
    recommendedTemplate,
    recommendedReason:
      nextAction.summary ||
      "当前结果适合继续沿推荐执行方式推进。",
    updatedAt: latest.updated_at || goal.created_at || "—",
    detailSections: detail?.detail_sections || [],
  };
}
