import { getOpenclawTemplateById } from "../config/openclawTemplates";

function lower(value) {
  return String(value || "").toLowerCase();
}

function includesAny(text, words) {
  const t = lower(text);
  return words.some((w) => t.includes(lower(w)));
}

export function getRecommendedOpenclawTemplate(detail) {
  if (!detail) {
    const fallback = getOpenclawTemplateById("inspect_order_submission_ui");
    return {
      templateId: fallback.id,
      reason: "No detail loaded yet, using default browser inspection template.",
    };
  }

  const latestOutcome = detail.latest_outcome || {};
  const goal = detail.goal || {};
  const nextAction = latestOutcome.next_action || {};
  const currentResult = latestOutcome.current_result || {};
  const executions = Array.isArray(detail.executions) ? detail.executions : [];

  const latestOpenclawExecution = executions.find(
    (item) => String(item.executor_name || "").toLowerCase() === "openclaw"
  );

  if (latestOpenclawExecution?.task_name) {
    return {
      templateId: latestOpenclawExecution.task_name,
      reason: "Reusing the latest OpenClaw execution template from this outcome.",
    };
  }

  const stepType = lower(nextAction.step_type);
  const goalType = lower(goal.goal_type);
  const goalText = `${goal.raw_input || ""} ${latestOutcome.title || ""}`;
  const summaryText = `${currentResult.summary || ""} ${nextAction.summary || ""}`;

  if (
    includesAny(stepType, ["review_browser_execution", "fix_browser_execution"]) ||
    includesAny(summaryText, ["browser", "submit button", "ui", "order"])
  ) {
    return {
      templateId: "inspect_order_submission_ui",
      reason: "Next action indicates a browser/UI follow-up or issue inspection.",
    };
  }

  if (
    includesAny(goalText, ["payment", "checkout", "billing"]) ||
    includesAny(summaryText, ["payment", "checkout", "billing"])
  ) {
    return {
      templateId: "locate_payment_module",
      reason: "Outcome content suggests payment-related browser analysis.",
    };
  }

  if (
    goalType === "system_understanding" ||
    includesAny(goalText, ["analyze", "understand", "context", "dashboard", "system"])
  ) {
    return {
      templateId: "collect_system_analysis_context",
      reason: "Outcome looks like a system-understanding task that needs extra browser context.",
    };
  }

  return {
    templateId: "inspect_order_submission_ui",
    reason: "Fallback to general browser inspection template.",
  };
}
