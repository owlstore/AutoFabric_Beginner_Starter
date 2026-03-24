export function normalizeObject(value) {
  if (!value) return {};
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

export function adaptWorkspace(raw) {
  if (!raw) return null;

  const goal = raw.goal || {};
  const latestOutcome = raw.latest_outcome || {};

  const parsedGoal = normalizeObject(goal.parsed_goal);
  const parserMeta = normalizeObject(goal.parser_meta || parsedGoal.parser_meta);
  const currentResult = normalizeObject(latestOutcome.current_result);
  const nextAction = normalizeObject(latestOutcome.next_action);

  return {
    ...raw,
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
  };
}

export function adaptWorkspaceList(items) {
  if (!Array.isArray(items)) return [];

  return items.map((item) => {
    const parserMeta = normalizeObject(item.parser_meta);
    const latestOutcome = item.latest_outcome || {};
    const currentResult = normalizeObject(latestOutcome.current_result);
    const nextAction = normalizeObject(latestOutcome.next_action);

    return {
      ...item,
      title:
        item.title ||
        latestOutcome.title ||
        currentResult.summary ||
        `Workspace #${item.goal_id}`,
      parser_meta: parserMeta,
      latest_outcome: {
        ...latestOutcome,
        current_result: currentResult,
        next_action: nextAction,
      },
      stage: item.stage || currentResult.stage || null,
      step_type: item.step_type || nextAction.step_type || null,
    };
  });
}