export default function SectionCard({ title, extra, children }) {
  return (
    <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="mb-4 flex items-start justify-between gap-3">
        <h3 className="text-lg font-semibold text-slate-900">{title}</h3>
        {extra ? <div>{extra}</div> : null}
      </div>
      {children}
    </div>
  );
}
