export default function ToastViewport({ toasts, onRemove }) {
  return (
    <div className="pointer-events-none fixed right-4 top-4 z-[100] flex w-[360px] max-w-[calc(100vw-2rem)] flex-col gap-3">
      {toasts.map((toast) => {
        const toneClass = {
          success: "border-emerald-200 bg-emerald-50 text-emerald-800",
          error: "border-red-200 bg-red-50 text-red-800",
          info: "border-blue-200 bg-blue-50 text-blue-800",
          warning: "border-amber-200 bg-amber-50 text-amber-800",
        }[toast.type || "info"] || "border-blue-200 bg-blue-50 text-blue-800";

        return (
          <div
            key={toast.id}
            className={`pointer-events-auto rounded-2xl border px-4 py-3 shadow-lg ${toneClass}`}
          >
            <div className="flex items-start justify-between gap-3">
              <div className="text-sm font-medium">{toast.message}</div>
              <button
                onClick={() => onRemove(toast.id)}
                className="text-xs opacity-70 hover:opacity-100"
              >
                关闭
              </button>
            </div>
          </div>
        );
      })}
    </div>
  );
}
