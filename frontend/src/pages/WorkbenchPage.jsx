import { useMemo, useState } from "react";
import MetricCard from "../components/common/MetricCard";
import SectionCard from "../components/common/SectionCard";
import QuickFilterChip from "../components/common/QuickFilterChip";
import Badge from "../components/common/Badge";
import ToastBar from "../components/common/ToastBar";

export default function WorkbenchPage() {
  const [input, setInput] = useState("Build an Ubuntu 22.04 development environment with Docker Git Python");
  const [toast, setToast] = useState("");
  const [quickFilter, setQuickFilter] = useState("all");
  const [recentInputs, setRecentInputs] = useState([
    "构建一个基于 Ubuntu 22.04 的开发环境，包含 Docker、Git 与 Python",
  ]);

  const metrics = useMemo(
    () => ({ total: 27, completed: 21, running: 0, failed: 0 }),
    []
  );

  function showToast(message) {
    setToast(message);
    setTimeout(() => setToast(""), 1500);
  }

  function saveDraftToRecent() {
    const trimmed = String(input || "").trim();
    if (!trimmed) {
      showToast("当前草稿为空，无法加入最近提交");
      return;
    }
    setRecentInputs((prev) => [trimmed, ...prev.filter((x) => x !== trimmed)].slice(0, 6));
    showToast("已加入最近提交");
  }

  function replaceDraft(value) {
    setInput(value);
    showToast("已用最近提交替换当前草稿");
  }

  return (
    <div className="min-h-screen bg-slate-100 text-slate-900">
      <div className="mx-auto max-w-[1440px] px-6 py-8">
        <div className="mb-6 rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
          <div className="mb-4 flex flex-col gap-2">
            <h1 className="text-5xl font-bold tracking-tight text-slate-900">AutoFabric 成果工作台</h1>
            <p className="text-lg text-slate-600">目标 → 结果 → 执行 → 流程事件 → 证据</p>
            <p className="text-base text-slate-500">以结果为导向的审计追踪准备就绪</p>
          </div>

          <div className="grid gap-3 lg:grid-cols-[1fr_auto]">
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
                  onClick={() => {
                    setInput("");
                    showToast("已清空输入草稿");
                  }}
                  className="rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
                >
                  清空
                </button>
                <button
                  type="button"
                  onClick={() => showToast("已恢复上一份草稿")}
                  className="rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
                >
                  恢复上一份草稿
                </button>
                <button
                  type="button"
                  onClick={saveDraftToRecent}
                  className="rounded-xl border border-blue-300 bg-blue-50 px-4 py-2 text-sm font-medium text-blue-700 hover:bg-blue-100"
                >
                  加入最近提交
                </button>
              </div>

              {recentInputs.length ? (
                <div>
                  <div className="mb-2 text-sm font-medium text-slate-600">最近提交</div>
                  <div className="flex flex-wrap gap-2">
                    {recentInputs.map((item) => (
                      <button
                        key={item}
                        onClick={() => replaceDraft(item)}
                        title={item}
                        className="rounded-full border border-slate-200 bg-white px-4 py-2 text-sm text-slate-700 hover:bg-slate-50"
                      >
                        {item.length > 28 ? `${item.slice(0, 28)}......` : item}
                      </button>
                    ))}
                  </div>
                </div>
              ) : null}

              <ToastBar message={toast} />
            </div>

            <button className="h-12 rounded-2xl bg-slate-900 px-5 text-sm font-medium text-white hover:bg-slate-800">
              提交目标
            </button>
          </div>
        </div>

        <div className="mb-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <MetricCard label="结果总数" value={metrics.total} active={quickFilter === "all"} onClick={() => setQuickFilter("all")} />
          <MetricCard label="已完成" value={metrics.completed} tone="success" active={quickFilter === "completed"} onClick={() => setQuickFilter("completed")} />
          <MetricCard label="执行中" value={metrics.running} tone="info" active={quickFilter === "running"} onClick={() => setQuickFilter("running")} />
          <MetricCard label="失败" value={metrics.failed} tone="danger" active={quickFilter === "failed"} onClick={() => setQuickFilter("failed")} />
        </div>

        <div className="grid grid-cols-1 gap-6 xl:grid-cols-[380px_minmax(0,1fr)]">
          <SectionCard title="结果清单" extra={<Badge tone="default">8 条 / 27 条</Badge>}>
            <div className="space-y-3">
              <div className="sticky top-0 z-10 -mx-1 rounded-2xl bg-white px-1 pb-3">
                <div className="flex flex-wrap gap-2">
                  <QuickFilterChip active={quickFilter === "all"} onClick={() => setQuickFilter("all")}>全部</QuickFilterChip>
                  <QuickFilterChip active={quickFilter === "completed"} onClick={() => setQuickFilter("completed")}>已完成</QuickFilterChip>
                  <QuickFilterChip active={quickFilter === "running"} onClick={() => setQuickFilter("running")}>执行中</QuickFilterChip>
                  <QuickFilterChip active={quickFilter === "failed"} onClick={() => setQuickFilter("failed")}>失败</QuickFilterChip>
                  <QuickFilterChip active={quickFilter === "openclaw"} onClick={() => setQuickFilter("openclaw")}>OpenClaw</QuickFilterChip>
                </div>

                <input
                  placeholder="搜索标题/状态/结果/下一步"
                  className="mt-3 h-11 w-full rounded-2xl border border-slate-300 px-4 text-sm outline-none"
                />

                <div className="mt-3 grid gap-3">
                  <select className="h-11 rounded-2xl border border-slate-300 bg-white px-3 text-sm outline-none">
                    <option>所有状态</option>
                  </select>
                  <select className="h-11 rounded-2xl border border-slate-300 bg-white px-3 text-sm outline-none">
                    <option>所有目标类型</option>
                  </select>
                  <select className="h-11 rounded-2xl border border-slate-300 bg-white px-3 text-sm outline-none">
                    <option>更新：最新</option>
                  </select>
                </div>
              </div>

              <div className="max-h-[980px] space-y-3 overflow-y-auto pr-1">
                <button className="w-full rounded-3xl border border-slate-900 bg-slate-50 p-4 text-left shadow-md ring-2 ring-slate-200">
                  <div className="mb-3 flex items-start justify-between gap-3">
                    <div>
                      <div className="text-base font-semibold text-slate-900">使用 Docker、Git 和 Python 构建 Ubuntu 22.04 开发环境</div>
                      <div className="mt-1 text-xs text-slate-500">结果 #27 · 目标 #42</div>
                    </div>
                    <Badge tone="success">已完成</Badge>
                  </div>
                  <div className="mb-3 flex flex-wrap gap-2">
                    <Badge tone="purple">系统构建</Badge>
                    <Badge tone="info">浏览器执行完成</Badge>
                  </div>
                  <div className="space-y-2">
                    <div className="rounded-2xl border border-slate-200 bg-slate-50 p-3">
                      <div className="mb-1 text-[11px] uppercase tracking-wide text-slate-500">当前结果</div>
                      <div className="text-sm text-slate-800">OpenClaw 执行器占位符已接受...</div>
                    </div>
                    <div className="rounded-2xl border border-slate-200 bg-white p-3">
                      <div className="mb-1 text-[11px] uppercase tracking-wide text-slate-500">下一步</div>
                      <div className="text-sm text-slate-800">查看 OpenClaw 执行跟踪并...</div>
                    </div>
                  </div>
                </button>
              </div>
            </div>
          </SectionCard>

          <SectionCard
            title="结果概览"
            extra={
              <div className="flex flex-wrap gap-2">
                <button className="rounded-xl border border-violet-300 bg-violet-50 px-4 py-2 text-sm font-medium text-violet-700 hover:bg-violet-100">开爪</button>
                <button className="rounded-xl border border-emerald-300 bg-emerald-50 px-4 py-2 text-sm font-medium text-emerald-700 hover:bg-emerald-100">基于当前结果继续</button>
                <button className="rounded-xl border border-blue-300 bg-blue-50 px-4 py-2 text-sm font-medium text-blue-700 hover:bg-blue-100">生成后续目标候选</button>
                <button className="rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-800 hover:bg-slate-50">刷新</button>
                <button className="rounded-xl bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800">执行</button>
              </div>
            }
          >
            <div className="mb-4 flex flex-wrap gap-2">
              <Badge tone="purple">系统构建</Badge>
              <Badge tone="success">已完成</Badge>
              <Badge tone="info">浏览器执行完成</Badge>
              <Badge tone="default">中等的</Badge>
              <Badge tone="info">推荐张开爪</Badge>
            </div>

            <div className="mb-4 rounded-2xl border border-blue-200 bg-blue-50 p-4">
              <div className="mb-2 flex flex-wrap items-center gap-2">
                <Badge tone="info">执行推荐方式</Badge>
                <Badge tone="purple">收集系统分析上下文</Badge>
              </div>
              <div className="text-sm text-slate-700">重用本次结果中最新的 OpenClaw 执行模板。</div>
              <button className="mt-3 rounded-xl border border-blue-300 bg-white px-4 py-2 text-sm font-medium text-blue-700 hover:bg-blue-100">
                应用推荐并打开OpenClaw
              </button>
            </div>

            <div className="mt-4 rounded-2xl border border-blue-200 bg-blue-50 p-4">
              <div className="mb-3 text-sm font-medium text-slate-800">后续目标候选</div>
              <div className="space-y-3">
                <div className="rounded-2xl border border-blue-100 bg-white p-3">
                  <div className="whitespace-pre-wrap text-sm text-slate-700">
                    Continue implementation for: 使用 Docker、Git 和 Python 构建 Ubuntu 22.04 开发环境
                  </div>
                  <div className="mt-3 flex flex-wrap gap-2">
                    <button className="rounded-xl border border-blue-300 bg-blue-50 px-3 py-2 text-sm font-medium text-blue-700 hover:bg-blue-100">
                      使用这个候选
                    </button>
                    <button className="rounded-xl border border-slate-300 bg-white px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50">
                      加入最近提交
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </SectionCard>
        </div>
      </div>
    </div>
  );
}
