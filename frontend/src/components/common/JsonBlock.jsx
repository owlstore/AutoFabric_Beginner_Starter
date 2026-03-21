export default function JsonBlock({ data }) {
  return (
    <pre className="max-h-[360px] overflow-auto rounded-2xl bg-slate-950 p-4 text-xs leading-6 text-slate-100">
      {JSON.stringify(data ?? {}, null, 2)}
    </pre>
  );
}
