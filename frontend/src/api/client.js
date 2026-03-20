const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

async function toJson(res, errorMessage) {
  if (!res.ok) {
    throw new Error(errorMessage);
  }
  return res.json();
}

export { API_BASE };

export async function loadHealth() {
  const res = await fetch(`${API_BASE}/health`);
  return toJson(res, "加载健康检查失败");
}

export async function loadWorkspaceList() {
  const res = await fetch(`${API_BASE}/workspaces`);
  return toJson(res, "加载 Workspace 列表失败");
}

export async function loadGoalsList() {
  const res = await fetch(`${API_BASE}/goals/list-view`);
  return toJson(res, "加载目标对象列表失败");
}

export async function loadOutcomesList() {
  const res = await fetch(`${API_BASE}/outcomes/list-view`);
  return toJson(res, "加载结果对象列表失败");
}

export async function refreshWorkspace(goalId) {
  const res = await fetch(`${API_BASE}/workspace/${goalId}`);
  return toJson(res, "刷新 Workspace 失败");
}

export async function submitEntry(payload) {
  const res = await fetch(`${API_BASE}/entry/submit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return toJson(res, "入口提交失败，请检查后端服务");
}

export async function executeWorkspaceAction(goalId, payload) {
  const res = await fetch(`${API_BASE}/workspace/${goalId}/actions/execute`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return toJson(res, "动作执行失败");
}
