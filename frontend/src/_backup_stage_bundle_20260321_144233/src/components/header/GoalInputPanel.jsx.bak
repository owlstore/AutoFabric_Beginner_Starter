export default function GoalInputPanel({
  input,
  setInput,
  submitting,
  handleSubmit,
  clearInputDraft,
  restoreInputDraft,
  saveCurrentDraftToRecent,
  hasInputDraft,
  recentInputs,
  replaceCurrentDraftWithRecent,
  notice,
}) {
  return (
    <div className="mb-6 rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
      <div className="mb-4 flex flex-col gap-2">
        <h1 className="text-5xl font-bold tracking-tight text-slate-900">AutoFabric 成果工作台</h1>
        <p className="text-lg text-slate-600">目标 → 需求 → 编排 → Agent → 执行 → 测试 → 交付</p>
        <p className="text-base text-slate-500">以结果为导向的研发操作系统</p>
      </div>

      <form onSubmit={handleSubmit} className="grid gap-3 lg:grid-cols-[1fr_auto]">
        <div className="space-y-3">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="描述你要构建的结果..."
            className="h-12 w-full rounded-2xl border border-slate-300 px-4 text-sm outline-none transition focus:border-slate-500"
          />

          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={clearInputDraft}
              className="rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
            >
              清空
            </button>
            <button
              type="button"
              onClick={restoreInputDraft}
              disabled={!hasInputDraft}
              className="rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
            >
              恢复上一份草稿
            </button>
            <button
              type="button"
              onClick={saveCurrentDraftToRecent}
              className="rounded-xl border border-blue-300 bg-blue-50 px-4 py-2 text-sm font-medium text-blue-700 hover:bg-blue-100"
            >
              加入最近提交
            </button>
          </div>

          {recentInputs?.length ? (
            <div>
              <div className="mb-2 text-sm font-medium text-slate-600">最近提交</div>
              <div className="flex flex-wrap gap-2">
                {recentInputs.map((item) => (
                  <button
                    key={item}
                    type="button"
                    onClick={() => replaceCurrentDraftWithRecent(item)}
                    className="max-w-full rounded-full border border-slate-200 bg-white px-3 py-2 text-left text-xs text-slate-700 transition hover:bg-slate-50"
                    title={item}
                  >
                    {item.length > 48 ? `${item.slice(0, 48)}...` : item}
                  </button>
                ))}
              </div>
            </div>
          ) : null}

          {notice ? (
            <div className="rounded-2xl border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-700">
              {notice}
            </div>
          ) : null}
        </div>

        <button
          type="submit"
          disabled={submitting}
          className="h-12 rounded-2xl bg-slate-900 px-5 text-sm font-medium text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {submitting ? "提交中..." : "提交目标"}
        </button>
      </form>
    </div>
  );
}
