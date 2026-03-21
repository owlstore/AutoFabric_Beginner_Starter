export default function HealthBanner({ health, onRefresh }) {
  const toneClass = health.loading
    ? "border-slate-200 bg-white text-slate-700"
    : health.ok
    ? "border-emerald-200 bg-emerald-50 text-emerald-800"
    : "border-red-200 bg-red-50 text-red-800";

  const label = health.loading
    ? "正在检查系统健康状态..."
    : health.ok
    ? `${health.service} 正常 · v${health.version}`
    : `API 异常：${health.error || "未知错误"}`;

  return (
    <div className={`mb-4 flex items-center justify-between gap-3 rounded-2xl border px-4 py-3 text-sm ${toneClass}`}>
      <div>{label}</div>
      <button
        onClick={onRefresh}
        className="rounded-xl border border-current/20 bg-white/70 px-3 py-1.5 text-xs font-medium hover:bg-white"
      >
        刷新状态
      </button>
    </div>
  );
}
