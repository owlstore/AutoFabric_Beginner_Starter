export default function ExpandableTextRow({ label, value, expanded, onToggle, minLength = 80 }) {
  const display = value === null || value === undefined || value === "" ? "—" : String(value);
  const shouldExpand = display.length > minLength;
  const shown = expanded || !shouldExpand ? display : `${display.slice(0, minLength)}...`;

  return (
    <div className="grid grid-cols-[120px_1fr] gap-4 py-2">
      <div className="text-sm font-medium text-slate-500">{label}</div>
      <div className="text-sm text-slate-900">
        <div className="whitespace-pre-wrap break-words">{shown}</div>
        {shouldExpand ? (
          <button onClick={onToggle} className="mt-2 text-xs font-medium text-violet-700 hover:text-violet-800">
            {expanded ? "收起" : "展开查看"}
          </button>
        ) : null}
      </div>
    </div>
  );
}
