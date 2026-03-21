export default function KV({ label, value }) {
  const display = value === null || value === undefined || value === "" ? "—" : String(value);

  return (
    <div className="grid grid-cols-[120px_1fr] gap-4 py-2">
      <div className="text-sm font-medium text-slate-500">{label}</div>
      <div className="break-all text-sm text-slate-900">{display}</div>
    </div>
  );
}
