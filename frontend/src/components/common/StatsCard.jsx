export default function StatsCard({ label, value, tone = "default" }) {
  const toneClass = {
    default: "border-slate-200 bg-white",
    success: "border-emerald-200 bg-emerald-50",
    info: "border-blue-200 bg-blue-50",
    danger: "border-red-200 bg-red-50",
  }[tone] || "border-slate-200 bg-white";

  return (
    <div className={`rounded-3xl border p-6 shadow-sm ${toneClass}`}>
      <div className="text-sm font-medium text-slate-500">{label}</div>
      <div className="mt-3 text-4xl font-semibold text-slate-900">{value}</div>
    </div>
  );
}
