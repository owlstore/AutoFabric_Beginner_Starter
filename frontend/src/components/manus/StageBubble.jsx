import { useState } from "react";
import { STAGE_LABELS } from "../../constants/stages";
import { API_BASE } from "../../api/client";
import QuarkButton from "../quark/QuarkButton";

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

  return (
    <div className="flex justify-start">
      <div className="max-w-[88%] flex items-start gap-2.5">
        {/* Avatar */}
        <div className="w-7 h-7 rounded-lg bg-[#1e1e28] flex items-center justify-center shrink-0">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
            <path d="M7 1L1.5 4l5.5 3 5.5-3L7 1zM1.5 10l5.5 3 5.5-3M1.5 7l5.5 3 5.5-3" stroke="#60a5fa" strokeWidth="1" strokeLinejoin="round" strokeLinecap="round"/>
          </svg>
        </div>

        {/* Card */}
        <div className="rounded-2xl rounded-tl-md border border-[#1e1e28] bg-[#16161a] px-4 py-3 shadow-lg shadow-black/10 min-w-[200px] max-w-full">
          {/* Header row */}
          <div className="flex items-center gap-2 mb-2">
            {stage && (
              <span className={`inline-flex items-center rounded-md px-2 py-0.5 text-[11px] font-medium stage-pill-${stage}`}>
                {label}
              </span>
            )}
            <span className={`flex items-center gap-1 text-[11px] ${sc.color}`}>
              {sc.icon === "check" && <CheckIcon />}
              {sc.icon === "dot" && <span className="w-1.5 h-1.5 rounded-full bg-current" />}
              {sc.text}
            </span>
          </div>

          {/* Content — stage-specific rendering */}
          <div className="text-[13px] text-[#a1a1aa] leading-relaxed">
            {renderStageContent(stage, message.content)}
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
      {/* Preview button + iframe */}
      {c.preview_url && (
        <div className="mt-2">
          <QuarkButton
            onClick={() => setShowPreview(!showPreview)}
            variant="raw"
            className="px-3 py-1 text-[12px] rounded-lg bg-blue-600/20 text-blue-400 hover:bg-blue-600/30 transition"
          >
            {showPreview ? "隐藏预览" : "查看原型预览"}
          </QuarkButton>
          {showPreview && (
            <div className="mt-2 rounded-xl overflow-hidden border border-[#2a2a30]">
              <iframe
                src={`${API_BASE}${c.preview_url}`}
                className="w-full h-[400px] bg-white"
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
    </div>
  );
}

function ExecutionContent({ c }) {
  const result = c.execution_result;
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
  return (
    <div className="space-y-2">
      {c._label && <p className="text-white font-medium">{c._label}</p>}
      {c.status && <Badge label="状态" value={c.status} />}
      {c.delivery_dir && (
        <p className="text-[11px] font-mono text-[#52525b] truncate">{c.delivery_dir}</p>
      )}
      {c.summary_md && (
        <details className="mt-1">
          <summary className="text-[11px] text-[#52525b] cursor-pointer hover:text-[#a1a1aa]">README 预览</summary>
          <pre className="mt-1 p-2 rounded bg-[#0d0d10] text-[11px] font-mono overflow-x-auto max-h-[300px] overflow-y-auto whitespace-pre-wrap">
            {c.summary_md.slice(0, 2000)}
          </pre>
        </details>
      )}
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
