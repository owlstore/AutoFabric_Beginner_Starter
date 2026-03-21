function downloadBlob(filename, content, mimeType) {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

export function downloadJson(filename, data) {
  downloadBlob(filename, JSON.stringify(data ?? {}, null, 2), "application/json;charset=utf-8");
}

export function downloadMarkdown(filename, markdown) {
  downloadBlob(filename, markdown || "", "text/markdown;charset=utf-8");
}

function safe(v) {
  return v === null || v === undefined || v === "" ? "—" : String(v);
}

export function buildDeliveryMarkdown(detailData) {
  const goal = detailData?.goal || {};
  const latest = detailData?.latest_outcome || {};
  const current = latest?.current_result || {};
  const next = latest?.next_action || {};
  const artifacts = detailData?.artifacts || [];
  const verifications = detailData?.verifications || [];
  const executions = detailData?.executions || [];
  const flowEvents = detailData?.flow_events || [];

  const lines = [
    `# AutoFabric 交付摘要`,
    ``,
    `## 基本信息`,
    `- 目标 ID：${safe(goal.id)}`,
    `- 结果 ID：${safe(latest.id)}`,
    `- 标题：${safe(latest.title || goal.raw_input)}`,
    `- 目标类型：${safe(goal.goal_type)}`,
    `- 风险等级：${safe(goal.risk_level)}`,
    `- 当前状态：${safe(latest.status)}`,
    `- 当前阶段：${safe(current.stage)}`,
    `- 更新时间：${safe(latest.updated_at || goal.created_at)}`,
    ``,
    `## 用户目标`,
    `${safe(goal.raw_input)}`,
    ``,
    `## 当前结果`,
    `${safe(current.summary)}`,
    ``,
    `## 下一步行动`,
    `${safe(next.summary)}`,
    ``,
    `## 产物摘要`,
    `- 产物数量：${artifacts.length}`,
    `- 最近产物类型：${safe(artifacts[0]?.artifact_type || current?.artifact?.type)}`,
    `- 最近产物引用：${safe(artifacts[0]?.artifact_ref || current?.artifact?.ref)}`,
    ``,
    `## 验证摘要`,
    `- 验证记录数：${verifications.length}`,
    `- 最近验证状态：${safe(verifications[0]?.status || current?.verification?.status)}`,
    `- 最近验证器：${safe(verifications[0]?.verifier_name)}`,
    ``,
    `## 执行摘要`,
    `- 执行记录数：${executions.length}`,
    `- 最近执行任务：${safe(executions[0]?.task_name || current?.openclaw?.task_name)}`,
    `- 最近执行器：${safe(executions[0]?.executor_name || current?.openclaw?.executor)}`,
    ``,
    `## 流程事件`,
    ...flowEvents.slice(0, 10).map((item, index) => {
      return `${index + 1}. [${safe(item.trigger_type)}] ${safe(item.note)} (${safe(item.created_at)})`;
    }),
    ``,
    `## 交付判断`,
    artifacts.length > 0 || current?.artifact
      ? `当前已有产物沉淀，建议继续整理验证结论与交付说明。`
      : `当前尚未形成明确产物，建议先执行并沉淀 artifact。`,
    ``,
    `---`,
    `由 AutoFabric 工作台生成`,
  ];

  return lines.join("\n");
}
