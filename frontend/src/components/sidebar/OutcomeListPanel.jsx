import SectionCard from "../common/SectionCard";
import Badge from "../common/Badge";
import QuickFilterChip from "../common/QuickFilterChip";
import OutcomeListItem from "./OutcomeListItem";

export default function OutcomeListPanel({
  cards,
  quickFilter,
  setQuickFilter,
  searchText,
  setSearchText,
  statusFilter,
  setStatusFilter,
  goalTypeFilter,
  setGoalTypeFilter,
  sortOrder,
  setSortOrder,
  activeCardId,
  setActiveCardId,
  loading = false,
}) {
  return (
    <SectionCard
      title="结果清单"
      extra={<Badge tone="default">{loading ? "加载中..." : `${cards.length} 条`}</Badge>}
    >
      <div className="space-y-3">
        <div className="sticky top-0 z-10 -mx-1 rounded-2xl bg-white px-1 pb-3">
          <div className="flex flex-wrap gap-2">
            <QuickFilterChip active={quickFilter === "all"} onClick={() => setQuickFilter("all")}>全部</QuickFilterChip>
            <QuickFilterChip active={quickFilter === "requirement"} onClick={() => setQuickFilter("requirement")}>需求</QuickFilterChip>
            <QuickFilterChip active={quickFilter === "clarification"} onClick={() => setQuickFilter("clarification")}>澄清</QuickFilterChip>
            <QuickFilterChip active={quickFilter === "execution"} onClick={() => setQuickFilter("execution")}>执行</QuickFilterChip>
            <QuickFilterChip active={quickFilter === "testing"} onClick={() => setQuickFilter("testing")}>测试</QuickFilterChip>
            <QuickFilterChip active={quickFilter === "delivery"} onClick={() => setQuickFilter("delivery")}>交付</QuickFilterChip>
          </div>

          <input
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            placeholder="搜索标题/阶段/结果/下一步"
            className="mt-3 h-11 w-full rounded-2xl border border-slate-300 px-4 text-sm outline-none transition focus:border-slate-500"
          />

          <div className="mt-3 grid gap-3">
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="h-11 rounded-2xl border border-slate-300 bg-white px-3 text-sm outline-none"
            >
              <option value="all">所有状态</option>
              <option value="completed">已完成</option>
              <option value="running">执行中</option>
              <option value="failed">失败</option>
              <option value="draft">草稿</option>
            </select>

            <select
              value={goalTypeFilter}
              onChange={(e) => setGoalTypeFilter(e.target.value)}
              className="h-11 rounded-2xl border border-slate-300 bg-white px-3 text-sm outline-none"
            >
              <option value="all">所有目标类型</option>
              <option value="system_build">系统构建</option>
              <option value="system_understanding">系统理解</option>
              <option value="general_task">通用任务</option>
            </select>

            <select
              value={sortOrder}
              onChange={(e) => setSortOrder(e.target.value)}
              className="h-11 rounded-2xl border border-slate-300 bg-white px-3 text-sm outline-none"
            >
              <option value="updated_desc">按最新结果排序</option>
              <option value="updated_asc">按最早结果排序</option>
              <option value="title_asc">按标题 A-Z</option>
              <option value="title_desc">按标题 Z-A</option>
            </select>
          </div>
        </div>

        <div className="space-y-3">
          {cards.map((item) => (
            <OutcomeListItem
              key={item.goal_id}
              item={item}
              active={item.goal_id === activeCardId}
              onClick={() => setActiveCardId(item.goal_id)}
            />
          ))}
        </div>
      </div>
    </SectionCard>
  );
}
