export default function ToastBar({ message, tone = "info" }) {
  if (!message) return null;

  const cls =
    tone === "success"
      ? "border-emerald-200 bg-emerald-50 text-emerald-700"
      : tone === "error"
      ? "border-red-200 bg-red-50 text-red-700"
      : "border-blue-200 bg-blue-50 text-blue-700";

  return <div className={`rounded-2xl border px-4 py-3 text-sm ${cls}`}>{message}</div>;
}
