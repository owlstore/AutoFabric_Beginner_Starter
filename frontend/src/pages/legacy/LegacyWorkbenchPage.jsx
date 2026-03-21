export default function LegacyWorkbenchPage() {
  return (
    <div className="min-h-screen bg-slate-100 text-slate-900">
      <div className="mx-auto max-w-[1440px] px-6 py-8">
        <div className="rounded-3xl border border-amber-200 bg-amber-50 p-8 text-amber-800 shadow-sm">
          <h1 className="text-2xl font-bold">Legacy Workbench 占位页</h1>
          <p className="mt-3 text-sm leading-6">
            旧版页面已切换为备份入口。当前默认主入口为 WorkbenchPageV2。
          </p>
          <p className="mt-2 text-sm leading-6">
            如需恢复旧版真实页面，可将历史备份 App.jsx 或旧页面组件重新挂载到这里。
          </p>
        </div>
      </div>
    </div>
  );
}
