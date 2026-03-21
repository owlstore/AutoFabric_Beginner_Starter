function normalizeObject(value) {
  if (value === null || value === undefined) return {};
  if (typeof value === "object" && !Array.isArray(value)) return value;

  if (typeof value === "string") {
    try {
      const parsed = JSON.parse(value);
      if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) {
        return parsed;
      }
    } catch {
      return {};
    }
  }

  return {};
}

function normalizeArray(value) {
  return Array.isArray(value) ? value : [];
}

function firstNonEmpty(...values) {
  for (const value of values) {
    if (value !== null && value !== undefined && String(value).trim() !== "") {
      return value;
    }
  }
  return "";
}

function buildCurrentResultSummary(currentResult, fallbackStatus) {
  if (!currentResult || typeof currentResult !== "object") {
    return fallbackStatus || "No current result yet.";
  }

  return firstNonEmpty(
    currentResult.summary,
    currentResult.message,
    currentResult.result,
    currentResult.description,
    fallbackStatus || "No current result yet."
  );
}

function buildNextActionSummary(nextAction) {
  if (!nextAction || typeof nextAction !== "object") {
    return "No next action suggested yet.";
  }

  return firstNonEmpty(
    nextAction.summary,
    nextAction.label,
    nextAction.action,
    nextAction.step_type,
    "No next action suggested yet."
  );
}

function buildVerificationSummary(latestOutcome) {
  const currentResult = normalizeObject(latestOutcome?.current_result);
  const verification =
    normalizeObject(currentResult.verification_summary).critical_failed !== undefined
      ? normalizeObject(currentResult.verification_summary)
      : normalizeObject(currentResult.verification);

  if (verification && Object.keys(verification).length > 0) {
    return verification;
  }

  return {
    status: latestOutcome?.status || "unknown",
    note: "Verification summary not available yet.",
  };
}

function buildArtifactSummary(latestOutcome) {
  const currentResult = normalizeObject(latestOutcome?.current_result);
  const artifactSummary = normalizeArray(currentResult.artifact_summary);

  if (artifactSummary.length > 0) return artifactSummary;

  const artifact = normalizeObject(currentResult.artifact);
  if (Object.keys(artifact).length > 0) return [artifact];

  return [];
}

export function adaptWorkspaceListToOutcomeCards(items) {
  if (!Array.isArray(items)) return [];

  return items.map((item) => {
    const latestOutcome = item?.latest_outcome || {};
    const currentResult = normalizeObject(latestOutcome.current_result);
    const nextAction = normalizeObject(latestOutcome.next_action);
    const parserMeta = normalizeObject(item.parser_meta);

    const title = firstNonEmpty(
      latestOutcome.title,
      item.title,
      currentResult.summary,
      `Outcome for Goal #${item.goal_id}`
    );

    return {
      id: latestOutcome.id ?? `goal-${item.goal_id}`,
      outcome_id: latestOutcome.id ?? null,
      goal_id: item.goal_id,
      title,
      goal_type: item.goal_type || parserMeta.goal_type || "unknown",
      scope: item.scope || "unspecified",
      risk_level: item.risk_level || "unknown",
      stage: item.stage || currentResult.stage || latestOutcome.status || "unknown",
      status: latestOutcome.status || "unknown",
      current_result_summary: buildCurrentResultSummary(currentResult, latestOutcome.status),
      next_action_summary: buildNextActionSummary(nextAction),
      verification_summary: buildVerificationSummary(latestOutcome),
      artifact_summary: buildArtifactSummary(latestOutcome),
      parser_meta: parserMeta,
      latest_outcome: {
        ...latestOutcome,
        current_result: currentResult,
        next_action: nextAction,
      },
      created_at: item.created_at,
      updated_at: item.updated_at,
      raw_workspace_item: item,
    };
  });
}

export function adaptWorkspaceDetailToOutcomeDetail(raw) {
  if (!raw) return null;

  const goal = raw.goal || {};
  const latestOutcome = raw.latest_outcome || {};
  const parsedGoal = normalizeObject(goal.parsed_goal);
  const parserMeta = normalizeObject(goal.parser_meta || parsedGoal.parser_meta);
  const currentResult = normalizeObject(latestOutcome.current_result);
  const nextAction = normalizeObject(latestOutcome.next_action);

  const outcomeTitle = firstNonEmpty(
    latestOutcome.title,
    currentResult.summary,
    goal.raw_input,
    `Outcome for Goal #${goal.id}`
  );

  return {
    goal: {
      ...goal,
      parsed_goal: parsedGoal,
      parser_meta: parserMeta,
    },
    latest_outcome: {
      ...latestOutcome,
      current_result: currentResult,
      next_action: nextAction,
    },
    outcomes: normalizeArray(raw.outcomes).map((item) => ({
      ...item,
      current_result: normalizeObject(item.current_result),
      next_action: normalizeObject(item.next_action),
    })),
    executions: normalizeArray(raw.executions),
    artifacts: normalizeArray(raw.artifacts),
    verifications: normalizeArray(raw.verifications),
    flow_events: normalizeArray(raw.flow_events),
    summary: raw.summary || {},
    outcome_view: {
      id: latestOutcome.id ?? null,
      goal_id: goal.id,
      title: outcomeTitle,
      status: latestOutcome.status || "unknown",
      current_result_summary: buildCurrentResultSummary(currentResult, latestOutcome.status),
      current_result: currentResult,
      next_action_summary: buildNextActionSummary(nextAction),
      next_action: nextAction,
      risk_boundary: latestOutcome.risk_boundary ?? null,
      verification_summary: buildVerificationSummary(latestOutcome),
      artifact_summary: buildArtifactSummary(latestOutcome),
      updated_at: latestOutcome.updated_at || goal.created_at || null,
    },
  };
}
