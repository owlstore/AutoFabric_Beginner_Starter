/**
 * Phase 2 API client — maps to the Phase 2 backend routers.
 */
import { API_BASE } from "./client";

async function req(path, options = {}) {
  const resp = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
  });
  const text = await resp.text();
  let data;
  try { data = text ? JSON.parse(text) : null; } catch { data = text; }
  if (!resp.ok) {
    const msg = (data && typeof data === "object" && (data.detail || data.error)) || text || `HTTP ${resp.status}`;
    throw new Error(String(msg));
  }
  return data;
}

function post(path, body) { return req(path, { method: "POST", body: JSON.stringify(body) }); }
function get(path) { return req(path); }

// --- Projects ---
export const listProjects = () => get("/projects");
export const createProject = (payload) => post("/projects", payload);
export const getProjectOverview = (id) => get(`/project-views/${id}/overview`);
export const bootstrapManusProject = (payload) => post("/manus/projects/bootstrap", payload);
export const getManusWorkspace = (id) => get(`/manus/projects/${id}/workspace`);
export const resumeManusAutopilot = (id, payload = {}) => post(`/manus/projects/${id}/autopilot`, payload);

// --- Requirements ---
export const createRequirement = (projectId, payload) => post(`/projects/${projectId}/requirements`, payload);
export const createRequirementFromInput = (projectId, userInput) => post(`/projects/${projectId}/requirements/from-input`, { user_input: userInput });
export const getRequirement = (id) => get(`/requirements/${id}`);
export const analyzeRequirement = (id) => post(`/requirements/${id}/analyze`, {});
export const confirmRequirement = (id) => post(`/requirements/${id}/confirm`, {});

// --- Clarifications ---
export const createClarification = (payload) => post("/clarifications", payload);
export const listClarifications = (projectId) => get(`/clarifications/by-project/${projectId}`);
export const replyClarification = (id, payload) => post(`/clarifications/${id}/reply`, payload);
export const resolveClarification = (id) => post(`/clarifications/${id}/resolve`, {});

// --- Prototypes ---
export const createPrototype = (payload) => post("/prototypes", payload);
export const listPrototypes = (projectId) => get(`/prototypes/by-project/${projectId}`);
export const generatePrototype = (id) => post(`/prototypes/${id}/generate`, {});
export const confirmPrototype = (id) => post(`/prototypes/${id}/confirm`, {});

// --- Orchestration ---
export const createOrchestrationPlan = (payload) => post("/orchestration-plans", payload);
export const listOrchestrationPlans = (projectId) => get(`/orchestration-plans/by-project/${projectId}`);
export const generateOrchestration = (id) => post(`/orchestration-plans/${id}/generate`, {});
export const approveOrchestrationPlan = (id) => post(`/orchestration-plans/${id}/approve`, {});

// --- Execution ---
export const createExecutionRun = (payload) => post("/execution-runs", payload);
export const listExecutionRuns = (projectId) => get(`/execution-runs/by-project/${projectId}`);
export const runExecution = (id) => post(`/execution-runs/${id}/run`, {});

// --- Testing ---
export const createTestingRun = (payload) => post("/testing-runs", payload);
export const listTestingRuns = (projectId) => get(`/testing-runs/by-project/${projectId}`);
export const executeTests = (id) => post(`/testing-runs/${id}/execute`, {});
export const passTestingRun = (id) => post(`/testing-runs/${id}/pass`, {});

// --- Delivery ---
export const createDelivery = (payload) => post("/deliveries", payload);
export const listDeliveries = (projectId) => get(`/deliveries/by-project/${projectId}`);
export const getDelivery = (id) => get(`/deliveries/${id}`);
