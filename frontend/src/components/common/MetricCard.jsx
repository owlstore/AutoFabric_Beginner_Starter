export default function MetricCard({ label, value, tone = "default", active = false, onClick }) {
  const toneClass = {
    default: "border-slate-200 bg-white",
    success: "border-emerald-200 bg-emerald-50",
    warning: "border-amber-200 bg-amber-50",
    danger: "border-red-200 bg-red-50",
    info: "border-blue-200 bg-blue-50",
  }[tone] || "border-slate-200 bg-white";

  return (
    <button
      onClick={onClick}
      className={`rounded-3xl border p-5 text-left transition ${toneClass} ${active ? "ring-2 ring-slate-300 shadow-sm" : "hover:shadow-sm"}`}
    >
      <div className="text-sm font-medium uppercase tracking-wide text-slate-500">{label}</div>
      <div className="mt-3 text-4xl font-semibold text-slate-900">{value}</div>
    </button>
  );
}
