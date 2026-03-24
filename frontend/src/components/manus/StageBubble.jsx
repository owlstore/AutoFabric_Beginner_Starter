import { useState } from "react";
import { STAGE_LABELS } from "../../constants/stages";
import { API_BASE } from "../../api/client";
import QuarkButton from "../quark/QuarkButton";
import MarkdownBlock from "./MarkdownBlock";
import CodePreview from "./CodePreview";
import MermaidDiagram from "./MermaidDiagram";

const STATUS_CFG = {
  completed: { icon: "check", text: "已完成", color: "text-green-400" },
  active:    { icon: "dot",   text: "进行中", color: "text-blue-400" },
  error:     { icon: "x",     text: "失败",   color: "text-red-400" },
  pending:   { icon: "dot",   text: "等待中", color: "text-[#52525b]" },
};

function CheckIcon() {
  return (
    <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
      <path
        d="M2.5 6.5L5 9l4.5-6"
        stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"
        style={{ strokeDasharray: 16, animation: "check-draw 0.4s ease forwards" }}
      />
    </svg>
  );
}

export default function StageBubble({ message }) {
  const stage = message.stage_key;
  const label = STAGE_LABELS[stage] || stage || "系统";
  const sc = STATUS_CFG[message.status] || STATUS_CFG.completed;
  const isApproval = message.type === "approval";

  return (
    <div className="flex justify-start">
      <div className="max-w-[88%] flex items-start gap-2.5">
        {/* Avatar */}
        <div className={`w-7 h-7 rounded-lg flex items-center justify-center shrink-0 ${isApproval ? "bg-amber-900/30" : "bg-[#1e1e28]"}`}>
          {isApproval ? (
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
              <path d="M7 1v5M7 9v1" stroke="#f59e0b" strokeWidth="2" strokeLinecap="round"/>
            </svg>
          ) : (
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
              <path d="M7 1L1.5 4l5.5 3 5.5-3L7 1zM1.5 10l5.5 3 5.5-3M1.5 7l5.5 3 5.5-3" stroke="#60a5fa" strokeWidth="1" strokeLinejoin="round" strokeLinecap="round"/>
            </svg>
          )}
        </div>

        {/* Card */}
        <div className={`group rounded-2xl rounded-tl-md border px-4 py-3 shadow-lg shadow-black/10 min-w-[200px] max-w-full ${isApproval ? "border-amber-500/30 bg-amber-950/30" : "border-[#1e1e28] bg-[#16161a]"}`}>
          {/* Header row */}
          <div className="flex items-center gap-2 mb-2">
            {stage && (
              <span className={`inline-flex items-center rounded-md px-2 py-0.5 text-[11px] font-medium stage-pill-${stage}`}>
                {label}
              </span>
            )}
            <span className={`flex items-center gap-1 text-[11px] ${isApproval ? "text-amber-400" : sc.color}`}>
              {isApproval ? (
                <>
                  <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" />
                  等待审批
                </>
              ) : (
                <>
                  {sc.icon === "check" && <CheckIcon />}
                  {sc.icon === "dot" && <span className="w-1.5 h-1.5 rounded-full bg-current" />}
                  {sc.text}
                </>
              )}
            </span>
            {!isApproval && message.status === "completed" && stage && message.content?.project_id && (
              <RerunButton projectId={message.content.project_id} stage={stage} />
            )}
          </div>

          {/* Content */}
          <div className="text-[13px] text-[#a1a1aa] leading-relaxed">
            {isApproval ? (
              <ApprovalContent c={message.content} />
            ) : (
              renderStageContent(stage, message.content)
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function renderStageContent(stage, c) {
  if (!c) return <span className="text-[#52525b]">-</span>;
  if (typeof c === "string") return <p className="whitespace-pre-wrap">{c}</p>;

  switch (stage) {
    case "requirement":
      return <RequirementContent c={c} />;
    case "prototype":
      return <PrototypeContent c={c} />;
    case "orchestration":
      return <OrchestrationContent c={c} />;
    case "execution":
      return <ExecutionContent c={c} />;
    case "testing":
      return <TestingContent c={c} />;
    case "delivery":
      return <DeliveryContent c={c} />;
    default:
      return <GenericContent c={c} />;
  }
}

// --- Stage-specific renderers ---

function RequirementContent({ c }) {
  const analysis = c.llm_analysis;
  return (
    <div className="space-y-2">
      {c._label && <p className="text-white font-medium">{c._label}</p>}
      {c.title && <p className="text-white">{c.title}</p>}
      {c.summary && <p className="text-[#a1a1aa]">{c.summary}</p>}
      {analysis && (
        <div className="mt-2 space-y-1.5">
          {analysis.goal_type && <Badge label="类型" value={analysis.goal_type} />}
          {analysis.risk_level && <Badge label="风险" value={analysis.risk_level} />}
          {analysis.estimated_complexity && <Badge label="复杂度" value={analysis.estimated_complexity} />}
          {analysis.functional_requirements?.length > 0 && (
            <div>
              <span className="text-[11px] text-[#52525b]">功能需求</span>
              <ul className="list-disc list-inside ml-1 text-[12px]">
                {analysis.functional_requirements.slice(0, 5).map((r, i) => (
                  <li key={i}>{r}</li>
                ))}
              </ul>
            </div>
          )}
          {analysis.tech_stack_suggestion && (
            <div className="flex flex-wrap gap-1 mt-1">
              {Object.entries(analysis.tech_stack_suggestion).map(([k, v]) => (
                v && <span key={k} className="px-1.5 py-0.5 rounded bg-[#1e1e28] text-[11px] text-blue-400">{k}: {v}</span>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function PrototypeContent({ c }) {
  const [showPreview, setShowPreview] = useState(false);
  const [showArch, setShowArch] = useState(false);
  const [showCode, setShowCode] = useState(false);
  const [viewport, setViewport] = useState("100%");

  // Extract mermaid from page_flow_json or module_map_json
  const mermaidCode = c.page_flow_json?.mermaid || c.module_map_json?.mermaid || null;

  // Build files array from generated_files if present
  const codeFiles = Array.isArray(c.generated_files) ? c.generated_files : [];

  return (
    <div className="space-y-2">
      {c._label && <p className="text-white font-medium">{c._label}</p>}
      {c.files_generated != null && (
        <p className="text-[12px]">生成了 {c.files_generated} 个文件</p>
      )}
      {/* IA summary */}
      {c.ia_json?.pages && (
        <div>
          <span className="text-[11px] text-[#52525b]">页面</span>
          <div className="flex flex-wrap gap-1 mt-0.5">
            {c.ia_json.pages.map((p, i) => (
              <span key={i} className="px-1.5 py-0.5 rounded bg-[#1e1e28] text-[11px]">{p.name || p}</span>
            ))}
          </div>
        </div>
      )}
      {/* API design summary */}
      {Array.isArray(c.api_draft_json) && c.api_draft_json.length > 0 && (
        <div>
          <span className="text-[11px] text-[#52525b]">API 设计</span>
          <div className="mt-0.5 space-y-0.5">
            {c.api_draft_json.slice(0, 4).map((a, i) => (
              <div key={i} className="text-[11px] font-mono">
                <span className="text-green-400">{a.method}</span> {a.path}
              </div>
            ))}
          </div>
        </div>
      )}
      {/* Mermaid architecture diagram */}
      {mermaidCode && (
        <div className="mt-2">
          <QuarkButton
            onClick={() => setShowArch(!showArch)}
            variant="raw"
            className="px-3 py-1 text-[12px] rounded-lg bg-purple-600/20 text-purple-400 hover:bg-purple-600/30 transition"
          >
            {showArch ? "隐藏架构图" : "查看架构图"}
          </QuarkButton>
          {showArch && <MermaidDiagram code={mermaidCode} className="mt-2" />}
        </div>
      )}
      {/* Code files preview */}
      {codeFiles.length > 0 && (
        <div className="mt-2">
          <QuarkButton
            onClick={() => setShowCode(!showCode)}
            variant="raw"
            className="px-3 py-1 text-[12px] rounded-lg bg-cyan-600/20 text-cyan-400 hover:bg-cyan-600/30 transition"
          >
            {showCode ? "隐藏代码" : `查看代码 (${codeFiles.length} 文件)`}
          </QuarkButton>
          {showCode && <CodePreview files={codeFiles} className="mt-2" />}
        </div>
      )}
      {/* Preview button + iframe with viewport switching */}
      {c.preview_url && (
        <div className="mt-2">
          <div className="flex items-center gap-2 flex-wrap">
            <QuarkButton
              onClick={() => setShowPreview(!showPreview)}
              variant="raw"
              className="px-3 py-1 text-[12px] rounded-lg bg-blue-600/20 text-blue-400 hover:bg-blue-600/30 transition"
            >
              {showPreview ? "隐藏预览" : "查看原型预览"}
            </QuarkButton>
            {showPreview && (
              <div className="flex gap-1">
                {[
                  { label: "桌面", w: "100%" },
                  { label: "平板", w: "768px" },
                  { label: "手机", w: "375px" },
                ].map(({ label, w }) => (
                  <button
                    key={w}
                    onClick={() => setViewport(w)}
                    className={`px-2 py-0.5 text-[10px] rounded ${viewport === w ? "bg-blue-600/30 text-blue-300" : "bg-[#1e1e28] text-[#52525b] hover:text-[#a1a1aa]"} transition`}
                  >
                    {label}
                  </button>
                ))}
              </div>
            )}
          </div>
          {showPreview && (
            <div className="mt-2 rounded-xl overflow-hidden border border-[#2a2a30] flex justify-center bg-[#0d0d12] p-2">
              <iframe
                src={`${API_BASE}${c.preview_url}`}
                style={{ width: viewport, maxWidth: "100%" }}
                className="h-[420px] bg-white rounded-lg transition-all duration-300"
                sandbox="allow-scripts allow-same-origin"
                title="Prototype Preview"
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function OrchestrationContent({ c }) {
  const [showDep, setShowDep] = useState(false);

  // dependency_graph_json may contain mermaid
  const depMermaid = c.dependency_graph_json?.mermaid || null;

  return (
    <div className="space-y-2">
      {c._label && <p className="text-white font-medium">{c._label}</p>}
      {c.epic_json && <p className="text-[12px] text-blue-400">{typeof c.epic_json === "string" ? c.epic_json : JSON.stringify(c.epic_json)}</p>}
      {Array.isArray(c.feature_json) && c.feature_json.length > 0 && (
        <div>
          <span className="text-[11px] text-[#52525b]">功能模块</span>
          <ul className="mt-0.5 space-y-1">
            {c.feature_json.slice(0, 5).map((f, i) => (
              <li key={i} className="text-[12px]">
                {typeof f === "string" ? f : f.name || JSON.stringify(f)}
              </li>
            ))}
          </ul>
        </div>
      )}
      {Array.isArray(c.tasks_json) && c.tasks_json.length > 0 && (
        <div>
          <span className="text-[11px] text-[#52525b]">执行顺序 ({c.tasks_json.length} 步)</span>
          <div className="flex flex-wrap gap-1 mt-0.5">
            {c.tasks_json.slice(0, 8).map((t, i) => (
              <span key={i} className="px-1.5 py-0.5 rounded bg-[#1e1e28] text-[11px] font-mono">{typeof t === "string" ? t : t.key || i+1}</span>
            ))}
          </div>
        </div>
      )}
      {/* Mermaid dependency graph */}
      {depMermaid && (
        <div className="mt-2">
          <QuarkButton
            onClick={() => setShowDep(!showDep)}
            variant="raw"
            className="px-3 py-1 text-[12px] rounded-lg bg-purple-600/20 text-purple-400 hover:bg-purple-600/30 transition"
          >
            {showDep ? "隐藏依赖图" : "查看依赖图"}
          </QuarkButton>
          {showDep && <MermaidDiagram code={depMermaid} className="mt-2" />}
        </div>
      )}
    </div>
  );
}

function ExecutionContent({ c }) {
  const result = c.execution_result;
  const [showCode, setShowCode] = useState(false);

  // Collect generated files from job results
  const codeFiles = [];
  if (result?.job_results) {
    for (const j of result.job_results) {
      if (j.files_written) {
        for (const f of j.files_written) {
          if (typeof f === "object" && f.path) codeFiles.push(f);
          else if (typeof f === "string") codeFiles.push({ path: f, content: "" });
        }
      }
    }
  }
  // Also check top-level generated_files
  if (Array.isArray(c.generated_files)) {
    for (const f of c.generated_files) {
      if (!codeFiles.find((cf) => cf.path === f.path)) codeFiles.push(f);
    }
  }

  return (
    <div className="space-y-2">
      {c._label && <p className="text-white font-medium">{c._label}</p>}
      {result && (
        <div className="space-y-1">
          <p className="text-[12px]">完成 {result.completed}/{result.total_jobs} 个任务</p>
          {result.job_results?.map((j, i) => (
            <div key={i} className="text-[11px] flex items-center gap-1.5">
              <span className={j.status === "completed" ? "text-green-400" : "text-red-400"}>●</span>
              <span className="font-mono">{j.job_id}</span>
              {j.files_written?.length > 0 && <span className="text-[#52525b]">({j.files_written.length} files)</span>}
            </div>
          ))}
        </div>
      )}
      {codeFiles.length > 0 && codeFiles.some((f) => f.content) && (
        <div className="mt-2">
          <QuarkButton
            onClick={() => setShowCode(!showCode)}
            variant="raw"
            className="px-3 py-1 text-[12px] rounded-lg bg-cyan-600/20 text-cyan-400 hover:bg-cyan-600/30 transition"
          >
            {showCode ? "隐藏代码" : `查看代码 (${codeFiles.length} 文件)`}
          </QuarkButton>
          {showCode && <CodePreview files={codeFiles} className="mt-2" />}
        </div>
      )}
    </div>
  );
}

function TestingContent({ c }) {
  const result = c.result;
  return (
    <div className="space-y-2">
      {c._label && <p className="text-white font-medium">{c._label}</p>}
      {c.status && <Badge label="状态" value={c.status} />}
      {result && (
        <div className="space-y-1.5">
          {result.tests_generated != null && (
            <p className="text-[12px]">生成了 {result.tests_generated} 个测试文件</p>
          )}
          {/* Code review summary */}
          {result.code_review && (
            <div>
              <span className="text-[11px] text-[#52525b]">代码审查分数: {result.code_review.overall_score}/100</span>
              {result.code_review.issues?.length > 0 && (
                <div className="mt-0.5 space-y-0.5">
                  {result.code_review.issues.slice(0, 3).map((issue, i) => (
                    <div key={i} className="text-[11px] flex items-start gap-1">
                      <span className={issue.severity === "critical" ? "text-red-400" : issue.severity === "warning" ? "text-yellow-400" : "text-blue-400"}>
                        [{issue.severity}]
                      </span>
                      <span>{issue.message}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
          {/* Sandbox result */}
          {result.sandbox_result && result.sandbox_result.stdout && (
            <details className="mt-1">
              <summary className="text-[11px] text-[#52525b] cursor-pointer hover:text-[#a1a1aa]">测试输出</summary>
              <pre className="mt-1 p-2 rounded bg-[#0d0d10] text-[10px] font-mono overflow-x-auto max-h-[200px] overflow-y-auto">
                {result.sandbox_result.stdout}
              </pre>
            </details>
          )}
        </div>
      )}
    </div>
  );
}

function DeliveryContent({ c }) {
  const [showReadme, setShowReadme] = useState(false);

  return (
    <div className="space-y-2">
      {c._label && <p className="text-white font-medium">{c._label}</p>}
      {c.status && <Badge label="状态" value={c.status} />}
      {c.delivery_dir && (
        <p className="text-[11px] font-mono text-[#52525b] truncate">{c.delivery_dir}</p>
      )}
      {c.summary_md && (
        <div className="mt-1">
          <QuarkButton
            onClick={() => setShowReadme(!showReadme)}
            variant="raw"
            className="px-3 py-1 text-[12px] rounded-lg bg-emerald-600/20 text-emerald-400 hover:bg-emerald-600/30 transition"
          >
            {showReadme ? "隐藏 README" : "README 预览"}
          </QuarkButton>
          {showReadme && (
            <div className="mt-2 p-3 rounded-lg bg-[#0d0d12] border border-[#1e1e28] max-h-[400px] overflow-y-auto">
              <MarkdownBlock content={c.summary_md} />
            </div>
          )}
        </div>
      )}
      {/* Download button */}
      {c.project_id && (
        <div className="mt-2">
          <a
            href={`${API_BASE}/projects/${c.project_id}/delivery/download`}
            download
            className="inline-flex items-center gap-1.5 px-3 py-1 text-[12px] rounded-lg bg-blue-600/20 text-blue-400 hover:bg-blue-600/30 transition"
          >
            <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
              <path d="M6 2v6m0 0L3.5 5.5M6 8l2.5-2.5M2 10h8" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            下载交付包
          </a>
        </div>
      )}
    </div>
  );
}

function RerunButton({ projectId, stage }) {
  const [loading, setLoading] = useState(false);

  async function handleRerun() {
    if (!confirm(`确定重跑 ${STAGE_LABELS[stage] || stage} 及下游阶段？`)) return;
    setLoading(true);
    try {
      await fetch(`${API_BASE}/manus/projects/${projectId}/stages/${stage}/rerun`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
      });
    } catch (e) {
      console.error("Rerun error:", e);
    } finally {
      setLoading(false);
    }
  }

  return (
    <button
      onClick={handleRerun}
      disabled={loading}
      className="ml-auto opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-white/5 text-[#52525b] hover:text-[#a1a1aa] transition-all"
      title={`重跑 ${STAGE_LABELS[stage] || stage}`}
    >
      <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
        <path d="M1 6a5 5 0 019-3M11 6a5 5 0 01-9 3M10 1v2h-2M2 11V9h2" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round"/>
      </svg>
    </button>
  );
}

function ApprovalContent({ c }) {
  const [submitting, setSubmitting] = useState(false);
  const [decided, setDecided] = useState(null);

  async function handleDecision(decision) {
    setSubmitting(true);
    try {
      const resp = await fetch(
        `${API_BASE}/manus/projects/${c.project_id}/approve/${c.stage}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ decision }),
        }
      );
      if (resp.ok) {
        setDecided(decision);
      }
    } catch (e) {
      console.error("Approval error:", e);
    } finally {
      setSubmitting(false);
    }
  }

  if (decided) {
    return (
      <div className="space-y-2">
        <p className="text-white font-medium">{c._label}</p>
        <p className="text-[12px]">
          {decided === "approved" ? "已批准，autopilot 继续推进" : "已拒绝"}
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <p className="text-white font-medium">{c._label}</p>
      {c.reason && <p className="text-[12px] text-amber-200/80">{c.reason}</p>}
      <div className="flex gap-2">
        <button
          onClick={() => handleDecision("approved")}
          disabled={submitting}
          className="px-4 py-1.5 text-[12px] rounded-lg bg-emerald-600/30 text-emerald-300 border border-emerald-500/30 hover:bg-emerald-600/50 transition disabled:opacity-50"
        >
          批准继续
        </button>
        <button
          onClick={() => handleDecision("rejected")}
          disabled={submitting}
          className="px-4 py-1.5 text-[12px] rounded-lg bg-red-600/20 text-red-300 border border-red-500/30 hover:bg-red-600/40 transition disabled:opacity-50"
        >
          拒绝
        </button>
      </div>
    </div>
  );
}

// --- Shared components ---

function Badge({ label, value }) {
  const colorMap = {
    low: "bg-green-900/30 text-green-400",
    medium: "bg-yellow-900/30 text-yellow-400",
    high: "bg-red-900/30 text-red-400",
    simple: "bg-green-900/30 text-green-400",
    complex: "bg-red-900/30 text-red-400",
    passed: "bg-green-900/30 text-green-400",
    failed: "bg-red-900/30 text-red-400",
    published: "bg-blue-900/30 text-blue-400",
  };
  const cls = colorMap[value] || "bg-[#1e1e28] text-[#a1a1aa]";
  return (
    <span className="text-[11px]">
      <span className="text-[#52525b] mr-1">{label}</span>
      <span className={`px-1.5 py-0.5 rounded ${cls}`}>{value}</span>
    </span>
  );
}

function GenericContent({ c }) {
  const label = c._label;
  const entries = Object.entries(c).filter(
    ([k, v]) => v != null && v !== "" && k !== "_label" && k !== "onReply"
  );

  return (
    <div className="space-y-1">
      {label && <p className="text-white font-medium">{label}</p>}
      {entries.length > 0 && (
        <div className="space-y-0.5 mt-1">
          {entries.slice(0, 6).map(([key, val]) => {
            const display = typeof val === "object" ? JSON.stringify(val) : String(val);
            return (
              <div key={key} className="flex gap-2 text-[12px]">
                <span className="text-[#52525b] shrink-0">{key}</span>
                <span className="text-[#a1a1aa] truncate">{display.length > 120 ? display.slice(0, 120) + "..." : display}</span>
              </div>
            );
          })}
          {entries.length > 6 && (
            <span className="text-[11px] text-[#3a3a3e]">+{entries.length - 6} more</span>
          )}
        </div>
      )}
    </div>
  );
}
