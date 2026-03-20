import { useEffect, useMemo, useState } from "react";
import { API_BASE } from "./config";
import WorkspaceList from "./components/WorkspaceList";
import WorkspaceSummary from "./components/WorkspaceSummary";
import ParsedGoalCard from "./components/ParsedGoalCard";
import ActionPanel from "./components/ActionPanel";
import ExecutorPanel from "./components/ExecutorPanel";
import GoalsListPanel from "./components/GoalsListPanel";
import OutcomesListPanel from "./components/OutcomesListPanel";
import { adaptWorkspace, adaptWorkspaceList } from "./adapters/workspaceAdapter";

export default function App() {
  const [userInput, setUserInput] = useState("");
  const [workspace, setWorkspace] = useState(null);

  const [workspaceList, setWorkspaceList] = useState([]);
  const [isLoadingWorkspaceList, setIsLoadingWorkspaceList] = useState(false);

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isExecuting, setIsExecuting] = useState(false);

  const [goalsList, setGoalsList] = useState([]);
  const [outcomesList, setOutcomesList] = useState([]);
  const [goalsLoaded, setGoalsLoaded] = useState(false);
  const [outcomesLoaded, setOutcomesLoaded] = useState(false);

  const [errorMessage, setErrorMessage] = useState("");

  const actionPanel = useMemo(() => {
    return Array.isArray(workspace?.action_panel) ? workspace.action_panel : [];
  }, [workspace]);

  const latestOutcome = workspace?.latest_outcome ?? null;
  const lastExecutorRun = latestOutcome?.current_result?.last_executor_run ?? null;
  const lastExecutorMessage = latestOutcome?.current_result?.last_executor_message ?? "";

  async function fetchJson(url, options = {}) {
    const response = await fetch(url, {
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {}),
      },
      ...options,
    });

    const contentType = response.headers.get("content-type") || "";
    const isJson = contentType.includes("application/json");

    if (!response.ok) {
      let detail = `${response.status} ${response.statusText}`;
      if (isJson) {
        const data = await response.json();
        detail = data?.detail || JSON.stringify(data);
      } else {
        detail = await response.text();
      }
      throw new Error(detail);
    }

    return isJson ? response.json() : null;
  }

  async function loadWorkspaceList() {
    try {
      setIsLoadingWorkspaceList(true);
      setErrorMessage("");

      const data = await fetchJson(`${API_BASE}/workspaces`);
      const items = adaptWorkspaceList(data?.items);
      setWorkspaceList(items); 

      if ((!workspace || !workspace.goal?.id) && items.length > 0) {
        const firstGoalId = items[0].goal_id;
        await syncWorkspace(firstGoalId);
      }
    } catch (error) {
      console.error("loadWorkspaceList error:", error);
      setErrorMessage(`加载 Workspace 列表失败：${error.message}`);
    } finally {
      setIsLoadingWorkspaceList(false);
    }
  }

  async function syncWorkspace(goalId) {
    try {
      setErrorMessage("");
      console.log("syncWorkspace goalId =", goalId);
      const data = await fetchJson(`${API_BASE}/workspaces/${goalId}`);
      console.log("workspace detail =", data);
      setWorkspace(adaptWorkspace(data));
    } catch (error) {
      console.error("syncWorkspace error:", error);
      setErrorMessage(`加载 Workspace 详情失败：${error.message}`);
    }
  }

  async function handleCreateWorkspace(event) {
    event.preventDefault();

    const value = userInput.trim();
    if (!value) {
      setErrorMessage("请输入目标描述。");
      return;
    }

    try {
      setIsSubmitting(true);
      setErrorMessage("");

      const data = await fetchJson(`${API_BASE}/entry/submit`, {
        method: "POST",
        body: JSON.stringify({
          user_input: value,
        }),
      });

      setWorkspace(adaptWorkspace(data));
      setUserInput("");
      await loadWorkspaceList();
    } catch (error) {
      console.error("handleCreateWorkspace error:", error);
      setErrorMessage(`创建 Workspace 失败：${error.message}`);
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleAction(actionItem) {
    if (!workspace) return;

    try {
      setIsExecuting(true);
      setErrorMessage("");

      if (actionItem.action_type === "progress_outcome") {
        const outcomeId = workspace?.latest_outcome?.id;
        if (!outcomeId) {
          throw new Error("当前没有可推进的 outcome_id");
        }

        await fetchJson(`${API_BASE}/outcomes/${outcomeId}/progress`, {
          method: "POST",
          body: JSON.stringify({
            status: "in_progress",
            stage: "next_stage",
            summary: `Progress updated for ${workspace.goal?.raw_input ?? "current workspace"}.`,
          }),
        });

        await syncWorkspace(workspace.goal.id);
        await loadWorkspaceList();
        return;
      }

      if (actionItem.action_type === "run_executor") {
        const goalId = workspace?.goal?.id;
        const outcomeId = workspace?.latest_outcome?.id;
        const stepType = workspace?.latest_outcome?.next_action?.step_type ?? "collect_context";
        const summary =
          workspace?.latest_outcome?.next_action?.summary ??
          workspace?.latest_outcome?.current_result?.summary ??
          "Run executor for current workspace.";

        if (!goalId || !outcomeId) {
          throw new Error("缺少 goal_id 或 outcome_id，无法执行执行器");
        }

        await fetchJson(`${API_BASE}/executors/openclaw/run`, {
          method: "POST",
          body: JSON.stringify({
            task_name: "collect_system_analysis_context",
            payload: {
              goal_id: goalId,
              outcome_id: outcomeId,
              step_type: stepType,
              action: "collect_system_context",
              context: {
                intent: workspace?.goal?.parsed_goal?.intent,
                scope: workspace?.goal?.parsed_goal?.scope,
                target: workspace?.goal?.parsed_goal?.target,
                summary,
              },
            },
          }),
        });

        await syncWorkspace(goalId);
        await loadWorkspaceList();
        return;
      }

      if (actionItem.action_type === "view_goals") {
        const data = await fetchJson(`${API_BASE}/goals/list-view`);
        setGoalsList(Array.isArray(data?.items) ? data.items : []);
        setGoalsLoaded(true);
        return;
      }

      if (actionItem.action_type === "view_outcomes") {
        const data = await fetchJson(`${API_BASE}/outcomes`);
        setOutcomesList(Array.isArray(data?.items) ? data.items : []);
        setOutcomesLoaded(true);
        return;
      }

      console.warn("未处理的 action_type:", actionItem.action_type);
    } catch (error) {
      console.error("handleAction error:", error);
      setErrorMessage(`动作执行失败：${error.message}`);
    } finally {
      setIsExecuting(false);
    }
  }

  useEffect(() => {
    loadWorkspaceList();
  }, []);

  return (
    <div style={{ minHeight: "100vh", background: "#f7f7f8", color: "#111" }}>
      <div style={{ maxWidth: 1440, margin: "0 auto", padding: 24 }}>
        <div style={{ marginBottom: 20, textAlign: "center" }}>
          <h1 style={{ margin: 0, fontSize: 28 }}>AutoFabric Workspace</h1>
          <div style={{ marginTop: 8, color: "#666" }}>
            本地智能工作台：目标解析、Workspace 浏览、动作推进与执行器联动。
          </div>
        </div>

        <form
          onSubmit={handleCreateWorkspace}
          style={{
            background: "#fff",
            border: "1px solid #e5e5e5",
            borderRadius: 16,
            padding: 20,
            marginBottom: 20,
          }}
        >
          <div style={{ fontSize: 14, color: "#666", marginBottom: 8, textAlign: "center" }}>
            创建新 Workspace
          </div>

          <textarea
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            placeholder="例如：I need to understand the legacy order dashboard before refactoring it"
            style={{
              width: "100%",
              minHeight: 96,
              borderRadius: 12,
              border: "1px solid #ddd",
              padding: 12,
              fontSize: 14,
              resize: "vertical",
              boxSizing: "border-box",
            }}
          />

          <div style={{ marginTop: 12, display: "flex", gap: 12, alignItems: "center" }}>
            <button
              type="submit"
              disabled={isSubmitting}
              style={{
                padding: "10px 16px",
                borderRadius: 10,
                border: "1px solid #111",
                background: "#111",
                color: "#fff",
                fontWeight: 600,
                cursor: "pointer",
              }}
            >
              {isSubmitting ? "创建中..." : "创建 Workspace"}
            </button>

            {errorMessage ? <div style={{ color: "#b00020", fontSize: 13 }}>{errorMessage}</div> : null}
          </div>
        </form>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "420px minmax(0, 1fr)",
            gap: 20,
            alignItems: "start",
          }}
        >
          <div style={{ display: "grid", gap: 20 }}>
            <WorkspaceList
              workspaceList={workspaceList}
              refreshWorkspace={syncWorkspace}
              isLoading={isLoadingWorkspaceList}
              activeGoalId={workspace?.goal?.id}
            />

            <GoalsListPanel goalsList={goalsList} hasLoaded={goalsLoaded} />
            <OutcomesListPanel outcomesList={outcomesList} hasLoaded={outcomesLoaded} />
          </div>

          <div style={{ display: "grid", gap: 20 }}>
            <WorkspaceSummary workspace={workspace} />
            <ParsedGoalCard workspace={workspace} />
            <ActionPanel
              workspace={workspace}
              actionPanel={actionPanel}
              handleAction={handleAction}
              isExecuting={isExecuting}
            />
            <ExecutorPanel
              lastExecutorRun={lastExecutorRun}
              lastExecutorMessage={lastExecutorMessage}
            />
          </div>
        </div>
      </div>
    </div>
  );
}