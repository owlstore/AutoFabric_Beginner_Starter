import Badge from "../common/Badge";

export default function OutcomeListItem({ item, active, onClick }) {
  return (
    <button
      onClick={onClick}
      className={`w-full rounded-3xl border p-4 text-left transition ${
        active
          ? "border-slate-900 bg-slate-50 shadow-md ring-2 ring-slate-200"
          : "border-slate-200 bg-white hover:bg-slate-50"
      }`}
    >
      <div className="mb-3 flex items-start justify-between gap-3">
        <div>
          <div className="text-base font-semibold text-slate-900">{item.title}</div>
          <div className="mt-1 text-xs text-slate-500">结果 #{item.outcome_id} · 目标 #{item.goal_id}</div>
        </div>
        <Badge tone={item.statusTone}>{item.statusLabel}</Badge>
      </div>

      <div className="mb-3 flex flex-wrap gap-2">
        <Badge tone="purple">{item.goalTypeLabel}</Badge>
        <Badge tone="info">{item.stageLabel}</Badge>
      </div>

      <div className="space-y-2">
        <div className="rounded-2xl border border-slate-200 bg-slate-50 p-3">
          <div className="mb-1 text-[11px] uppercase tracking-wide text-slate-500">当前结果</div>
          <div className="text-sm text-slate-800">{item.currentResult}</div>
        </div>
        <div className="rounded-2xl border border-slate-200 bg-white p-3">
          <div className="mb-1 text-[11px] uppercase tracking-wide text-slate-500">下一步</div>
          <div className="text-sm text-slate-800">{item.nextAction}</div>
        </div>
      </div>
    </button>
  );
}
