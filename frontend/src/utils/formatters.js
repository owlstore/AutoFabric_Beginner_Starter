import { GOAL_TYPE_LABELS, STATUS_LABELS } from "../constants/uiLabels";

export function mapStatusLabel(status) {
  const key = String(status || "").toLowerCase();
  return STATUS_LABELS[key] || status || "未知";
}

export function mapGoalTypeLabel(goalType) {
  const key = String(goalType || "").toLowerCase();
  return GOAL_TYPE_LABELS[key] || goalType || "未知类型";
}

export function formatDate(value) {
  if (!value) return "—";
  try {
    return new Date(value).toLocaleString();
  } catch {
    return String(value);
  }
}

export function truncateText(value, max = 120) {
  const text = value ? String(value) : "—";
  return text.length <= max ? text : `${text.slice(0, max)}...`;
}

export function getToneByStatus(status) {
  const s = String(status || "").toLowerCase();
  if (["ready", "completed", "passed", "success"].includes(s)) return "success";
  if (["failed", "error"].includes(s)) return "danger";
  if (["building", "running", "in_progress", "verifying"].includes(s)) return "info";
  if (["draft", "parsed", "pending"].includes(s)) return "warning";
  return "default";
}
