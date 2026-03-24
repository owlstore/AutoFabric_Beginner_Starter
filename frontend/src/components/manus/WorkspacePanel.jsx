import { useState } from "react";
import MarkdownBlock from "./MarkdownBlock";
import CodePreview from "./CodePreview";

function StatusBadge({ status }) {
  const palette = {
    completed: "bg-emerald-500/15 text-emerald-300 border-emerald-500/20",
    active: "bg-cyan-500/15 text-cyan-200 border-cyan-500/20",
    pending: "bg-white/5 text-slate-400 border-white/10",
  };
  return (
    <span className={`inline-flex items-center rounded-full border px-2 py-0.5 text-[11px] ${palette[status] || palette.pending}`}>
      {status}
    </span>
  );
}

function relativeTime(ts) {
  if (!ts) return "";
  const diff = Date.now() - new Date(ts).getTime();
  const seconds = Math.floor(diff / 1000);
  if (seconds < 60) return "刚刚";
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes} 分钟前`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours} 小时前`;
  const days = Math.floor(hours / 24);
  return `${days} 天前`;
}

export default function WorkspacePanel({ snapshot, loading }) {
  const workspace = snapshot?.workspace;
  const project = snapshot?.project;
  const overview = snapshot?.overview;
  const [expandedArtifact, setExpandedArtifact] = useState(null);

  // Extract tech stack from requirement analysis
  const techStack = (() => {
    const reqs = overview?.stage_objects?.requirements;
    if (!reqs?.length) return null;
    const analysis = reqs[0]?.llm_analysis;
    return analysis?.tech_stack_suggestion || null;
  })();

  if (!workspace && !loading) {
    return (
      <aside className="hidden w-[360px] shrink-0 border-l border-white/5 bg-[#0c1115]/95 xl:flex xl:flex-col">
        <div className="border-b border-white/5 px-5 py-4">
          <p className="text-[11px] uppercase tracking-[0.28em] text-cyan-200/70">Mission View</p>
          <h2 className="mt-2 text-lg font-semibold text-white">Autopilot Workspace</h2>
        </div>
        <div className="flex-1 px-5 py-6 text-sm leading-7 text-slate-400">
          选中一个项目，或者直接输入你的目标。系统会自己创建项目、推进阶段，并把最近活动、产物和下一步建议聚合到这里。
        </div>
      </aside>
    );
  }

  return (
    <aside className="hidden w-[360px] shrink-0 border-l border-white/5 bg-[#0c1115]/95 xl:flex xl:flex-col">
      <div className="border-b border-white/5 px-5 py-4">
        <p className="text-[11px] uppercase tracking-[0.28em] text-cyan-200/70">Mission View</p>
        <h2 className="mt-2 text-lg font-semibold text-white">{workspace?.headline || project?.name || "Workspace"}</h2>
        <p className="mt-2 text-sm leading-6 text-slate-400">{workspace?.summary || "暂无摘要"}</p>
      </div>

      <div className="flex-1 overflow-y-auto px-5 py-5">
        <section className="rounded-3xl border border-white/8 bg-white/[0.03] p-4">
          <div className="flex items-start justify-between gap-3">
            <div>
              <p className="text-[11px] uppercase tracking-[0.24em] text-slate-500">Control Mode</p>
              <p className="mt-2 text-sm font-medium text-white">{workspace?.control_mode || "autopilot"}</p>
            </div>
            <StatusBadge status={project?.status === "active" ? "active" : "pending"} />
          </div>
          <div className="mt-4 grid grid-cols-2 gap-3">
            <Metric label="LLM" value={workspace?.llm_provider || "mock"} />
            <Metric label="Bridge" value={workspace?.bridge_mode || "llm"} />
            <Metric label="Artifacts" value={String(workspace?.metrics?.artifacts || 0)} />
            <Metric label="Stages" value={`${workspace?.metrics?.completed_stages || 0}/7`} />
          </div>
        </section>

        {/* Recommended Actions */}
        {workspace?.recommended_actions?.length > 0 && (
          <section className="mt-4 rounded-3xl border border-white/8 bg-white/[0.03] p-4">
            <p className="text-[11px] uppercase tracking-[0.24em] text-slate-500">Recommended Actions</p>
            <div className="mt-3 space-y-2">
              {workspace.recommended_actions.map((action, i) => (
                <div key={i} className="flex items-start gap-2 rounded-xl border border-cyan-400/10 bg-cyan-400/5 px-3 py-2">
                  <span className="mt-0.5 text-cyan-400 shrink-0">
                    <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                      <path d="M2 6l3 3 5-5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                  </span>
                  <p className="text-[12px] leading-5 text-cyan-100">{action}</p>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Tech Stack */}
        {techStack && Object.keys(techStack).length > 0 && (
          <section className="mt-4 rounded-3xl border border-white/8 bg-white/[0.03] p-4">
            <p className="text-[11px] uppercase tracking-[0.24em] text-slate-500">Tech Stack</p>
            <div className="mt-3 flex flex-wrap gap-1.5">
              {Object.entries(techStack).map(([k, v]) =>
                v ? (
                  <span key={k} className="inline-flex items-center gap-1 rounded-lg bg-blue-500/10 border border-blue-500/20 px-2 py-1 text-[11px] text-blue-300">
                    <span className="text-[#52525b]">{k}:</span> {v}
                  </span>
                ) : null
              )}
            </div>
          </section>
        )}

        {/* Stage Rail */}
        <section className="mt-4 rounded-3xl border border-white/8 bg-white/[0.03] p-4">
          <p className="text-[11px] uppercase tracking-[0.24em] text-slate-500">Stage Rail</p>
          <div className="mt-4 space-y-3">
            {(workspace?.stage_rail || []).map((item) => (
              <div key={item.key} className="flex items-center gap-3">
                <div
                  className={`h-2.5 w-2.5 rounded-full ${
                    item.status === "completed"
                      ? "bg-emerald-400 shadow-[0_0_0_4px_rgba(16,185,129,0.12)]"
                      : item.status === "active"
                        ? "bg-cyan-300 shadow-[0_0_0_4px_rgba(34,211,238,0.12)]"
                        : "bg-slate-700"
                  }`}
                />
                <div className="min-w-0 flex-1">
                  <div className="flex items-center justify-between gap-3">
                    <p className="text-sm font-medium text-white">{item.label}</p>
                    <StatusBadge status={item.status} />
                  </div>
                  {item.is_current && <p className="mt-1 text-[12px] text-cyan-200/70">当前阶段</p>}
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Run Summary */}
        <section className="mt-4 rounded-3xl border border-white/8 bg-white/[0.03] p-4">
          <p className="text-[11px] uppercase tracking-[0.24em] text-slate-500">Run Summary</p>
          <div className="mt-3 space-y-2">
            {(workspace?.run_summary || []).length === 0 && (
              <p className="text-sm text-slate-500">还没有 run 记录。</p>
            )}
            {(workspace?.run_summary || []).map((item) => (
              <div key={item.label} className="rounded-2xl border border-white/8 bg-black/20 px-3 py-3">
                <div className="flex items-center justify-between gap-3">
                  <p className="text-sm font-medium text-white">{item.label}</p>
                  <StatusBadge status={item.status === "published" || item.status === "passed" ? "completed" : item.status || "pending"} />
                </div>
                {item.meta && <p className="mt-1 text-[12px] text-slate-400">{item.meta}</p>}
              </div>
            ))}
          </div>
        </section>

        {/* Artifacts — clickable */}
        <section className="mt-4 rounded-3xl border border-white/8 bg-white/[0.03] p-4">
          <p className="text-[11px] uppercase tracking-[0.24em] text-slate-500">Artifacts</p>
          <div className="mt-3 space-y-2">
            {(workspace?.artifacts || []).length === 0 && (
              <p className="text-sm text-slate-500">产物会在执行和交付阶段自动出现。</p>
            )}
            {(workspace?.artifacts || []).map((item) => (
              <button
                key={item.path}
                onClick={() => setExpandedArtifact(expandedArtifact === item.path ? null : item.path)}
                className="w-full text-left rounded-2xl border border-white/8 bg-black/20 px-3 py-3 hover:border-cyan-500/20 hover:bg-cyan-500/5 transition-colors"
              >
                <div className="flex items-center justify-between gap-3">
                  <p className="truncate text-sm font-medium text-white">{item.name}</p>
                  <span className="rounded-full bg-white/5 px-2 py-0.5 text-[11px] text-slate-400">{item.category}</span>
                </div>
                <p className="mt-1 truncate text-[12px] text-slate-500">{item.path}</p>
                {item.size_kb != null && (
                  <p className="mt-0.5 text-[10px] text-slate-600">{item.size_kb} KB</p>
                )}
              </button>
            ))}
          </div>
        </section>

        {/* Recent Activity — with relative time */}
        <section className="mt-4 rounded-3xl border border-white/8 bg-white/[0.03] p-4">
          <p className="text-[11px] uppercase tracking-[0.24em] text-slate-500">Recent Activity</p>
          <div className="mt-3 space-y-3">
            {(workspace?.recent_activity || []).map((item, index) => (
              <div key={`${item.title}-${index}`} className="relative pl-4">
                <span className="absolute left-0 top-1.5 h-2 w-2 rounded-full bg-cyan-300/80" />
                <p className="text-sm font-medium text-white">{item.title}</p>
                <p className="mt-1 text-[12px] leading-5 text-slate-400">{item.detail}</p>
                {item.timestamp && (
                  <p className="mt-1 text-[11px] text-slate-500" title={item.timestamp}>
                    {relativeTime(item.timestamp)}
                  </p>
                )}
              </div>
            ))}
          </div>
        </section>
      </div>
    </aside>
  );
}

function Metric({ label, value }) {
  return (
    <div className="rounded-2xl border border-white/8 bg-black/20 px-3 py-3">
      <p className="text-[11px] uppercase tracking-[0.18em] text-slate-500">{label}</p>
      <p className="mt-2 text-base font-semibold text-white">{value}</p>
    </div>
  );
}
