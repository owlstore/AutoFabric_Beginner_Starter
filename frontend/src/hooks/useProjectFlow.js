import { useState, useEffect, useCallback, useRef } from "react";
import * as api from "../api/phase2Api";
import { API_BASE } from "../api/client";

const STAGE_LABELS = {
  requirement: "需求分析",
  clarification: "澄清整理",
  prototype: "原型设计",
  orchestration: "任务编排",
  execution: "代码执行",
  testing: "验证测试",
  delivery: "交付归档",
};

/**
 * Core hook: manages project list, active project, workspace snapshot, and chat timeline.
 * Manus 入口统一走 `/manus/projects/*`，由后端 autopilot 串联多阶段流程。
 * Phase 2: Uses SSE for real-time stage-by-stage streaming.
 */
export default function useProjectFlow() {
  const [projects, setProjects] = useState([]);
  const [activeProjectId, setActiveProjectId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [currentAction, setCurrentAction] = useState("");
  const [overview, setOverview] = useState(null);
  const [workspaceSnapshot, setWorkspaceSnapshot] = useState(null);

  const activeIdRef = useRef(activeProjectId);
  activeIdRef.current = activeProjectId;
  const eventSourceRef = useRef(null);

  const activeProject = overview?.project || null;

  const pushMsg = useCallback((role, type, content, stageKey, status) => {
    const msg = {
      id: `msg_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`,
      role, type, content,
      stage_key: stageKey || null,
      status: status || (role === "system" ? "completed" : null),
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, msg]);
    return msg;
  }, []);

  // --- Load project list ---
  const loadProjects = useCallback(async () => {
    try {
      const data = await api.listProjects();
      const list = Array.isArray(data) ? data : data.items || [];
      setProjects(list);
      return list;
    } catch (e) {
      console.error("loadProjects:", e);
      return [];
    }
  }, []);

  useEffect(() => {
    loadProjects();
  }, [loadProjects]);

  // Cleanup EventSource on unmount
  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }
    };
  }, []);

  // --- Select existing project ---
  const selectProject = useCallback(async (id) => {
    setActiveProjectId(id);
    setMessages([]);
    setLoading(true);
    try {
      const snapshot = await api.getManusWorkspace(id);
      setWorkspaceSnapshot(snapshot);
      setOverview(snapshot.overview);
      setMessages(rebuildMessages(snapshot.overview));
    } catch (e) {
      console.error("selectProject:", e);
      pushMsg("system", "text", `加载项目失败: ${e.message}`, null, "error");
    } finally {
      setLoading(false);
    }
  }, [pushMsg]);

  // --- Create new project (sidebar button) ---
  const createNewProject = useCallback(() => {
    setActiveProjectId(null);
    setOverview(null);
    setWorkspaceSnapshot(null);
    setMessages([]);
  }, []);

  // --- Handle send (SSE streaming for new projects) ---
  const handleSend = useCallback(async (text) => {
    if (!text.trim()) return;
    setLoading(true);

    try {
      if (!activeIdRef.current) {
        // New project: use SSE streaming bootstrap
        setCurrentAction("正在创建项目...");
        pushMsg("user", "text", text, null, null);

        const resp = await fetch(`${API_BASE}/manus/projects/bootstrap-stream`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ prompt: text }),
        });

        if (!resp.ok) {
          throw new Error(`Bootstrap failed: ${resp.status}`);
        }

        // Parse SSE stream manually since EventSource only supports GET
        const reader = resp.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          buffer += decoder.decode(value, { stream: true });

          // Parse SSE events from buffer
          const lines = buffer.split("\n");
          buffer = lines.pop() || ""; // Keep incomplete line

          let currentEvent = "";
          let currentData = "";

          for (const line of lines) {
            if (line.startsWith("event: ")) {
              currentEvent = line.slice(7).trim();
            } else if (line.startsWith("data: ")) {
              currentData = line.slice(6);
            } else if (line === "" && currentEvent) {
              // End of event — process it
              handleSSEEvent(currentEvent, currentData);
              currentEvent = "";
              currentData = "";
            }
          }
        }
      } else {
        // Existing project: resume autopilot (non-streaming for now)
        setCurrentAction("Autopilot 正在继续推进...");
        pushMsg("user", "text", text, null, null);
        const snapshot = await api.resumeManusAutopilot(activeIdRef.current, {
          operator_note: text,
        });
        setWorkspaceSnapshot(snapshot);
        setOverview(snapshot.overview);
        setMessages(rebuildMessages(snapshot.overview));
      }
    } catch (e) {
      console.error("[handleSend] error:", e);
      pushMsg("system", "text", `处理失败: ${e.message}`, null, "error");
    } finally {
      setLoading(false);
      setCurrentAction("");
    }

    function handleSSEEvent(event, dataStr) {
      let data;
      try { data = JSON.parse(dataStr); } catch { data = dataStr; }

      switch (event) {
        case "project_created": {
          const pid = data.project_id;
          setActiveProjectId(pid);
          activeIdRef.current = pid;
          setCurrentAction("Autopilot 正在运行...");
          pushMsg("system", "text", {
            _label: `项目已创建: ${data.name}`,
            project_id: pid,
          }, null, "completed");
          loadProjects();
          break;
        }
        case "stage_update": {
          const { stage_key, content } = data;
          const label = STAGE_LABELS[stage_key] || stage_key;
          setCurrentAction(`${label} 已完成`);
          pushMsg("system", `stage_${stage_key}`, {
            ...content,
            _label: `${label} — 完成`,
          }, stage_key, "completed");
          break;
        }
        case "complete": {
          setWorkspaceSnapshot(data);
          setOverview(data.overview);
          setCurrentAction("");
          break;
        }
        case "error": {
          pushMsg("system", "text", `Autopilot 错误: ${data.message || data}`, null, "error");
          break;
        }
      }
    }
  }, [pushMsg, loadProjects]);

  return {
    projects,
    activeProjectId,
    activeProject,
    messages,
    loading,
    overview,
    workspaceSnapshot,
    currentAction,
    selectProject,
    createNewProject,
    handleSend,
  };
}

// --- Rebuild messages from overview ---
function rebuildMessages(overview) {
  if (!overview) return [];
  const msgs = [];
  const so = overview.stage_objects || {};
  let n = 0;
  const mk = (role, type, content, stage, status) => ({
    id: `rebuild_${++n}`,
    role, type, content,
    stage_key: stage || null,
    status: status || "completed",
    timestamp: new Date().toISOString(),
  });

  const description = overview.project?.description || "";
  if (description.trim()) {
    const [basePrompt, ...operatorNotes] = description.split("\n\nOperator note: ");
    if (basePrompt.trim()) {
      msgs.push(mk("user", "text", basePrompt.trim(), null, null));
    }
    operatorNotes.forEach((note) => {
      if (note.trim()) {
        msgs.push(mk("user", "text", note.trim(), null, null));
      }
    });
  }

  (so.requirements || []).forEach((r) => {
    msgs.push(mk("system", "stage_requirement", r, "requirement", "completed"));
  });

  (so.clarifications || []).forEach((c) => {
    msgs.push(mk("system", "stage_clarification", {
      ...c, questions: c.questions_json, answers: c.answers_json,
    }, "clarification", c.status === "resolved" ? "completed" : "active"));
  });

  (so.prototypes || []).forEach((p) => {
    msgs.push(mk("system", "stage_prototype", {
      ...p, preview_url: `/preview/${overview.project?.id}`,
    }, "prototype", "completed"));
  });

  (so.orchestration_plans || []).forEach((o) => {
    msgs.push(mk("system", "stage_orchestration", o, "orchestration", "completed"));
  });

  (so.execution_runs || []).forEach((e) => {
    msgs.push(mk("system", "stage_execution", e, "execution", "completed"));
  });

  (so.testing_runs || []).forEach((t) => {
    msgs.push(mk("system", "stage_testing", t, "testing", "completed"));
  });

  (so.deliveries || []).forEach((d) => {
    msgs.push(mk("system", "stage_delivery", {
      ...d,
      project_id: overview.project?.id,
    }, "delivery", "completed"));
  });

  return msgs;
}
