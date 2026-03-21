import { getOpenclawTemplateById } from "../config/openclawTemplates";

function getLastExecutionSummary(executions) {
  const latest = executions?.filter((item) => item.executor_name === "openclaw").slice(-1)[0];
  return latest
    ? {
        task_name: latest.task_name,
        status: latest.status,
        returncode: latest.returncode,
        message: latest.output_payload?.stdout?.message || latest.output_payload?.message,
      }
    : null;
}

export function optimizeExecution({ currentOutcome, latestExecution }) {
  if (!currentOutcome || !latestExecution) {
    return { nextAction: "retry", templateId: "inspect_order_submission_ui" };
  }

  const isExecutionFailed = latestExecution.status === "failed" || latestExecution.returncode !== 0;
  if (isExecutionFailed) {
    return { nextAction: "retry", templateId: latestExecution.task_name || "inspect_order_submission_ui" };
  }

  const isActionAlreadyCompleted = currentOutcome.latest_outcome?.next_action?.step_type === "completed";
  if (isActionAlreadyCompleted) {
    return { nextAction: "done", templateId: "inspect_order_submission_ui" };
  }

  if (currentOutcome.latest_outcome?.next_action?.step_type === "review_browser_execution") {
    return {
      nextAction: "review",
      templateId: getOpenclawTemplateById("inspect_order_submission_ui").id,
    };
  }

  return { nextAction: "proceed", templateId: latestExecution.task_name || "inspect_order_submission_ui" };
}
