import { STAGE_LABELS } from "../../constants/stages";

const STAGE_KEYS = ["requirement", "clarification", "prototype", "orchestration", "execution", "testing", "delivery"];

export default function ProjectCard({ project, onSelect }) {
  const stage = project.current_stage_key || "requirement";
  const stageIdx = STAGE_KEYS.indexOf(stage);
  const progress = Math.round(((stageIdx + 1) / STAGE_KEYS.length) * 100);

  return (
    <button
      onClick={() => onSelect(project.id)}
      className="w-full text-left rounded-2xl border border-white/8 bg-white/[0.03] p-4 hover:border-cyan-500/20 hover:bg-cyan-500/5 transition-colors"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <h3 className="text-sm font-medium text-white truncate">{project.name}</h3>
          {project.description && (
            <p className="mt-1 text-[12px] text-slate-400 line-clamp-2">{project.description}</p>
          )}
        </div>
        <span className={`shrink-0 inline-flex items-center rounded-full border px-2 py-0.5 text-[11px] ${
          project.status === "active"
            ? "bg-cyan-500/15 text-cyan-200 border-cyan-500/20"
            : "bg-white/5 text-slate-400 border-white/10"
        }`}>
          {project.status}
        </span>
      </div>

      <div className="mt-3">
        <div className="flex items-center justify-between mb-1">
          <span className="text-[11px] text-slate-500">
            {STAGE_LABELS[stage] || stage}
          </span>
          <span className="text-[11px] text-slate-500">{progress}%</span>
        </div>
        <div className="h-1.5 rounded-full bg-white/5 overflow-hidden">
          <div
            className="h-full rounded-full bg-gradient-to-r from-cyan-500 to-blue-500 transition-all duration-500"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {project.created_at && (
        <p className="mt-2 text-[10px] text-slate-600">
          {new Date(project.created_at).toLocaleDateString()}
        </p>
      )}
    </button>
  );
}
