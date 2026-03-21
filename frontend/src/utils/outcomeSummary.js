import { formatDate } from "./formatters";

export function buildOutcomeSummaryText(detail) {
  if (!detail) return "";
  return [
    `标题：${detail.outcome_view?.title || "—"}`,
    `用户目标：${detail.goal?.raw_input || "—"}`,
    `当前结果：${detail.outcome_view?.current_result_summary || "—"}`,
    `下一步行动：${detail.outcome_view?.next_action_summary || "—"}`,
    `更新时间：${formatDate(detail.outcome_view?.updated_at)}`,
  ].join("\n\n");
}
